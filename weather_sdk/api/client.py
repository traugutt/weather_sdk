"""OpenWeatherMap API clients organised by service area."""

from typing import Any, Self

import httpx

from weather_sdk.exceptions import APIError
from weather_sdk.models import (
    AirQuality,
    Coordinates,
    CurrentWeather,
    GeoLocation,
    WeatherCondition,
)

_BASE = "https://api.openweathermap.org"
_GEO_BASE = f"{_BASE}/geo/1.0"


def _parse_geo(geo_dict: dict[str, Any]) -> GeoLocation:
    return GeoLocation(
        name=geo_dict["name"],
        country=geo_dict.get("country", ""),
        state=geo_dict.get("state", ""),
        coordinates=Coordinates(
            lat=float(geo_dict["lat"]),
            lon=float(geo_dict["lon"]),
        ),
    )


def _parse_weather(weather_dict: dict[str, Any]) -> CurrentWeather:
    conditions = tuple(
        WeatherCondition(main=cond["main"], description=cond["description"])
        for cond in weather_dict.get("weather", [])
    )
    main = weather_dict["main"]
    return CurrentWeather(
        city=weather_dict["name"],
        country=weather_dict["sys"]["country"],
        coordinates=Coordinates(
            lat=weather_dict["coord"]["lat"],
            lon=weather_dict["coord"]["lon"],
        ),
        conditions=conditions,
        temp_celsius=float(main["temp"]),
        feels_like_celsius=float(main["feels_like"]),
        humidity_percent=int(main["humidity"]),
        wind_speed_ms=float(weather_dict["wind"]["speed"]),
    )


def _parse_air(air_dict: dict[str, Any]) -> AirQuality:
    record = air_dict["list"][0]
    comp = record["components"]
    coord = air_dict["coord"]
    return AirQuality(
        coordinates=Coordinates(
            lat=float(coord["lat"]),
            lon=float(coord["lon"]),
        ),
        aqi=int(record["main"]["aqi"]),
        co=float(comp.get("co", 0)),
        no2=float(comp.get("no2", 0)),
        o3=float(comp.get("o3", 0)),
        pm2_5=float(comp.get("pm2_5", 0)),
        pm10=float(comp.get("pm10", 0)),
    )


class _HTTPSession:
    """Shared HTTP connection and auth — injected into each sub-client."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._http = httpx.Client(timeout=10)

    def fetch(self, url: str, url_params: dict[str, Any]) -> Any:
        full_params = {**url_params, "appid": self._api_key}
        response = self._http.get(url, params=full_params)
        if response.status_code != 200:
            raise APIError(response.status_code, response.text)
        return response.json()

    def close(self) -> None:
        self._http.close()


class GeoClient:
    """Forward geocoding via the OWM Geocoding API."""

    def __init__(self, http: _HTTPSession) -> None:
        self._http = http

    def geocode(self, city: str, limit: int = 1) -> GeoLocation:
        """Return the first geocoding result for *city*."""
        raw = self._http.fetch(
            f"{_GEO_BASE}/direct",
            url_params={"q": city, "limit": limit},
        )
        if not raw:
            raise APIError(404, f"City not found: {city}")
        return _parse_geo(raw[0])


class WeatherClient:
    """Current weather via the OWM Current Weather API."""

    def __init__(self, http: _HTTPSession) -> None:
        self._http = http

    def current(self, coordinates: Coordinates) -> CurrentWeather:
        raw = self._http.fetch(
            f"{_BASE}/data/2.5/weather",
            url_params={
                "lat": coordinates.lat,
                "lon": coordinates.lon,
                "units": "metric",
            },
        )
        return _parse_weather(raw)


class AirClient:
    """Air quality via the OWM Air Pollution API."""

    def __init__(self, http: _HTTPSession) -> None:
        self._http = http

    def quality(self, coordinates: Coordinates) -> AirQuality:
        raw = self._http.fetch(
            f"{_BASE}/data/2.5/air_pollution",
            url_params={"lat": coordinates.lat, "lon": coordinates.lon},
        )
        return _parse_air(raw)


class OWMClient:
    """Entry point for the OpenWeatherMap SDK.

    Composes focused sub-clients, one per OWM service area, sharing a
    single HTTP session. Adding a new service area means adding a new
    sub-client class — this class stays unchanged.

    Usage::

        with OWMClient(api_key="...") as client:
            geo     = client.geo.geocode("London")
            weather = client.weather.current(geo.coordinates)
            aqi     = client.air.quality(geo.coordinates)
    """

    def __init__(self, api_key: str) -> None:
        self._session = _HTTPSession(api_key)
        self.geo = GeoClient(self._session)
        self.weather = WeatherClient(self._session)
        self.air = AirClient(self._session)

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
