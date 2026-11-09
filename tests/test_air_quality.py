import pytest

from core import air_quality as aq


def client(payload):
    return aq.OpenMeteoClient(fetch=lambda url: payload)


def test_parses_worst_values():
    result = client({"hourly": {"pm10": [10, 40, 20], "nitrogen_dioxide": [5, 3, 90]}}).get_forecast()
    assert (result.pm10, result.no2) == (40, 90)
    assert result.source == "Open-Meteo forecast"


def test_ignores_null_values():
    result = client({"hourly": {"pm10": [None, 12], "nitrogen_dioxide": [None, 7]}}).get_forecast()
    assert (result.pm10, result.no2) == (12, 7)


def test_all_null_is_unavailable():
    with pytest.raises(aq.AirQualityUnavailable):
        client({"hourly": {"pm10": [None], "nitrogen_dioxide": [None]}}).get_forecast()


def test_missing_block_is_unavailable():
    with pytest.raises(aq.AirQualityUnavailable):
        client({}).get_forecast()


def test_network_error_is_unavailable():
    def boom(url):
        raise OSError("timeout")
    with pytest.raises(aq.AirQualityUnavailable):
        aq.OpenMeteoClient(fetch=boom).get_forecast()


def test_text_numbers_are_parsed():
    result = client({"hourly": {"pm10": ["12.5"], "nitrogen_dioxide": ["7"]}}).get_forecast()
    assert result.pm10 == 12.5


def test_url_contains_location_and_pollutants():
    seen = []
    def fetch(url):
        seen.append(url)
        return {"hourly": {"pm10": [1], "nitrogen_dioxide": [1]}}
    aq.OpenMeteoClient(latitude=48.2, longitude=16.37, fetch=fetch).get_forecast()
    assert "latitude=48.2" in seen[0] and "pm10" in seen[0] and "nitrogen_dioxide" in seen[0]


def test_manual_reading():
    assert aq.manual_reading(60, 210).source == "Manual override"
