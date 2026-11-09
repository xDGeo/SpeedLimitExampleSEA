"""AirQualityClient: the worst forecast PM10 and NO₂ of the coming hours, in µg/m³."""
import http.client
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass

from core import config


class AirQualityUnavailable(Exception):
    pass


@dataclass(frozen=True)
class AirQuality:
    pm10: float
    no2: float
    source: str


def manual_reading(pm10: float, no2: float) -> AirQuality:
    return AirQuality(float(pm10), float(no2), "Manual override")


def _http_get_json(url: str, timeout: float = config.HTTP_TIMEOUT_S) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.load(response)


def _worst(values) -> float:
    numbers = [float(value) for value in values or [] if value is not None]
    if not numbers:
        raise AirQualityUnavailable("The forecast contains no values")
    return max(numbers)


class OpenMeteoClient:
    def __init__(self, url=config.OPEN_METEO_URL, latitude=config.LATITUDE, longitude=config.LONGITUDE,
                 hours=config.FORECAST_HOURS, fetch=None):
        self.url, self.latitude, self.longitude, self.hours = url, latitude, longitude, hours
        self.fetch = fetch or _http_get_json

    def get_forecast(self) -> AirQuality:
        query = urllib.parse.urlencode({
            "latitude": self.latitude, "longitude": self.longitude,
            "hourly": "pm10,nitrogen_dioxide", "forecast_hours": self.hours,
        })
        try:
            hourly = self.fetch(f"{self.url}?{query}").get("hourly") or {}
            return AirQuality(_worst(hourly.get("pm10")), _worst(hourly.get("nitrogen_dioxide")),
                              "Open-Meteo forecast")
        except (OSError, ValueError, TypeError, http.client.HTTPException) as error:
            raise AirQualityUnavailable(str(error)) from error
