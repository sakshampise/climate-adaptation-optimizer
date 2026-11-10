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
    retrieval_timestamp: str             # ISO8601 UTC string (when data was retrieved / cached)
    observation_time: str                # Timestamp reported by meteorological provider
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
        return asdict(self)


@dataclass
class HistoricalClimateSummary:
    """Historical climate summary over a specified multi-month or annual period."""
    source: str                          # e.g., "open-meteo-era5" | "fallback"
    retrieval_timestamp: str             # ISO8601 UTC string
    latitude: float
    longitude: float
    period_start: str                    # YYYY-MM-DD
    period_end: str                      # YYYY-MM-DD
    days_count: int                      # Total calendar days in target period
    valid_days_count: int                # Days with valid, non-null observations
    data_completeness_pct: float         # valid_days_count / days_count * 100
    total_rainfall_mm: float
    max_daily_rainfall_mm: float
    mean_daily_rainfall_mm: float
    mean_temp_max_c: float
    mean_temp_min_c: float
    heat_stress_days_ge_38c: int         # Project-defined planning indicator: Tmax >= 38.0°C (PMC alert level)
    imd_heavy_rain_days_ge_64_5mm: int   # Official IMD Heavy Rain criterion: daily precipitation >= 64.5 mm
    moderate_to_heavy_rain_days_ge_35_5mm: int  # Project-defined rainfall indicator: daily rain >= 35.5 mm
    data_status: str = "verified_historical"  # "verified_historical" | "cached" | "fallback_simulated"
    is_live: bool = False
    cache_hit: bool = False

    @property
    def heatwave_days(self) -> int:
        """Backward-compatible alias for heat_stress_days_ge_38c."""
        return self.heat_stress_days_ge_38c

    @property
    def heavy_rain_days(self) -> int:
        """Backward-compatible alias for moderate_to_heavy_rain_days_ge_35_5mm."""
        return self.moderate_to_heavy_rain_days_ge_35_5mm

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to serializable dictionary."""
        return asdict(self)


DAYS_IN_MONTH: Dict[str, float] = {
    "JAN": 31.0,
    "FEB": 28.25,
    "MAR": 31.0,
    "APR": 30.0,
    "MAY": 31.0,
    "JUN": 30.0,
    "JUL": 31.0,
    "AUG": 31.0,
    "SEP": 30.0,
    "OCT": 31.0,
    "NOV": 30.0,
    "DEC": 31.0,
}


@dataclass(frozen=True)
class NasaClimatologyParameter:
    """Represents a single NASA POWER climatological parameter with monthly values and provenance metadata."""
    parameter_id: str                          # e.g., "ALLSKY_SFC_SW_DWN", "TS", "PRECTOTCORR"
    long_name: str                             # Descriptive name from API metadata
    units: str                                 # Dynamically parsed from API response metadata
    source_dataset: str                        # e.g., "SYN1DEG (CERES / GEWEX)" vs "MERRA2"
    native_spatial_resolution: str             # e.g., "1.00° x 1.00°" vs "0.50° x 0.625°"
    climatology_period: str                    # Documented baseline period (e.g. "January 2001 - December 2025")
    aggregation_semantics: str                 # Annual value mathematical interpretation
    monthly_values: Dict[str, Optional[float]] # {"JAN": 4.99, ... "DEC": 4.66}
    annual_value: Optional[float]              # e.g., 5.135 (from "ANN")


@dataclass
class NasaClimatologySummary:
    """Multi-decadal climatological baseline summary for Pune from NASA POWER."""
    source: str                                # "NASA POWER (MERRA-2 / CERES SYN1DEG)"
    retrieval_timestamp: str                   # ISO8601 UTC string
    latitude: float
    longitude: float
    elevation_m: float
    solar_irradiance: NasaClimatologyParameter # ALLSKY_SFC_SW_DWN
    surface_temperature: NasaClimatologyParameter # TS
    precipitation: NasaClimatologyParameter    # PRECTOTCORR
    data_status: str = "verified_climatology"  # "verified_climatology" | "cached" | "fallback_simulated"
    is_live: bool = False
    cache_hit: bool = False
    provenance_note: str = (
        "Climatological normals are derived from NASA POWER multi-decadal baselines. "
        "Solar radiation originates from CERES SYN1DEG at 1.00° resolution; surface temperature "
        "and precipitation originate from MERRA-2 at 0.50° x 0.625° resolution. "
        "Does not modify optimizer scoring or portfolio allocation."
    )

    @property
    def annual_cumulative_precipitation_mm(self) -> float:
        """Calculates cumulative annual rainfall normal equivalent from monthly daily rates."""
        total = 0.0
        for m, days in DAYS_IN_MONTH.items():
            rate = self.precipitation.monthly_values.get(m)
            if rate is not None:
                total += rate * days
        return round(total, 1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert climatology summary to serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NasaClimatologySummary":
        """Reconstruct NasaClimatologySummary from serialized dictionary."""
        d = dict(data)
        if isinstance(d.get("solar_irradiance"), dict):
            d["solar_irradiance"] = NasaClimatologyParameter(**d["solar_irradiance"])
        if isinstance(d.get("surface_temperature"), dict):
            d["surface_temperature"] = NasaClimatologyParameter(**d["surface_temperature"])
        if isinstance(d.get("precipitation"), dict):
            d["precipitation"] = NasaClimatologyParameter(**d["precipitation"])
        return cls(**d)

