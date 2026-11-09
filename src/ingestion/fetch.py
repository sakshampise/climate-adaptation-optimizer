"""Ingestion orchestrator coordinating external API retrieval, caching, and fallback."""

from datetime import datetime, timezone
import logging
import statistics
from typing import Any, Dict, List, Optional
import requests
from src.ingestion.cache import ClimateCache
from src.ingestion.schemas import (
    LiveWeatherObservation,
    DailyForecastItem,
    HistoricalClimateSummary,
    get_weather_description,
)
from src.integrations.open_meteo import OpenMeteoClient
from src.integrations.base import IntegrationError

logger = logging.getLogger(__name__)

PUNE_CENTROID_LAT = 18.5204
PUNE_CENTROID_LON = 73.8567
LIVE_CACHE_TTL_SECONDS = 1800      # 30 minutes
HISTORICAL_CACHE_TTL_SECONDS = 86400 * 7  # 7 days


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Converts a value to float, safely handling None, invalid strings, and type errors."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    """Converts a value to integer, safely handling None, floats, and strings."""
    if val is None:
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def get_fallback_live_observation() -> LiveWeatherObservation:
    """Returns an illustrative synthetic weather observation for offline fallback.

    Explicitly tagged as 'fallback_simulated' and 'is_live=False'.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    return LiveWeatherObservation(
        source="illustrative_fallback",
        retrieval_timestamp=now_iso,
        observation_time=now_iso[:16],
        latitude=PUNE_CENTROID_LAT,
        longitude=PUNE_CENTROID_LON,
        elevation_m=560.0,
        temperature_c=28.5,
        apparent_temperature_c=29.2,
        relative_humidity_pct=45.0,
        precipitation_mm=0.0,
        wind_speed_kmh=10.0,
        weather_code=1,
        weather_description="Mainly clear (Offline Fallback)",
        daily_forecast=[
            DailyForecastItem(
                date=f"2026-11-{d:02d}",
                temp_max_c=31.0,
                temp_min_c=18.0,
                precipitation_sum_mm=0.0,
                precipitation_hours=0.0,
                precipitation_probability_pct=5,
            )
            for d in range(10, 17)
        ],
        data_status="fallback_simulated",
        is_live=False,
        cache_hit=False,
        freshness_seconds=None,
    )


def get_fallback_historical_summary() -> HistoricalClimateSummary:
    """Returns an illustrative historical baseline for Pune monsoon season (June-Sept)."""
    now_iso = datetime.now(timezone.utc).isoformat()
    return HistoricalClimateSummary(
        source="illustrative_fallback",
        retrieval_timestamp=now_iso,
        latitude=PUNE_CENTROID_LAT,
        longitude=PUNE_CENTROID_LON,
        period_start="2024-06-01",
        period_end="2024-09-30",
        days_count=122,
        valid_days_count=122,
        data_completeness_pct=100.0,
        total_rainfall_mm=752.4,
        max_daily_rainfall_mm=86.5,
        mean_daily_rainfall_mm=6.17,
        mean_temp_max_c=28.4,
        mean_temp_min_c=22.1,
        heat_stress_days_ge_38c=2,
        imd_heavy_rain_days_ge_64_5mm=3,
        moderate_to_heavy_rain_days_ge_35_5mm=6,
        data_status="fallback_simulated",
        is_live=False,
        cache_hit=False,
    )


def parse_live_observation_dict(
    data: Dict[str, Any],
    source: str,
    data_status: str,
    is_live: bool,
    cache_hit: bool,
    age_seconds: Optional[float] = None,
    retrieval_timestamp: Optional[str] = None,
) -> LiveWeatherObservation:
    """Parses raw Open-Meteo response or cached dict into LiveWeatherObservation.

    Safely handles missing keys, null array elements, and corrupted types.
    """
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict for observation payload, received {type(data).__name__}")

    current = data.get("current", {}) if isinstance(data.get("current"), dict) else {}
    daily = data.get("daily", {}) if isinstance(data.get("daily"), dict) else {}

    weather_code = _safe_int(current.get("weather_code"), default=0)
    weather_desc = get_weather_description(weather_code)

    forecast_items: List[DailyForecastItem] = []
    times = daily.get("time", []) if isinstance(daily.get("time"), list) else []
    max_temps = daily.get("temperature_2m_max", []) if isinstance(daily.get("temperature_2m_max"), list) else []
    min_temps = daily.get("temperature_2m_min", []) if isinstance(daily.get("temperature_2m_min"), list) else []
    rain_sums = daily.get("precipitation_sum", []) if isinstance(daily.get("precipitation_sum"), list) else []
    rain_hours = daily.get("precipitation_hours", []) if isinstance(daily.get("precipitation_hours"), list) else []
    rain_probs = daily.get("precipitation_probability_max", []) if isinstance(daily.get("precipitation_probability_max"), list) else []

    for i, date_str in enumerate(times):
        forecast_items.append(
            DailyForecastItem(
                date=str(date_str),
                temp_max_c=_safe_float(max_temps[i] if i < len(max_temps) else None, default=0.0),
                temp_min_c=_safe_float(min_temps[i] if i < len(min_temps) else None, default=0.0),
                precipitation_sum_mm=_safe_float(rain_sums[i] if i < len(rain_sums) else None, default=0.0),
                precipitation_hours=_safe_float(rain_hours[i] if i < len(rain_hours) else None, default=0.0),
                precipitation_probability_pct=_safe_int(rain_probs[i] if i < len(rain_probs) else None, default=0),
            )
        )

    # Observation time from provider (e.g. "2026-11-09T18:00")
    observation_time = str(current.get("time") or "")

    # Retrieval timestamp preserves original fetch time from cache if available
    retrieval_ts = retrieval_timestamp or datetime.now(timezone.utc).isoformat()

    return LiveWeatherObservation(
        source=source,
        retrieval_timestamp=retrieval_ts,
        observation_time=observation_time,
        latitude=_safe_float(data.get("latitude"), default=PUNE_CENTROID_LAT),
        longitude=_safe_float(data.get("longitude"), default=PUNE_CENTROID_LON),
        elevation_m=_safe_float(data.get("elevation"), default=560.0),
        temperature_c=_safe_float(current.get("temperature_2m"), default=0.0),
        apparent_temperature_c=_safe_float(current.get("apparent_temperature"), default=0.0),
        relative_humidity_pct=_safe_float(current.get("relative_humidity_2m"), default=0.0),
        precipitation_mm=_safe_float(current.get("precipitation"), default=0.0),
        wind_speed_kmh=_safe_float(current.get("wind_speed_10m"), default=0.0),
        weather_code=weather_code,
        weather_description=weather_desc,
        daily_forecast=forecast_items,
        data_status=data_status,
        is_live=is_live,
        cache_hit=cache_hit,
        freshness_seconds=age_seconds,
    )


def fetch_live_climate(
    latitude: float = PUNE_CENTROID_LAT,
    longitude: float = PUNE_CENTROID_LON,
    client: Optional[OpenMeteoClient] = None,
    cache: Optional[ClimateCache] = None,
    use_cache: bool = True,
) -> LiveWeatherObservation:
    """Fetches live weather observation for Pune with caching, retry, and fallback.

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        client: Optional OpenMeteoClient instance (for dependency injection/testing).
        cache: Optional ClimateCache instance.
        use_cache: Whether to check and write to disk cache.

    Returns:
        Validated LiveWeatherObservation.
    """
    cache_inst = cache if cache is not None else ClimateCache()
    cache_key = f"open_meteo_live_{latitude:.4f}_{longitude:.4f}"

    # 1. Try cache if enabled
    if use_cache:
        cached_result = cache_inst.get(cache_key)
        if cached_result is not None:
            data, age, orig_ts = cached_result
            try:
                return parse_live_observation_dict(
                    data=data,
                    source="open-meteo (cached)",
                    data_status="cached",
                    is_live=True,
                    cache_hit=True,
                    age_seconds=age,
                    retrieval_timestamp=orig_ts,
                )
            except Exception as parse_err:
                logger.warning("Corrupted cached record for %s: %s", cache_key, parse_err)

    # 2. Try live API call
    client_inst = client if client is not None else OpenMeteoClient()
    fetch_ts = datetime.now(timezone.utc).isoformat()
    try:
        raw_data = client_inst.fetch_current_and_forecast(latitude, longitude)
        obs = parse_live_observation_dict(
            data=raw_data,
            source="open-meteo (live)",
            data_status="verified_live",
            is_live=True,
            cache_hit=False,
            age_seconds=0.0,
            retrieval_timestamp=fetch_ts,
        )
        if use_cache:
            cache_inst.set(cache_key, raw_data, ttl_seconds=LIVE_CACHE_TTL_SECONDS, retrieval_timestamp=fetch_ts)
        return obs

    except (IntegrationError, requests.RequestException) as net_err:
        logger.info("Open-Meteo live API unavailable (%s); attempting stale cache fallback", net_err)
        # 3. Network or API error -> attempt stale cache
        stale_result = cache_inst.get_stale(cache_key)
        if stale_result is not None:
            data, age, orig_ts = stale_result
            try:
                return parse_live_observation_dict(
                    data=data,
                    source="open-meteo (stale cache)",
                    data_status="cached",
                    is_live=False,  # Clearly not live!
                    cache_hit=True,
                    age_seconds=age,
                    retrieval_timestamp=orig_ts,
                )
            except Exception as stale_err:
                logger.warning("Failed to parse stale cache for %s: %s", cache_key, stale_err)

        # 4. No cache available -> graceful offline fallback
        return get_fallback_live_observation()

    except Exception as unexpected_err:
        logger.error(
            "Unexpected error during live climate fetch (%s): %s",
            type(unexpected_err).__name__,
            unexpected_err,
            exc_info=True,
        )
        # In unexpected programming failure, log traceback and fall back safely
        return get_fallback_live_observation()


def fetch_historical_climate(
    latitude: float = PUNE_CENTROID_LAT,
    longitude: float = PUNE_CENTROID_LON,
    start_date: str = "2024-06-01",
    end_date: str = "2024-09-30",
    client: Optional[OpenMeteoClient] = None,
    cache: Optional[ClimateCache] = None,
    use_cache: bool = True,
) -> HistoricalClimateSummary:
    """Fetches historical climate records and computes statistical baseline indicators.

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        start_date: Period start date (YYYY-MM-DD).
        end_date: Period end date (YYYY-MM-DD).
        client: Optional OpenMeteoClient instance.
        cache: Optional ClimateCache instance.
        use_cache: Whether to use caching.

    Returns:
        HistoricalClimateSummary with computed aggregates.
    """
    cache_inst = cache if cache is not None else ClimateCache()
    cache_key = f"open_meteo_hist_{latitude:.4f}_{longitude:.4f}_{start_date}_{end_date}"

    if use_cache:
        cached_result = cache_inst.get(cache_key)
        if cached_result is not None:
            data, _, orig_ts = cached_result
            try:
                # Remove deprecated properties if present in stored JSON
                clean_data = {k: v for k, v in data.items() if k not in ("heatwave_days", "heavy_rain_days")}
                return HistoricalClimateSummary(**clean_data)
            except Exception as parse_err:
                logger.warning("Corrupted cached historical record for %s: %s", cache_key, parse_err)

    client_inst = client if client is not None else OpenMeteoClient()
    fetch_ts = datetime.now(timezone.utc).isoformat()
    try:
        raw_data = client_inst.fetch_historical_archive(latitude, longitude, start_date, end_date)
        daily = raw_data.get("daily", {}) if isinstance(raw_data.get("daily"), dict) else {}

        time_list = daily.get("time", []) if isinstance(daily.get("time"), list) else []
        days_count = len(time_list)

        raw_precip = daily.get("precipitation_sum", []) if isinstance(daily.get("precipitation_sum"), list) else []
        raw_tmax = daily.get("temperature_2m_max", []) if isinstance(daily.get("temperature_2m_max"), list) else []
        raw_tmin = daily.get("temperature_2m_min", []) if isinstance(daily.get("temperature_2m_min"), list) else []

        valid_precip = [_safe_float(x) for x in raw_precip if x is not None]
        valid_tmax = [_safe_float(x) for x in raw_tmax if x is not None]
        valid_tmin = [_safe_float(x) for x in raw_tmin if x is not None]

        valid_days_count = len(valid_precip)
        completeness_pct = round((valid_days_count / days_count * 100.0), 1) if days_count > 0 else 0.0

        total_rain = sum(valid_precip) if valid_precip else 0.0
        max_daily_rain = max(valid_precip) if valid_precip else 0.0
        mean_daily_rain = statistics.mean(valid_precip) if valid_precip else 0.0
        mean_tmax = statistics.mean(valid_tmax) if valid_tmax else 0.0
        mean_tmin = statistics.mean(valid_tmin) if valid_tmin else 0.0

        # Thresholds per approved scope:
        # 1. heat_stress_days_ge_38c: project-defined planning indicator (PMC alert level), not official IMD heatwave
        heat_stress_days = sum(1 for t in valid_tmax if t >= 38.0)
        # 2. imd_heavy_rain_days_ge_64_5mm: official IMD Heavy Rain criterion (>= 64.5 mm)
        imd_heavy_rain_days = sum(1 for r in valid_precip if r >= 64.5)
        # 3. moderate_to_heavy_rain_days_ge_35_5mm: project-defined rainfall indicator (>= 35.5 mm)
        mod_heavy_rain_days = sum(1 for r in valid_precip if r >= 35.5)

        summary = HistoricalClimateSummary(
            source="open-meteo-era5",
            retrieval_timestamp=fetch_ts,
            latitude=_safe_float(raw_data.get("latitude"), default=latitude),
            longitude=_safe_float(raw_data.get("longitude"), default=longitude),
            period_start=start_date,
            period_end=end_date,
            days_count=days_count,
            valid_days_count=valid_days_count,
            data_completeness_pct=completeness_pct,
            total_rainfall_mm=round(total_rain, 1),
            max_daily_rainfall_mm=round(max_daily_rain, 1),
            mean_daily_rainfall_mm=round(mean_daily_rain, 2),
            mean_temp_max_c=round(mean_tmax, 1),
            mean_temp_min_c=round(mean_tmin, 1),
            heat_stress_days_ge_38c=heat_stress_days,
            imd_heavy_rain_days_ge_64_5mm=imd_heavy_rain_days,
            moderate_to_heavy_rain_days_ge_35_5mm=mod_heavy_rain_days,
            data_status="verified_historical",
            is_live=False,
            cache_hit=False,
        )

        if use_cache:
            cache_inst.set(cache_key, summary.to_dict(), ttl_seconds=HISTORICAL_CACHE_TTL_SECONDS, retrieval_timestamp=fetch_ts)

        return summary

    except (IntegrationError, requests.RequestException) as net_err:
        logger.info("Open-Meteo historical archive unavailable (%s); checking stale cache", net_err)
        stale_result = cache_inst.get_stale(cache_key)
        if stale_result is not None:
            data, _, orig_ts = stale_result
            try:
                clean_data = {k: v for k, v in data.items() if k not in ("heatwave_days", "heavy_rain_days")}
                summary = HistoricalClimateSummary(**clean_data)
                summary.cache_hit = True
                return summary
            except Exception as stale_err:
                logger.warning("Failed to parse stale historical cache for %s: %s", cache_key, stale_err)

        return get_fallback_historical_summary()

    except Exception as unexpected_err:
        logger.error(
            "Unexpected error in fetch_historical_climate (%s): %s",
            type(unexpected_err).__name__,
            unexpected_err,
            exc_info=True,
        )
        return get_fallback_historical_summary()
