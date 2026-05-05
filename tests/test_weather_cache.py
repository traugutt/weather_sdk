"""Unit tests for WeatherCache."""

from datetime import datetime

import pytest

from weather_sdk.exceptions import StorageKeyError
from weather_sdk.models import (
    AirQuality,
    Coordinates,
    CurrentWeather,
    GeoLocation,
    WeatherCondition,
)
from weather_sdk.service.weather_cache import WeatherCache

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
def cache() -> WeatherCache:
    return WeatherCache()


def test_put_and_get_location(cache: WeatherCache) -> None:
    cache.put_location("London", _GEO)
    assert cache.get_location("London") is _GEO


def test_put_and_get_weather(cache: WeatherCache) -> None:
    cache.put_current_weather("London", _WEATHER)
    assert cache.get_current_weather("london") is _WEATHER


def test_put_and_get_air_quality(cache: WeatherCache) -> None:
    cache.put_air_quality("London", _AQI)
    assert cache.get_air_quality("London") is _AQI


def test_put_overwrites_existing(cache: WeatherCache) -> None:
    cache.put_current_weather("London", _WEATHER)
    cache.put_current_weather("London", _WEATHER)
    assert cache.get_current_weather("London") is _WEATHER


def test_key_is_case_insensitive(cache: WeatherCache) -> None:
    cache.put_location("London", _GEO)
    assert cache.get_location("LONDON") is _GEO


def test_get_missing_raises(cache: WeatherCache) -> None:
    with pytest.raises(StorageKeyError):
        cache.get_current_weather("Paris")


def test_list_cities_covers_all_repos(cache: WeatherCache) -> None:
    cache.put_location("London", _GEO)
    cache.put_air_quality("Paris", _AQI)
    cities = cache.list_cities()
    assert "london" in cities
    assert "paris" in cities


def test_evict_removes_all_records(cache: WeatherCache) -> None:
    cache.put_location("London", _GEO)
    cache.put_current_weather("London", _WEATHER)
    cache.evict("London")
    with pytest.raises(StorageKeyError):
        cache.get_current_weather("London")
    with pytest.raises(StorageKeyError):
        cache.get_location("London")


def test_evict_missing_city_is_noop(cache: WeatherCache) -> None:
    cache.evict("Nowhere")
