"""Unit tests for WeatherService (API calls are mocked)."""

yfrom datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from weather_sdk.exceptions import StorageKeyError
from weather_sdk.models import (
    AirQuality,
    Coordinates,
    CurrentWeather,
    GeoLocation,
    WeatherCondition,
)
from weather_sdk.service.weather_service import WeatherService

_COORDS = Coordinates(lat=51.5, lon=-0.12)

_GEO = GeoLocation(
    name="London",
    country="GB",
    state="England",
    coordinates=_COORDS,
    fetched_at=datetime(2024, 1, 1),
)

_WEATHER = CurrentWeather(
    city="London",
    country="GB",
    coordinates=_COORDS,
    conditions=(WeatherCondition(main="Clouds", description="overcast"),),
    temp_celsius=10.0,
    feels_like_celsius=8.5,
    humidity_percent=80,
    wind_speed_ms=5.0,
    fetched_at=datetime(2024, 1, 1),
)

_AQI = AirQuality(
    coordinates=_COORDS,
    aqi=2,
    co=200.0,
    no2=10.0,
    o3=50.0,
    pm2_5=5.0,
    pm10=8.0,
    fetched_at=datetime(2024, 1, 1),
)


@pytest.fixture()
def mock_client() -> MagicMock:
    client = MagicMock()
    client.geocode.return_value = _GEO
    client.current_weather.return_value = _WEATHER
    client.air_quality.return_value = _AQI
    return client


@pytest.fixture()
def service(mock_client: MagicMock) -> WeatherService:
    svc = WeatherService(api_key="test-key")
    with patch.object(svc, "_client", mock_client):  # noqa: WPS437
        yield svc


def test_fetch_location_stores_result(service: WeatherService) -> None:
    geo = service.fetch_location("London")
    assert geo.name == "London"
    assert service.get_location("London") is geo


def test_fetch_weather_resolves_geo(service: WeatherService) -> None:
    weather = service.fetch_current_weather("London")
    assert weather.city == "London"
    assert service.get_current_weather("london") is weather


def test_fetch_weather_reuses_cached_geo(
    service: WeatherService,
    mock_client: MagicMock,
) -> None:
    service.fetch_location("London")
    service.fetch_current_weather("London")
    assert mock_client.geocode.call_count == 1


def test_fetch_air_quality(service: WeatherService) -> None:
    aqi = service.fetch_air_quality("London")
    assert aqi.aqi == 2
    assert service.get_air_quality("London") is aqi


def test_get_missing_raises(service: WeatherService) -> None:
    with pytest.raises(StorageKeyError):
        service.get_current_weather("Paris")


def test_evict_removes_all(service: WeatherService) -> None:
    service.fetch_location("London")
    service.fetch_current_weather("London")
    service.evict("London")
    with pytest.raises(StorageKeyError):
        service.get_current_weather("London")


def test_list_cached_cities(service: WeatherService) -> None:
    service.fetch_current_weather("London")
    assert "london" in service.list_cached_cities()
