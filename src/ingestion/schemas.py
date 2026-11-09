"""Data schemas and contracts for external climate observations and historical baselines.

Enforces clear provenance metadata, freshness timestamps, and explicit flags
distinguishing verified live/historical data from fallback simulated fixtures.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


WEATHER_CODE_DESCRIPTIONS: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_description(code: int) -> str:
    """Returns human-readable weather description for WMO weather code."""
    return WEATHER_CODE_DESCRIPTIONS.get(code, f"Weather condition (code {code})")


@dataclass(frozen=True)
class DailyForecastItem:
    """Daily forecast metrics for a single date."""
    date: str
    temp_max_c: float
    temp_min_c: float
    precipitation_sum_mm: float
    precipitation_hours: float
    precipitation_probability_pct: int


@dataclass
class LiveWeatherObservation:
    """Current weather observation and short-term forecast for Pune."""
    source: str                          # e.g., "open-meteo" | "cache" | "fallback"
    retrieval_timestamp: str             # ISO8601 UTC string
    latitude: float
    longitude: float
    elevation_m: float
    temperature_c: float
    apparent_temperature_c: float
    relative_humidity_pct: float
    precipitation_mm: float
    wind_speed_kmh: float
    weather_code: int
    weather_description: str
    daily_forecast: List[DailyForecastItem] = field(default_factory=list)
    data_status: str = "verified_live"   # "verified_live" | "cached" | "fallback_simulated"
    is_live: bool = True
    cache_hit: bool = False
    freshness_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert observation to serializable dictionary."""
        d = asdict(self)
        return d


@dataclass
class HistoricalClimateSummary:
    """Historical climate summary over a specified multi-month or annual period."""
    source: str                          # e.g., "open-meteo-era5" | "fallback"
    retrieval_timestamp: str             # ISO8601 UTC string
    latitude: float
    longitude: float
    period_start: str                    # YYYY-MM-DD
    period_end: str                      # YYYY-MM-DD
    days_count: int
    total_rainfall_mm: float
    max_daily_rainfall_mm: float
    mean_daily_rainfall_mm: float
    mean_temp_max_c: float
    mean_temp_min_c: float
    heatwave_days: int                   # Days with Tmax >= 38.0°C (Pune heat threshold)
    heavy_rain_days: int                 # Days with Rain >= 35.5 mm (IMD rather heavy threshold)
    data_status: str = "verified_historical"  # "verified_historical" | "cached" | "fallback_simulated"
    is_live: bool = False
    cache_hit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to serializable dictionary."""
        return asdict(self)
