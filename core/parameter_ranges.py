"""InputGuardrail and the Normal / Abnormal classification, with units."""
import json
import math
from dataclasses import dataclass

import pandas as pd

from core import config

RULE_TYPE = "Rule: changes the limit"
BAND_TYPE = "Data band: informational only"
READING_KEYS = ("illuminance_lux", "water_um", "temperature_c",
                "wind_strength_kmh", "humidity_pct", "traffic_cars_s")
DARK_LUX = config.DARK_BELOW_MILLILUX / 1000.0


class InvalidReading(ValueError):
    pass


@dataclass(frozen=True)
class Param:
    key: str
    label: str
    unit: str
    minimum: float
    maximum: float
    kind: str
    normal: str
    abnormal: str
    basis: str


@dataclass(frozen=True)
class Status:
    status: str
    reason: str


def _rule(key, label, unit, low, high, normal, abnormal, basis):
    return Param(key, label, unit, low, high, RULE_TYPE, normal, abnormal, basis)


def _band(key, label, unit, low, high):
    return Param(key, label, unit, low, high, BAND_TYPE, "", "", "Data only (January); does not change the limit")


PARAMETERS = {param.key: param for param in (
    _rule("illuminance_lux", "Illuminance", "lux", *config.RANGES["light"],
          f"at least {DARK_LUX} lux", f"below {DARK_LUX} lux (dark)", "SPEC1 (500 millilux)"),
    _rule("water_um", "Water on road", "µm", *config.RANGES["water"],
          "at most 1000 µm, or any amount at 0 °C or warmer",
          "above 1000 µm while below 0 °C (black ice)", "SPEC2"),
    _rule("temperature_c", "Temperature", "°C", *config.RANGES["temperature"],
          "0 °C or warmer, or colder with at most 1000 µm of water",
          "below 0 °C with more than 1000 µm of water (black ice)", "SPEC2"),
    _band("wind_strength_kmh", "Wind strength", "km/h", *config.RANGES["wind_strength"]),
    _band("humidity_pct", "Humidity", "%", *config.RANGES["humidity"]),
    _band("traffic_cars_s", "Traffic", "cars/s", *config.RANGES["traffic"]),
    _rule("pm10", "PM10", "µg/m³", 0.0, config.AIR_INPUT_MAX,
          f"at most {config.PM10_LIMIT:g} µg/m³", f"above {config.PM10_LIMIT:g} µg/m³",
          "EU daily limit, Directive 2008/50/EC"),
    _rule("no2", "NO₂", "µg/m³", 0.0, config.AIR_INPUT_MAX,
          f"at most {config.NO2_LIMIT:g} µg/m³", f"above {config.NO2_LIMIT:g} µg/m³",
          "EU hourly limit, Directive 2008/50/EC"),
)}


def load_bands(path=config.PARAMETER_BANDS) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            return {key: tuple(value) for key, value in json.load(handle).items()}
    except (OSError, ValueError):
        return {}


def _classify_water(value, temperature):
    freezing = temperature is None or temperature < config.ICE_TEMPERATURE_BELOW_C
    if value > config.ICE_WATER_ABOVE_UM and freezing:
        return Status("Abnormal", "More than 1000 µm of water below 0 °C: black-ice danger (SPEC2)")
    return Status("Normal", "No black-ice danger from water (SPEC2)")


def _classify_temperature(value, water):
    wet = water is None or water > config.ICE_WATER_ABOVE_UM
    if value < config.ICE_TEMPERATURE_BELOW_C and wet:
        return Status("Abnormal", "Below 0 °C with more than 1000 µm of water: black-ice danger (SPEC2)")
    return Status("Normal", "No black-ice danger from temperature (SPEC2)")


def _classify_band(key, value, bands):
    if key not in bands:
        return Status("Unknown", "No typical band available. Run analyze_data.py")
    low, high = bands[key]
    unit = PARAMETERS[key].unit
    inside = low <= value <= high
    place = "Inside" if inside else "Outside"
    return Status("Normal" if inside else "Abnormal",
                  f"{place} the typical January band {low:g} to {high:g} {unit}. This does not change the limit")


def classify(key: str, value: float, context: dict = None, bands: dict = None) -> Status:
    context = context or {}
    bands = load_bands() if bands is None else bands
    if key == "illuminance_lux":
        if value < DARK_LUX:
            return Status("Abnormal", "Below 0.5 lux: dark (SPEC1)")
        return Status("Normal", "At least 0.5 lux: not dark (SPEC1)")
    if key == "water_um":
        return _classify_water(value, context.get("temperature_c"))
    if key == "temperature_c":
        return _classify_temperature(value, context.get("water_um"))
    if key == "pm10":
        limit, name = config.PM10_LIMIT, "PM10"
    elif key == "no2":
        limit, name = config.NO2_LIMIT, "NO₂"
    else:
        return _classify_band(key, value, bands)
    if value > limit:
        return Status("Abnormal", f"{name} above the EU limit of {limit:g} µg/m³")
    return Status("Normal", f"{name} within the EU limit of {limit:g} µg/m³")


def validate_readings(readings: dict) -> None:
    """Input guardrail: raises InvalidReading for missing, non-numeric or impossible values."""
    for key in READING_KEYS:
        param = PARAMETERS[key]
        if key not in readings:
            raise InvalidReading(f"{param.label} is missing")
        value = readings[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise InvalidReading(f"{param.label} must be a number, got {value!r}")
        if not param.minimum <= value <= param.maximum:
            raise InvalidReading(
                f"{param.label} {value:g} {param.unit} is outside the allowed range "
                f"{param.minimum:g} to {param.maximum:g} {param.unit}")


def format_value(key: str, value: float) -> str:
    return f"{value:.1f} {PARAMETERS[key].unit}"


def ranges_table(bands: dict) -> pd.DataFrame:
    rows = []
    for param in PARAMETERS.values():
        normal, abnormal = param.normal, param.abnormal
        if param.kind == BAND_TYPE:
            low, high = bands.get(param.key, (None, None))
            if low is None:
                normal = abnormal = "No band available"
            else:
                normal = f"{low:g} to {high:g} {param.unit}"
                abnormal = f"below {low:g} or above {high:g} {param.unit}"
        rows.append({
            "Parameter": param.label, "Unit": param.unit,
            "Allowed range": f"{param.minimum:g} to {param.maximum:g} {param.unit}",
            "Normal": normal, "Abnormal": abnormal, "Basis": param.basis, "Type": param.kind,
        })
    return pd.DataFrame(rows)
