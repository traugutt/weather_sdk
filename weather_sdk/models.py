"""Shared domain models used across all layers."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Coordinates:
    """Geographic coordinates."""

    lat: float
    lon: float


@dataclass(frozen=True)
class WeatherCondition:
    """A single weather condition descriptor."""

    main: str
    description: str


@dataclass(frozen=True)
class CurrentWeather:
    """Parsed response from the *current weather* endpoint."""

    city: str
    country: str
    coordinates: Coordinates
    conditions: tuple[WeatherCondition, ...]
    temp_celsius: float
    feels_like_celsius: float
    humidity_percent: int
    wind_speed_ms: float
    fetched_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class AirQuality:
    """Parsed response from the *air quality* endpoint."""

    coordinates: Coordinates
    aqi: int  # 1=Good … 5=Very Poor
    co: float
    no2: float
    o3: float
    pm2_5: float
    pm10: float
    fetched_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class GeoLocation:
    """Parsed response from the *geocoding* endpoint."""

    name: str
    country: str
    state: str
    coordinates: Coordinates
    fetched_at: datetime = field(default_factory=_utcnow)
