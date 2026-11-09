"""DataLoader and DataCleaner: raw CSV files to one clean row per hour."""
from dataclasses import dataclass

import pandas as pd

from core import config

RAW_COLUMNS = ["Month", "Day", "Hour", "Minute", "Second", "Sensor", "Value"]
ACCIDENT_COLUMNS = ["Month", "Day", "Hour", "Second", "Damage", "Injured",
                    "CloseCarCm", "CloseGuardrailCm", "SkidAngle"]


@dataclass
class CleanResult:
    table: pd.DataFrame
    wide: pd.DataFrame
    report: dict


def load_readings(path) -> pd.DataFrame:
    """Read a readings file as raw text. The header is optional: Year N+1 has none."""
    with open(path, encoding="utf-8-sig") as handle:
        has_header = handle.readline().strip().startswith("Month")
    return pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False,
                       header=None, names=RAW_COLUMNS, skiprows=1 if has_header else 0)


def load_sensor_types(path=config.SENSOR_TYPES) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str)
    frame.columns = ["code", "type", "unit", "min", "max"]
    for column in ("code", "type", "unit"):
        frame[column] = frame[column].str.strip()
    frame[["min", "max"]] = frame[["min", "max"]].astype(float)
    return frame


def load_sensors(path=config.SENSORS) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str)
    frame.columns = ["sensor", "code"]
    frame["sensor"] = frame["sensor"].astype(int)
    frame["code"] = frame["code"].str.strip()
    return frame


def load_accidents(path) -> pd.DataFrame:
    """Licence plates are personal data and never leave this function."""
    frame = pd.read_csv(path, sep=";", encoding="utf-8-sig", usecols=ACCIDENT_COLUMNS)
    return frame.apply(pd.to_numeric, errors="coerce")


def _repair_months(month: pd.Series) -> tuple[pd.Series, int]:
    numeric = pd.to_numeric(month, errors="coerce")
    bad = numeric.isna()
    fill = int(numeric.mode().iloc[0]) if numeric.notna().any() else 1
    return numeric.fillna(fill), int(bad.sum())


def clean_readings(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Repair the raw rows. Returns long-format readings and a count of every repair."""
    frame = raw.copy()
    report = {"rows_read": len(frame)}
    frame["Month"], report["months_repaired"] = _repair_months(frame["Month"])

    exact_duplicates = frame.duplicated(RAW_COLUMNS)
    frame = frame[~exact_duplicates]

    for column in ("Day", "Hour"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    valid_time = frame["Day"].between(1, config.SENSOR_DAYS) & frame["Hour"].between(0, 23)
    report["rows_bad_time"] = int((~valid_time).sum())
    frame = frame[valid_time]

    sensors = pd.to_numeric(frame["Sensor"], errors="coerce")
    report["rows_without_sensor"] = int(sensors.isna().sum())
    frame = frame[sensors.notna()].assign(Sensor=sensors[sensors.notna()].astype(int))

    known = frame["Sensor"].isin(config.SENSOR_KIND)
    report["unknown_sensor_rows"] = int((~known).sum())
    frame = frame[known]

    values = pd.to_numeric(frame["Value"].str.replace(",", ".", regex=False), errors="coerce")
    report["empty_values"] = int(values.isna().sum())
    frame = frame.assign(value=values)[values.notna()]

    frame, report["out_of_range"] = _drop_out_of_range(frame)

    same_key = frame.duplicated(["Day", "Hour", "Sensor"])
    report["duplicates_removed"] = int(exact_duplicates.sum() + same_key.sum())
    frame = frame[~same_key]

    long = frame[["Day", "Hour", "Sensor", "value"]].astype(
        {"Day": int, "Hour": int, "Sensor": int}
    ).reset_index(drop=True)
    return long, report


def _drop_out_of_range(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    kinds = frame["Sensor"].map(config.SENSOR_KIND)
    lows = kinds.map(lambda kind: config.RANGES[kind][0])
    highs = kinds.map(lambda kind: config.RANGES[kind][1])
    in_range = (frame["value"] >= lows) & (frame["value"] <= highs)
    is_limit = frame["Sensor"] == config.SPEED_LIMIT_SENSOR
    in_range &= ~is_limit | frame["value"].isin(config.ALLOWED_LIMITS)
    return frame[in_range], int((~in_range).sum())


def hourly_table(long: pd.DataFrame, days: int = config.SENSOR_DAYS):
    """Combine redundant sensors by median and return a complete grid of hours."""
    grid = pd.MultiIndex.from_product([range(1, days + 1), range(24)], names=["Day", "Hour"])
    wide = long.pivot_table(index=["Day", "Hour"], columns="Sensor", values="value", aggfunc="first")
    wide = wide.reindex(grid)
    wide.columns.name = None

    report = {"hours_filled": int(wide.isna().all(axis=1).sum())}
    combined = pd.DataFrame(index=grid)
    for column, sensors in config.SENSOR_GROUPS.items():
        present = [sensor for sensor in sensors if sensor in wide.columns]
        combined[column] = wide[present].median(axis=1) if present else float("nan")

    missing_before = int(combined.isna().sum().sum())
    combined = combined.interpolate(limit=config.MAX_GAP_HOURS, limit_direction="both")
    report["cells_interpolated"] = missing_before - int(combined.isna().sum().sum())

    limit = config.SPEED_LIMIT_SENSOR
    speed = wide[limit] if limit in wide.columns else pd.Series(index=grid, dtype=float)
    combined.insert(0, "speed_limit", speed.ffill().bfill())

    table = combined.reset_index().rename(columns={"Day": "day", "Hour": "hour"})
    return table, wide, report


def build_hourly(path) -> CleanResult:
    long, report = clean_readings(load_readings(path))
    table, wide, grid_report = hourly_table(long)
    found = set(long["Sensor"]) - {config.SPEED_LIMIT_SENSOR}
    documented = set(load_sensors()["sensor"])
    report.update(grid_report)
    report["sensors_without_readings"] = sorted(documented - found)
    report["undocumented_sensors"] = sorted(found - documented)
    return CleanResult(table, wide, report)
