"""Shared test data. Deliberately independent of core/ so tests can fail on their own."""
import pandas as pd

RAW_COLUMNS = ["Month", "Day", "Hour", "Minute", "Second", "Sensor", "Value"]
SENSOR_VALUES = {
    1: "0,00", 8: "0,00", 11: "0,00",
    2: "5000,00", 9: "5000,00", 12: "5000,00",
    3: "90,00", 4: "80,00",
    5: "100,00", 13: "100,00",
    6: "10,00", 14: "10,00",
    15: "-5,00", 18: "-5,00", 19: "-5,00",
    16: "15,00", -1: "70,00",
}


def raw_rows(days=31):
    rows = [
        ["1", str(day), str(hour), "10", "5", str(sensor), value]
        for day in range(1, days + 1)
        for hour in range(24)
        for sensor, value in SENSOR_VALUES.items()
    ]
    return pd.DataFrame(rows, columns=RAW_COLUMNS, dtype=str)


def write_readings(path, rows, header=True, bom=True):
    lines = [";".join(RAW_COLUMNS)] if header else []
    lines += [";".join(row) for row in rows[RAW_COLUMNS].astype(str).values.tolist()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig" if bom else "utf-8")
    return path


def hourly_table(days=31, limit=60.0, lux=0.1, near=1):
    rows = [
        {
            "day": day, "hour": hour, "speed_limit": limit, "lux": lux, "water_um": 10.0,
            "temperature_c": -5.0, "wind_strength": 10.0, "humidity_pct": 80.0,
            "traffic_cars_s": 15.0, "near_accidents": near,
        }
        for day in range(1, days + 1)
        for hour in range(24)
    ]
    return pd.DataFrame(rows)


def accidents(rows):
    """rows: dicts with Day and Hour plus any measurement columns."""
    columns = ["Month", "Day", "Hour", "Second", "Damage", "Injured",
               "CloseCarCm", "CloseGuardrailCm", "SkidAngle"]
    frame = pd.DataFrame(rows).reindex(columns=columns)
    frame["Month"] = 1
    frame["Second"] = 0
    return frame


DAY_READINGS = {
    "illuminance_lux": 50000.0, "water_um": 0.0, "temperature_c": 10.0,
    "wind_strength_kmh": 10.0, "humidity_pct": 60.0, "traffic_cars_s": 15.0,
}
NIGHT_READINGS = {**DAY_READINGS, "illuminance_lux": 0.1}
