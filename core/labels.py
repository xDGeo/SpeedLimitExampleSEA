"""NearAccidentLabeler: counts near-accidents per hour (SPEC4)."""
import pandas as pd

from core import config


def _has_any(frame: pd.DataFrame, columns) -> pd.Series:
    return frame[list(columns)].notna().any(axis=1)


def count_near_accidents(accidents: pd.DataFrame, kinds=config.NEAR_ACCIDENT_KINDS,
                         days: int = config.SENSOR_DAYS) -> pd.Series:
    """Count per (day, hour). Accident hours run 1 to 24, sensor hours 0 to 23."""
    near = accidents[_has_any(accidents, kinds) & accidents["Hour"].between(1, 24)]
    counts = near.assign(hour=near["Hour"].astype(int) - 1, day=near["Day"].astype(int)) \
        .groupby(["day", "hour"]).size()
    grid = pd.MultiIndex.from_product([range(1, days + 1), range(24)], names=["day", "hour"])
    return counts.reindex(grid, fill_value=0)


def label_report(accidents: pd.DataFrame) -> dict:
    near = _has_any(accidents, config.NEAR_ACCIDENT_KINDS)
    real = _has_any(accidents, config.REAL_ACCIDENT_KINDS)
    return {
        "rows": len(accidents),
        "near_accidents": int(near.sum()),
        "accidents": int((real & ~near).sum()),
        "empty_rows": int((~near & ~real).sum()),
    }


def attach_labels(table: pd.DataFrame, accidents: pd.DataFrame, kinds=config.NEAR_ACCIDENT_KINDS) -> pd.DataFrame:
    counts = count_near_accidents(accidents, kinds).rename("near_accidents").reset_index()
    return table.drop(columns="near_accidents", errors="ignore").merge(counts, on=["day", "hour"], how="left")
