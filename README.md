# Weather SDK

A clean Python SDK for the [OpenWeatherMap API](https://openweathermap.org/api) with three endpoints and in-memory CRUD storage.

## Architecture

```
weather_sdk/
├── api/
│   └── client.py          # Thin HTTP wrapper (httpx)
├── storage/
│   └── repository.py      # Generic InMemoryRepository[T]
├── service/
│   └── weather_service.py # Orchestration façade
├── models.py              # Frozen dataclasses (domain types)
└── exceptions.py          # Custom exception hierarchy
```

### Layers

| Layer | Responsibility |
|-------|---------------|
| **API** | HTTP calls, JSON → dataclass parsing, error mapping |
| **Storage** | Generic CRUD over an in-memory `dict` |
| **Service** | Composes API + Storage; public interface for callers |

## Covered Endpoints

| Method | OWM endpoint | Description |
|--------|-------------|-------------|
| `fetch_location` | `GET /geo/1.0/direct` | Forward geocoding |
| `fetch_current_weather` | `GET /data/2.5/weather` | Current weather |
| `fetch_air_quality` | `GET /data/2.5/air_pollution` | Air quality index |

## Quick Start

```python
from weather_sdk import WeatherService

with WeatherService(api_key="YOUR_KEY") as svc:
    # Fetch (network) and store
    weather = svc.fetch_current_weather("London")
    aqi     = svc.fetch_air_quality("London")

    print(f"{weather.city}: {weather.temp_celsius}°C, AQI {aqi.aqi}")

    # Read from cache (no network)
    cached = svc.get_current_weather("London")

    # See what's cached
    print(svc.list_cached_cities())

    # Remove from cache
    svc.evict("London")
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
