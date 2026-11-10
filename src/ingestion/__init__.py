"""Ingestion and caching layer for climate data."""

from src.ingestion.schemas import (
    LiveWeatherObservation,
    DailyForecastItem,
    HistoricalClimateSummary,
    get_weather_description,
)
from src.ingestion.cache import ClimateCache
from src.ingestion.fetch import (
    fetch_live_climate,
    fetch_historical_climate,
    get_fallback_live_observation,
    get_fallback_historical_summary,
)

__all__ = [
    "LiveWeatherObservation",
    "DailyForecastItem",
    "HistoricalClimateSummary",
    "get_weather_description",
    "ClimateCache",
    "fetch_live_climate",
    "fetch_historical_climate",
    "get_fallback_live_observation",
    "get_fallback_historical_summary",
]
