# Weather SDK

A Python SDK for the [OpenWeatherMap API](https://openweathermap.org/api) with three endpoints and in-memory CRUD storage.

## Architecture

```
weather_sdk/
├── api/
│   └── client.py       # HTTP client (httpx) — fetching only
├── storage/
│   └── repository.py   # Generic InMemoryRepository[T]
├── service/
│   └── weather_cache.py  # WeatherCache — stores and reads data by city
├── models.py           # Frozen dataclasses (domain types)
└── exceptions.py       # Custom exception hierarchy
```

| Layer | Responsibility |
|-------|---------------|
| **API** | HTTP calls, JSON → dataclass parsing, error mapping |
| **Storage** | Generic CRUD over an in-memory `dict` |
| **Cache** | Typed store for weather data; key normalisation; eviction |

## Covered Endpoints

| Client method | OWM endpoint | Description |
|--------------|-------------|-------------|
| `geocode` | `GET /geo/1.0/direct` | Forward geocoding |
| `current_weather` | `GET /data/2.5/weather` | Current weather |
| `air_quality` | `GET /data/2.5/air_pollution` | Air quality index |

## Quick Start

```python
from weather_sdk import WeatherAPIClient, WeatherCache

cache = WeatherCache()

with WeatherAPIClient(api_key="YOUR_KEY") as client:
    geo = client.geocode("London")
    cache.put_location("London", geo)

    weather = client.current_weather(geo.coordinates)
    cache.put_current_weather("London", weather)

    aqi = client.air_quality(geo.coordinates)
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
