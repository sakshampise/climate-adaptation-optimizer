"""Ingestion orchestrator coordinating external API retrieval, caching, and fallback."""

from datetime import datetime, timezone, timedelta
import logging
import statistics
from typing import Any, Dict, List, Optional
import requests
from src.ingestion.cache import ClimateCache
from src.ingestion.schemas import (
    LiveWeatherObservation,
    DailyForecastItem,
    HistoricalClimateSummary,
    NasaClimatologyParameter,
    NasaClimatologySummary,
    DAYS_IN_MONTH,
    get_weather_description,
)
from src.integrations.open_meteo import OpenMeteoClient
from src.integrations.nasa_power import NasaPowerClient
from src.integrations.base import IntegrationError

logger = logging.getLogger(__name__)

PUNE_CENTROID_LAT = 18.5204
PUNE_CENTROID_LON = 73.8567
LIVE_CACHE_TTL_SECONDS = 1800      # 30 minutes
HISTORICAL_CACHE_TTL_SECONDS = 86400 * 7  # 7 days
NASA_CLIMATOLOGY_CACHE_TTL_SECONDS = 86400 * 30  # 30 days

MONTH_KEYS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")

NASA_PARAMETER_METADATA_SPEC: Dict[str, Dict[str, str]] = {
    "ALLSKY_SFC_SW_DWN": {
        "source_dataset": "SYN1DEG (CERES / GEWEX)",
        "native_spatial_resolution": "1.00° x 1.00° (~110 km)",
        "aggregation_semantics": "Day-weighted mean daily downward solar flux (kW-hr/m²/day)",
        "default_period": "January 2001 - December 2025 (25-year)",
    },
    "TS": {
        "source_dataset": "MERRA2",
        "native_spatial_resolution": "0.50° x 0.625° (~55 km)",
        "aggregation_semantics": "Day-weighted annual mean ground skin temperature (°C)",
        "default_period": "January 2001 - December 2025 (25-year)",
    },
    "PRECTOTCORR": {
        "source_dataset": "MERRA2 (GPCP-adjusted)",
        "native_spatial_resolution": "0.50° x 0.625° (~55 km)",
        "aggregation_semantics": "Day-weighted mean daily precipitation rate (mm/day); cumulative annual normal equivalent is ~1,730 mm/year",
        "default_period": "January 2001 - December 2025 (25-year)",
    },
}


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
    Generates 7-day forecast dates dynamically relative to current UTC date.
    """
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    today = now.date()
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
                date=(today + timedelta(days=i)).isoformat(),
                temp_max_c=31.0,
                temp_min_c=18.0,
                precipitation_sum_mm=0.0,
                precipitation_hours=0.0,
                precipitation_probability_pct=5,
            )
            for i in range(7)
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


def _safe_nasa_float(val: Any) -> Optional[float]:
    """Parse numeric float while strictly filtering NASA -999.0 fill values and sentinels."""
    if val is None or val == -999.0 or val == -999:
        return None
    try:
        f = float(val)
        return None if f < -900.0 else round(f, 3)
    except (ValueError, TypeError):
        return None


def parse_nasa_parameter(
    param_id: str,
    raw_props: Dict[str, Any],
    metadata_params: Dict[str, Any],
    header_info: Dict[str, Any],
) -> NasaClimatologyParameter:
    """Parse parameter values and bind parameter-specific source, period, units, and aggregation semantics."""
    param_meta = metadata_params.get(param_id, {})
    spec = NASA_PARAMETER_METADATA_SPEC.get(param_id, {})

    # DYNAMIC UNIT EXTRACTION: dynamically bind units returned by API metadata
    units = param_meta.get("units", "unknown")
    long_name = param_meta.get("longname", param_id)

    # Documented climatology period from header range or parameter-specific baseline
    climatology_period = str(header_info.get("range") or spec.get("default_period", "January 2001 - December 2025 (25-year)"))

    param_data = raw_props.get("parameter", {}).get(param_id, {})

    monthly_vals: Dict[str, Optional[float]] = {}
    for m in MONTH_KEYS:
        monthly_vals[m] = _safe_nasa_float(param_data.get(m))

    annual_val = _safe_nasa_float(param_data.get("ANN"))

    return NasaClimatologyParameter(
        parameter_id=param_id,
        long_name=long_name,
        units=units,
        source_dataset=spec.get("source_dataset", "NASA POWER"),
        native_spatial_resolution=spec.get("native_spatial_resolution", "Native"),
        climatology_period=climatology_period,
        aggregation_semantics=spec.get("aggregation_semantics", "Annual mean"),
        monthly_values=monthly_vals,
        annual_value=annual_val,
    )


def get_fallback_nasa_climatology() -> NasaClimatologySummary:
    """Returns an illustrative synthetic NASA POWER climatological baseline for Pune.

    Explicitly tagged as 'fallback_simulated' and 'is_live=False'.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    return NasaClimatologySummary(
        source="illustrative_fallback (NASA POWER simulated)",
        retrieval_timestamp=now_iso,
        latitude=PUNE_CENTROID_LAT,
        longitude=PUNE_CENTROID_LON,
        elevation_m=635.99,
        solar_irradiance=NasaClimatologyParameter(
            parameter_id="ALLSKY_SFC_SW_DWN",
            long_name="All Sky Surface Shortwave Downward Irradiance",
            units="kW-hr/m^2/day",
            source_dataset="SYN1DEG (CERES / GEWEX)",
            native_spatial_resolution="1.00° x 1.00° (~110 km)",
            climatology_period="January 2001 - December 2025 (25-year)",
            aggregation_semantics="Day-weighted mean daily downward solar flux (kW-hr/m²/day)",
            monthly_values={
                "JAN": 4.989, "FEB": 5.850, "MAR": 6.614, "APR": 7.078,
                "MAY": 7.017, "JUN": 4.568, "JUL": 3.310, "AUG": 3.384,
                "SEP": 4.309, "OCT": 5.012, "NOV": 4.896, "DEC": 4.665,
            },
            annual_value=5.135,
        ),
        surface_temperature=NasaClimatologyParameter(
            parameter_id="TS",
            long_name="Earth Skin Temperature",
            units="C",
            source_dataset="MERRA2",
            native_spatial_resolution="0.50° x 0.625° (~55 km)",
            climatology_period="January 2001 - December 2025 (25-year)",
            aggregation_semantics="Day-weighted annual mean ground skin temperature (°C)",
            monthly_values={
                "JAN": 19.64, "FEB": 23.46, "MAR": 28.06, "APR": 31.56,
                "MAY": 31.59, "JUN": 26.91, "JUL": 24.44, "AUG": 23.67,
                "SEP": 23.77, "OCT": 22.78, "NOV": 20.57, "DEC": 18.95,
            },
            annual_value=24.61,
        ),
        precipitation=NasaClimatologyParameter(
            parameter_id="PRECTOTCORR",
            long_name="Precipitation Corrected",
            units="mm/day",
            source_dataset="MERRA2 (GPCP-adjusted)",
            native_spatial_resolution="0.50° x 0.625° (~55 km)",
            climatology_period="January 2001 - December 2025 (25-year)",
            aggregation_semantics="Day-weighted mean daily precipitation rate (mm/day); cumulative annual normal equivalent is ~1,730 mm/year",
            monthly_values={
                "JAN": 0.03, "FEB": 0.05, "MAR": 0.15, "APR": 0.14,
                "MAY": 0.84, "JUN": 12.06, "JUL": 16.61, "AUG": 13.19,
                "SEP": 9.17, "OCT": 3.41, "NOV": 0.73, "DEC": 0.13,
            },
            annual_value=4.74,
        ),
        data_status="fallback_simulated",
        is_live=False,
        cache_hit=False,
    )


def fetch_nasa_climatology(
    latitude: float = PUNE_CENTROID_LAT,
    longitude: float = PUNE_CENTROID_LON,
    client: Optional[NasaPowerClient] = None,
    cache: Optional[ClimateCache] = None,
    use_cache: bool = True,
) -> NasaClimatologySummary:
    """Fetches multi-decadal solar and surface climatology normals from NASA POWER.

    Coordinates retrieval for:
    - ALLSKY_SFC_SW_DWN (Surface solar irradiance)
    - TS (Earth skin / surface temperature)
    - PRECTOTCORR (Precipitation corrected)

    Args:
        latitude: Geographic latitude in decimal degrees.
        longitude: Geographic longitude in decimal degrees.
        client: Optional NasaPowerClient for testing/mocking.
        cache: Optional ClimateCache instance.
        use_cache: Whether to check and write to disk cache.

    Returns:
        NasaClimatologySummary instance with verified, cached, or fallback status.
    """
    cache_inst = cache if cache is not None else ClimateCache()
    cache_key = f"nasa_power_climatology_{latitude:.4f}_{longitude:.4f}"

    if use_cache:
        cached_result = cache_inst.get(cache_key)
        if cached_result is not None:
            data, _, orig_ts = cached_result
            try:
                summary = NasaClimatologySummary.from_dict(data)
                summary.cache_hit = True
                summary.data_status = "cached"
                return summary
            except Exception as parse_err:
                logger.warning("Corrupted cached NASA climatology record for %s: %s", cache_key, parse_err)

    client_inst = client if client is not None else NasaPowerClient()
    fetch_ts = datetime.now(timezone.utc).isoformat()

    try:
        raw_data = client_inst.fetch_climatology(
            latitude=latitude,
            longitude=longitude,
            parameters=["ALLSKY_SFC_SW_DWN", "TS", "PRECTOTCORR"],
            community="RE",
        )

        props = raw_data.get("properties", {})
        meta_params = raw_data.get("parameters", {})
        header = raw_data.get("header", {})
        geometry = raw_data.get("geometry", {})
        coords = geometry.get("coordinates", [longitude, latitude, 635.99])
        elevation = float(coords[2]) if len(coords) > 2 else 635.99

        solar = parse_nasa_parameter("ALLSKY_SFC_SW_DWN", props, meta_params, header)
        surface_temp = parse_nasa_parameter("TS", props, meta_params, header)
        precip = parse_nasa_parameter("PRECTOTCORR", props, meta_params, header)

        summary = NasaClimatologySummary(
            source="NASA POWER (MERRA-2 / CERES SYN1DEG)",
            retrieval_timestamp=fetch_ts,
            latitude=latitude,
            longitude=longitude,
            elevation_m=elevation,
            solar_irradiance=solar,
            surface_temperature=surface_temp,
            precipitation=precip,
            data_status="verified_climatology",
            is_live=False,
            cache_hit=False,
        )

        if use_cache:
            cache_inst.set(
                cache_key,
                summary.to_dict(),
                ttl_seconds=NASA_CLIMATOLOGY_CACHE_TTL_SECONDS,
                retrieval_timestamp=fetch_ts,
            )

        return summary

    except (IntegrationError, requests.RequestException) as net_err:
        logger.info("NASA POWER API unavailable (%s); checking stale cache", net_err)
        stale_result = cache_inst.get_stale(cache_key)
        if stale_result is not None:
            data, _, orig_ts = stale_result
            try:
                summary = NasaClimatologySummary.from_dict(data)
                summary.cache_hit = True
                summary.data_status = "cached"
                return summary
            except Exception as stale_err:
                logger.warning("Failed to parse stale NASA climatology cache for %s: %s", cache_key, stale_err)

        return get_fallback_nasa_climatology()

    except Exception as unexpected_err:
        logger.error(
            "Unexpected error in fetch_nasa_climatology (%s): %s",
            type(unexpected_err).__name__,
            unexpected_err,
            exc_info=True,
        )
        return get_fallback_nasa_climatology()


