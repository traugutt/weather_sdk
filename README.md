# Weather SDK

A Python SDK for the [OpenWeatherMap API](https://openweathermap.org/api) with three endpoints and in-memory CRUD storage.

## Architecture

```
weather_sdk/
├── api/
│   └── client.py         # OWMClient + one sub-client per service area
├── storage/
│   └── repository.py     # Generic InMemoryRepository[T]
├── service/
│   └── weather_cache.py  # WeatherCache — stores and reads data by city
├── models.py             # Frozen dataclasses (domain types)
└── exceptions.py         # Custom exception hierarchy
```

| Layer | Responsibility |
|-------|---------------|
| **API** | HTTP calls, JSON → dataclass parsing, error mapping |
| **Storage** | Generic CRUD over an in-memory `dict` |
| **Cache** | Typed store for weather data; key normalisation; eviction |

## Client design

`OWMClient` composes three focused sub-clients — `GeoClient`, `WeatherClient`,
`AirClient` — each responsible for one OWM service area and sharing a single
`_HTTPSession` for connection pooling and auth.

This was chosen over a flat single-class client because each new OWM service
area maps cleanly to a new sub-client class with no changes to existing code.
The alternatives considered were a method registry (loses static type safety)
and mixins (inheritance for sharing rather than IS-A, same problem as the
`_Closable` mixin removed in the previous iteration).

## Covered Endpoints

| Sub-client | Method | OWM endpoint | Description |
|-----------|--------|-------------|-------------|
| `client.geo` | `geocode` | `GET /geo/1.0/direct` | Forward geocoding |
| `client.weather` | `current` | `GET /data/2.5/weather` | Current weather |
| `client.air` | `quality` | `GET /data/2.5/air_pollution` | Air quality index |

## Quick Start

```python
from weather_sdk import OWMClient, WeatherCache

cache = WeatherCache()

with OWMClient(api_key="YOUR_KEY") as client:
    geo = client.geo.geocode("London")
    cache.put_location("London", geo)

    weather = client.weather.current(geo.coordinates)
    cache.put_current_weather("London", weather)

    aqi = client.air.quality(geo.coordinates)
    cache.put_air_quality("London", aqi)

# Read from cache — no network calls
print(cache.get_current_weather("London").temp_celsius)
print(cache.list_cities())
cache.evict("London")
```

## Installation

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest --cov=weather_sdk
```

## Type Checking & Linting

```bash
mypy weather_sdk
flake8 weather_sdk tests
```
