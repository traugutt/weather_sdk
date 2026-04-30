"""High-level service that fetches weather data and stores results."""

from typing import Self

from weather_sdk.api.client import WeatherAPIClient
from weather_sdk.models import AirQuality, CurrentWeather, GeoLocation
from weather_sdk.storage.repository import InMemoryRepository


class _Closable:
    """Mixin that adds context-manager support to any closable resource."""

    def close(self) -> None:
        """Release underlying resources."""

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class WeatherService(_Closable):
    """Façade that composes :class:`WeatherAPIClient` and three repositories.

    Each ``fetch_*`` method calls the upstream API and persists the result
    under the lower-cased city name so callers can retrieve it later without
    making a second network request.

    Example::

        with WeatherService(api_key="...") as svc:
            weather = svc.fetch_current_weather("London")
            aqi     = svc.fetch_air_quality("London")
            geo     = svc.fetch_location("London")
            weather = svc.get_current_weather("London")  # from cache
    """

    def __init__(self, api_key: str) -> None:
        self._client = WeatherAPIClient(api_key)
        self._weather_repo: InMemoryRepository[CurrentWeather] = (
            InMemoryRepository()
        )
        self._air_repo: InMemoryRepository[AirQuality] = (
            InMemoryRepository()
        )
        self._geo_repo: InMemoryRepository[GeoLocation] = (
            InMemoryRepository()
        )

    # ------------------------------------------------------------------
    # Fetch-and-store operations
    # ------------------------------------------------------------------

    def fetch_location(self, city: str) -> GeoLocation:
        """Geocode *city* and persist the result."""
        geo = self._client.geocode(city)
        self._geo_repo.upsert(city.lower(), geo)
        return geo

    def fetch_current_weather(self, city: str) -> CurrentWeather:
        """Fetch current weather for *city* and persist the result."""
        key = city.lower()
        if key not in self._geo_repo:
            self.fetch_location(city)
        geo = self._geo_repo.read(key)
        weather = self._client.current_weather(geo.coordinates)
        self._weather_repo.upsert(key, weather)
        return weather

    def fetch_air_quality(self, city: str) -> AirQuality:
        """Fetch air quality for *city* and persist the result."""
        key = city.lower()
        if key not in self._geo_repo:
            self.fetch_location(city)
        geo = self._geo_repo.read(key)
        aqi = self._client.air_quality(geo.coordinates)
        self._air_repo.upsert(key, aqi)
        return aqi

    # ------------------------------------------------------------------
    # Read-only storage access (no network call)
    # ------------------------------------------------------------------

    def get_current_weather(self, city: str) -> CurrentWeather:
        """Return the cached weather for *city* (no network call)."""
        return self._weather_repo.read(city.lower())

    def get_air_quality(self, city: str) -> AirQuality:
        """Return the cached air quality for *city* (no network call)."""
        return self._air_repo.read(city.lower())

    def get_location(self, city: str) -> GeoLocation:
        """Return the cached geo location for *city* (no network call)."""
        return self._geo_repo.read(city.lower())

    def list_cached_cities(self) -> list[str]:
        """Return cities that have at least one cached weather record."""
        return self._weather_repo.list_keys()

    def evict(self, city: str) -> None:
        """Remove all cached records for *city* (best-effort)."""
        key = city.lower()
        for repo in (self._weather_repo, self._air_repo, self._geo_repo):
            if key in repo:
                repo.delete(key)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()
