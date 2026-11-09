"""Router: applies SPEC1 and SPEC2. Plain rules, fully testable at the boundaries."""
from dataclasses import dataclass

from core import config


@dataclass(frozen=True)
class RouteDecision:
    dark: bool
    black_ice: bool

    @property
    def use_nn(self) -> bool:
        return self.dark or self.black_ice


def lux_to_millilux(lux: float) -> float:
    return lux * 1000.0


def is_dark(illuminance_mlx: float) -> bool:
    return bool(illuminance_mlx < config.DARK_BELOW_MILLILUX)


def is_black_ice(water_um: float, temperature_c: float) -> bool:
    return bool(water_um > config.ICE_WATER_ABOVE_UM and temperature_c < config.ICE_TEMPERATURE_BELOW_C)


def route(illuminance_mlx: float, water_um: float, temperature_c: float) -> RouteDecision:
    return RouteDecision(is_dark(illuminance_mlx), is_black_ice(water_um, temperature_c))
