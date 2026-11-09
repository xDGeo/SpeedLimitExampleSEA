"""FeatureBuilder: the only definition of model inputs, shared by training and live use."""
import math

import pandas as pd

from core import router

FEATURES = (
    "speed_limit", "log_lux", "water_um", "temperature_c", "wind_strength",
    "humidity_pct", "traffic_cars_s", "is_dark", "is_black_ice",
)


def _row(speed_limit, lux, water_um, temperature_c, wind_strength, humidity_pct, traffic_cars_s) -> dict:
    route = router.route(router.lux_to_millilux(lux), water_um, temperature_c)
    return {
        "speed_limit": float(speed_limit),
        "log_lux": math.log1p(lux),
        "water_um": float(water_um),
        "temperature_c": float(temperature_c),
        "wind_strength": float(wind_strength),
        "humidity_pct": float(humidity_pct),
        "traffic_cars_s": float(traffic_cars_s),
        "is_dark": float(route.dark),
        "is_black_ice": float(route.black_ice),
    }


def training_matrix(table: pd.DataFrame) -> pd.DataFrame:
    rows = [
        _row(r.speed_limit, r.lux, r.water_um, r.temperature_c, r.wind_strength, r.humidity_pct, r.traffic_cars_s)
        for r in table.itertuples()
    ]
    return pd.DataFrame(rows, columns=FEATURES, index=table.index)


def live_matrix(readings: dict, limits) -> pd.DataFrame:
    rows = [
        _row(limit, readings["illuminance_lux"], readings["water_um"], readings["temperature_c"],
             readings["wind_strength_kmh"], readings["humidity_pct"], readings["traffic_cars_s"])
        for limit in limits
    ]
    return pd.DataFrame(rows, columns=FEATURES)


def dark_or_ice_mask(table: pd.DataFrame) -> pd.Series:
    flags = [
        router.route(router.lux_to_millilux(r.lux), r.water_um, r.temperature_c).use_nn
        for r in table.itertuples()
    ]
    return pd.Series(flags, index=table.index)
