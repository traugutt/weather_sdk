"""In-memory cache for weather data keyed by city name."""

from typing import TypeVar

from weather_sdk.models import AirQuality, CurrentWeather, GeoLocation
from weather_sdk.storage.repository import InMemoryRepository

_ET = TypeVar("_ET")


class WeatherCache:
    """Stores and retrieves weather data by city name.

    Keys are normalised to lowercase so "London" and "london" resolve
    to the same entry. Does not make network calls — callers are
    responsible for fetching data and passing it in.
    """

    def __init__(self) -> None:
        self._weather: InMemoryRepository[CurrentWeather] = (
            InMemoryRepository()
        )
        self._air: InMemoryRepository[AirQuality] = InMemoryRepository()
        self._geo: InMemoryRepository[GeoLocation] = InMemoryRepository()

    def put_location(self, city: str, geo: GeoLocation) -> None:
        self._store(self._geo, city.lower(), geo)

    def put_current_weather(
        self, city: str, weather: CurrentWeather,
    ) -> None:
        self._store(self._weather, city.lower(), weather)

    def put_air_quality(self, city: str, aqi: AirQuality) -> None:
        self._store(self._air, city.lower(), aqi)

    def get_location(self, city: str) -> GeoLocation:
        return self._geo.read(city.lower())

    def get_current_weather(self, city: str) -> CurrentWeather:
        return self._weather.read(city.lower())

    def get_air_quality(self, city: str) -> AirQuality:
        return self._air.read(city.lower())

    def list_cities(self) -> list[str]:
        all_keys = (
            set(self._weather.list_keys())
            | set(self._air.list_keys())
            | set(self._geo.list_keys())
        )
        return sorted(all_keys)

    def evict(self, city: str) -> None:
        """Remove all cached records for *city*."""
        key = city.lower()
        for repo in (self._weather, self._air, self._geo):
            if key in repo:
                repo.delete(key)

    def _store(
        self, repo: InMemoryRepository[_ET], key: str, entry: _ET,
    ) -> None:
        if key in repo:
            repo.update(key, entry)
        else:
            repo.create(key, entry)
