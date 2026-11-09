"""Ingestion orchestrator coordinating external API retrieval, caching, and fallback."""

from datetime import datetime, timezone
import statistics
from typing import Any, Dict, List, Optional
from src.ingestion.cache import ClimateCache
from src.ingestion.schemas import (
    LiveWeatherObservation,
    DailyForecastItem,
    HistoricalClimateSummary,
    get_weather_description,
)
from src.integrations.open_meteo import OpenMeteoClient
from src.integrations.base import IntegrationError

PUNE_CENTROID_LAT = 18.5204
PUNE_CENTROID_LON = 73.8567
LIVE_CACHE_TTL_SECONDS = 1800      # 30 minutes
HISTORICAL_CACHE_TTL_SECONDS = 86400 * 7  # 7 days


def get_fallback_live_observation() -> LiveWeatherObservation:
    """Returns an illustrative synthetic weather observation for offline fallback.

    Explicitly tagged as 'fallback_simulated' and 'is_live=False'.
    """
    return LiveWeatherObservation(
        source="illustrative_fallback",
        retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
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
    return HistoricalClimateSummary(
        source="illustrative_fallback",
        retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
        latitude=PUNE_CENTROID_LAT,
        longitude=PUNE_CENTROID_LON,
        period_start="2024-06-01",
        period_end="2024-09-30",
        days_count=122,
        total_rainfall_mm=752.4,
        max_daily_rainfall_mm=86.5,
        mean_daily_rainfall_mm=6.17,
        mean_temp_max_c=28.4,
        mean_temp_min_c=22.1,
        heatwave_days=2,
        heavy_rain_days=6,
        data_status="fallback_simulated",
        is_live=False,
        cache_hit=False,
    )


def parse_live_observation_dict(data: Dict[str, Any], source: str, data_status: str, is_live: bool, cache_hit: bool, age_seconds: Optional[float] = None) -> LiveWeatherObservation:
    """Parses raw Open-Meteo response or cached dict into LiveWeatherObservation."""
    current = data.get("current", {})
    daily = data.get("daily", {})

    weather_code = int(current.get("weather_code", 0))
    weather_desc = get_weather_description(weather_code)

    forecast_items: List[DailyForecastItem] = []
    times = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    rain_sums = daily.get("precipitation_sum", [])
    rain_hours = daily.get("precipitation_hours", [])
    rain_probs = daily.get("precipitation_probability_max", [])

    for i, date_str in enumerate(times):
        forecast_items.append(
            DailyForecastItem(
                date=str(date_str),
                temp_max_c=float(max_temps[i]) if i < len(max_temps) else 0.0,
                temp_min_c=float(min_temps[i]) if i < len(min_temps) else 0.0,
                precipitation_sum_mm=float(rain_sums[i]) if i < len(rain_sums) else 0.0,
                precipitation_hours=float(rain_hours[i]) if i < len(rain_hours) else 0.0,
                precipitation_probability_pct=int(rain_probs[i]) if i < len(rain_probs) else 0,
            )
        )

    return LiveWeatherObservation(
        source=source,
        retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
        latitude=float(data.get("latitude", PUNE_CENTROID_LAT)),
        longitude=float(data.get("longitude", PUNE_CENTROID_LON)),
        elevation_m=float(data.get("elevation", 560.0)),
        temperature_c=float(current.get("temperature_2m", 0.0)),
        apparent_temperature_c=float(current.get("apparent_temperature", 0.0)),
        relative_humidity_pct=float(current.get("relative_humidity_2m", 0.0)),
        precipitation_mm=float(current.get("precipitation", 0.0)),
        wind_speed_kmh=float(current.get("wind_speed_10m", 0.0)),
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
            data, age = cached_result
            return parse_live_observation_dict(
                data=data,
                source="open-meteo (cached)",
                data_status="cached",
                is_live=True,
                cache_hit=True,
                age_seconds=age,
            )

    # 2. Try live API call
    client_inst = client if client is not None else OpenMeteoClient()
    try:
        raw_data = client_inst.fetch_current_and_forecast(latitude, longitude)
        obs = parse_live_observation_dict(
            data=raw_data,
            source="open-meteo (live)",
            data_status="verified_live",
            is_live=True,
            cache_hit=False,
            age_seconds=0.0,
        )
        if use_cache:
            cache_inst.set(cache_key, raw_data, ttl_seconds=LIVE_CACHE_TTL_SECONDS)
        return obs
    except (IntegrationError, Exception):
        # 3. Network or API error -> attempt stale cache
        stale_result = cache_inst.get_stale(cache_key)
        if stale_result is not None:
            data, age = stale_result
            return parse_live_observation_dict(
                data=data,
                source="open-meteo (stale cache)",
                data_status="cached",
                is_live=False,
                cache_hit=True,
                age_seconds=age,
            )

        # 4. No cache available -> graceful offline fallback
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
            data, _ = cached_result
            return HistoricalClimateSummary(**data)

    client_inst = client if client is not None else OpenMeteoClient()
    try:
        raw_data = client_inst.fetch_historical_archive(latitude, longitude, start_date, end_date)
        daily = raw_data.get("daily", {})

        precip_list = [float(x) for x in daily.get("precipitation_sum", []) if x is not None]
        tmax_list = [float(x) for x in daily.get("temperature_2m_max", []) if x is not None]
        tmin_list = [float(x) for x in daily.get("temperature_2m_min", []) if x is not None]

        days_count = len(daily.get("time", []))
        total_rain = sum(precip_list) if precip_list else 0.0
        max_daily_rain = max(precip_list) if precip_list else 0.0
        mean_daily_rain = statistics.mean(precip_list) if precip_list else 0.0
        mean_tmax = statistics.mean(tmax_list) if tmax_list else 0.0
        mean_tmin = statistics.mean(tmin_list) if tmin_list else 0.0

        # Pune heat threshold: Tmax >= 38.0°C; IMD heavy rain: daily rain >= 35.5 mm
        heatwave_days = sum(1 for t in tmax_list if t >= 38.0)
        heavy_rain_days = sum(1 for r in precip_list if r >= 35.5)

        summary = HistoricalClimateSummary(
            source="open-meteo-era5",
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            latitude=float(raw_data.get("latitude", latitude)),
            longitude=float(raw_data.get("longitude", longitude)),
            period_start=start_date,
            period_end=end_date,
            days_count=days_count,
            total_rainfall_mm=round(total_rain, 1),
            max_daily_rainfall_mm=round(max_daily_rain, 1),
            mean_daily_rainfall_mm=round(mean_daily_rain, 2),
            mean_temp_max_c=round(mean_tmax, 1),
            mean_temp_min_c=round(mean_tmin, 1),
            heatwave_days=heatwave_days,
            heavy_rain_days=heavy_rain_days,
            data_status="verified_historical",
            is_live=False,
            cache_hit=False,
        )

        if use_cache:
            cache_inst.set(cache_key, summary.to_dict(), ttl_seconds=HISTORICAL_CACHE_TTL_SECONDS)

        return summary
    except (IntegrationError, Exception):
        stale_result = cache_inst.get_stale(cache_key)
        if stale_result is not None:
            data, _ = stale_result
            summary = HistoricalClimateSummary(**data)
            summary.cache_hit = True
            return summary

        return get_fallback_historical_summary()
