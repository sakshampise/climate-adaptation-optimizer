"""Ingestion and caching layer for climate data."""

from src.ingestion.schemas import (
    LiveWeatherObservation,
    DailyForecastItem,
    HistoricalClimateSummary,
    NasaClimatologyParameter,
    NasaClimatologySummary,
    get_weather_description,
)
from src.ingestion.cache import ClimateCache
from src.ingestion.fetch import (
    fetch_live_climate,
    fetch_historical_climate,
    fetch_nasa_climatology,
    get_fallback_live_observation,
    get_fallback_historical_summary,
    get_fallback_nasa_climatology,
)

__all__ = [
    "LiveWeatherObservation",
    "DailyForecastItem",
    "HistoricalClimateSummary",
    "NasaClimatologyParameter",
    "NasaClimatologySummary",
    "get_weather_description",
    "ClimateCache",
    "fetch_live_climate",
    "fetch_historical_climate",
    "fetch_nasa_climatology",
    "get_fallback_live_observation",
    "get_fallback_historical_summary",
    "get_fallback_nasa_climatology",
]
