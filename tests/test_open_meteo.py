"""Automated unit and integration tests for Open-Meteo API pipeline, caching, and fallback."""

import json
import time
from unittest.mock import MagicMock, patch
import pytest
import requests
from src.integrations.base import BaseClient, IntegrationError
from src.integrations.open_meteo import OpenMeteoClient
from src.ingestion.cache import ClimateCache
from src.ingestion.fetch import (
    fetch_live_climate,
    fetch_historical_climate,
    get_fallback_live_observation,
    get_fallback_historical_summary,
    PUNE_CENTROID_LAT,
    PUNE_CENTROID_LON,
)
from src.ingestion.schemas import (
    LiveWeatherObservation,
    HistoricalClimateSummary,
    get_weather_description,
)

# Sample mock Open-Meteo Forecast response
MOCK_FORECAST_PAYLOAD = {
    "latitude": 18.52,
    "longitude": 73.86,
    "elevation": 560.0,
    "timezone": "Asia/Kolkata",
    "current": {
        "time": "2026-11-09T18:00",
        "temperature_2m": 27.6,
        "relative_humidity_2m": 32.0,
        "apparent_temperature": 26.0,
        "precipitation": 0.0,
        "weather_code": 0,
        "wind_speed_10m": 9.5,
    },
    "daily": {
        "time": ["2026-11-09", "2026-11-10", "2026-11-11"],
        "temperature_2m_max": [30.2, 31.0, 31.5],
        "temperature_2m_min": [18.5, 17.8, 17.2],
        "precipitation_sum": [0.0, 2.5, 14.2],
        "precipitation_hours": [0.0, 1.5, 4.0],
        "precipitation_probability_max": [0, 20, 65],
    },
}

# Sample mock Open-Meteo Historical Archive response
MOCK_ARCHIVE_PAYLOAD = {
    "latitude": 18.52,
    "longitude": 73.86,
    "elevation": 560.0,
    "daily": {
        "time": ["2024-07-01", "2024-07-02", "2024-07-03", "2024-07-04"],
        "temperature_2m_max": [28.0, 29.5, 39.0, 27.5],  # 1 day >= 38°C
        "temperature_2m_min": [22.0, 23.0, 24.0, 21.5],
        "precipitation_sum": [10.0, 42.0, 0.0, 5.0],     # 1 day >= 35.5mm
        "precipitation_hours": [6.0, 14.0, 0.0, 3.0],
    },
}


def test_weather_code_descriptions():
    """Verify WMO weather code to description mapping."""
    assert get_weather_description(0) == "Clear sky"
    assert get_weather_description(65) == "Heavy rain"
    assert get_weather_description(95) == "Thunderstorm"
    assert "999" in get_weather_description(999)


def test_base_client_success():
    """Verify BaseClient handles successful GET requests."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_session.get.return_value = mock_response

    client = BaseClient(base_url="https://api.test.com", session=mock_session)
    data = client.get("data", params={"q": 1})

    assert data == {"status": "ok"}
    mock_session.get.assert_called_once_with(
        "https://api.test.com/data", params={"q": 1}, timeout=8.0
    )


def test_base_client_retry_and_failure():
    """Verify BaseClient raises IntegrationError on persistent non-200 or request exception."""
    mock_session = MagicMock()
    mock_session.get.side_effect = requests.exceptions.Timeout("Connection timed out")

    client = BaseClient(base_url="https://api.test.com", session=mock_session)
    with pytest.raises(IntegrationError) as exc_info:
        client.get("endpoint")

    assert "Connection timed out" in str(exc_info.value)


def test_open_meteo_client_endpoints(monkeypatch):
    """Verify OpenMeteoClient constructs proper query parameters."""
    client = OpenMeteoClient()

    # Mock inner forecast_client.get
    mock_forecast_get = MagicMock(return_value=MOCK_FORECAST_PAYLOAD)
    monkeypatch.setattr(client.forecast_client, "get", mock_forecast_get)

    res = client.fetch_current_and_forecast(18.52, 73.86)
    assert res == MOCK_FORECAST_PAYLOAD
    mock_forecast_get.assert_called_once()
    args, kwargs = mock_forecast_get.call_args
    assert args[0] == "forecast"
    assert kwargs["params"]["latitude"] == 18.52
    assert "temperature_2m" in kwargs["params"]["current"]
    assert "temperature_2m_max" in kwargs["params"]["daily"]

    # Mock inner archive_client.get
    mock_archive_get = MagicMock(return_value=MOCK_ARCHIVE_PAYLOAD)
    monkeypatch.setattr(client.archive_client, "get", mock_archive_get)

    hist = client.fetch_historical_archive(18.52, 73.86, "2024-07-01", "2024-07-04")
    assert hist == MOCK_ARCHIVE_PAYLOAD
    mock_archive_get.assert_called_once()
    h_args, h_kwargs = mock_archive_get.call_args
    assert h_args[0] == "archive"
    assert h_kwargs["params"]["start_date"] == "2024-07-01"


def test_climate_cache_ttl_and_stale(tmp_path):
    """Verify disk cache respects TTL, handles expiration, and provides stale fallback."""
    cache = ClimateCache(cache_dir=tmp_path)
    key = "test_item"
    payload = {"city": "Pune", "temp": 28.0}

    # Set with 1-second TTL
    cache.set(key, payload, ttl_seconds=1)

    # Immediate retrieval succeeds
    hit = cache.get(key)
    assert hit is not None
    data, age = hit
    assert data["temp"] == 28.0
    assert age >= 0

    # Wait for expiration
    time.sleep(1.1)

    # Normal get returns None
    assert cache.get(key) is None

    # Stale get still retrieves expired data
    stale = cache.get_stale(key)
    assert stale is not None
    stale_data, stale_age = stale
    assert stale_data["temp"] == 28.0
    assert stale_age >= 1.0

    # Clear deletes entry
    cache.clear()
    assert cache.get_stale(key) is None


def test_fetch_live_climate_success(tmp_path):
    """Verify fetch_live_climate parses temperature, humidity, apparent temp, and forecast."""
    cache = ClimateCache(cache_dir=tmp_path)
    mock_client = MagicMock(spec=OpenMeteoClient)
    mock_client.fetch_current_and_forecast.return_value = MOCK_FORECAST_PAYLOAD

    obs = fetch_live_climate(
        latitude=18.5204,
        longitude=73.8567,
        client=mock_client,
        cache=cache,
        use_cache=True,
    )

    # 1. Current metrics
    assert obs.temperature_c == 27.6
    assert obs.relative_humidity_pct == 32.0
    assert obs.apparent_temperature_c == 26.0
    assert obs.precipitation_mm == 0.0
    assert obs.wind_speed_kmh == 9.5
    assert obs.weather_description == "Clear sky"
    assert obs.data_status == "verified_live"
    assert obs.is_live is True
    assert obs.cache_hit is False

    # 2. Daily forecast items
    assert len(obs.daily_forecast) == 3
    day2 = obs.daily_forecast[1]
    assert day2.date == "2026-11-10"
    assert day2.temp_max_c == 31.0
    assert day2.temp_min_c == 17.8
    assert day2.precipitation_sum_mm == 2.5
    assert day2.precipitation_probability_pct == 20

    # 3. Cache verification (second call should hit cache)
    obs_cached = fetch_live_climate(
        latitude=18.5204,
        longitude=73.8567,
        client=mock_client,
        cache=cache,
        use_cache=True,
    )
    assert obs_cached.cache_hit is True
    assert obs_cached.data_status == "cached"
    assert obs_cached.temperature_c == 27.6
    assert mock_client.fetch_current_and_forecast.call_count == 1  # Only called once


def test_fetch_live_climate_fallback_on_network_error(tmp_path):
    """Verify fetch_live_climate gracefully falls back to synthetic observation when API fails."""
    cache = ClimateCache(cache_dir=tmp_path)
    mock_client = MagicMock(spec=OpenMeteoClient)
    mock_client.fetch_current_and_forecast.side_effect = IntegrationError("Network offline")

    obs = fetch_live_climate(
        latitude=18.5204,
        longitude=73.8567,
        client=mock_client,
        cache=cache,
        use_cache=True,
    )

    # Fallback assertions
    assert obs.data_status == "fallback_simulated"
    assert obs.is_live is False
    assert obs.source == "illustrative_fallback"
    assert obs.temperature_c > 0.0
    assert len(obs.daily_forecast) == 7


def test_fetch_live_climate_stale_cache_fallback(tmp_path):
    """Verify stale cache is utilized when API fails and cache has expired."""
    cache = ClimateCache(cache_dir=tmp_path)
    cache_key = f"open_meteo_live_{PUNE_CENTROID_LAT:.4f}_{PUNE_CENTROID_LON:.4f}"
    # Populate cache with zero TTL (immediately expired)
    cache.set(cache_key, MOCK_FORECAST_PAYLOAD, ttl_seconds=-1)

    mock_client = MagicMock(spec=OpenMeteoClient)
    mock_client.fetch_current_and_forecast.side_effect = IntegrationError("503 Service Unavailable")

    obs = fetch_live_climate(
        latitude=PUNE_CENTROID_LAT,
        longitude=PUNE_CENTROID_LON,
        client=mock_client,
        cache=cache,
        use_cache=True,
    )

    # Should use stale cache rather than raw fallback
    assert obs.data_status == "cached"
    assert obs.is_live is False
    assert obs.temperature_c == 27.6
    assert obs.cache_hit is True


def test_fetch_historical_climate_success(tmp_path):
    """Verify historical climate statistical aggregates calculation."""
    cache = ClimateCache(cache_dir=tmp_path)
    mock_client = MagicMock(spec=OpenMeteoClient)
    mock_client.fetch_historical_archive.return_value = MOCK_ARCHIVE_PAYLOAD

    summary = fetch_historical_climate(
        latitude=18.5204,
        longitude=73.8567,
        start_date="2024-07-01",
        end_date="2024-07-04",
        client=mock_client,
        cache=cache,
        use_cache=True,
    )

    assert summary.days_count == 4
    # Total rain = 10.0 + 42.0 + 0.0 + 5.0 = 57.0 mm
    assert summary.total_rainfall_mm == 57.0
    assert summary.max_daily_rainfall_mm == 42.0
    assert summary.mean_daily_rainfall_mm == pytest.approx(14.25, abs=0.01)
    # Tmax = [28.0, 29.5, 39.0, 27.5] -> mean = 31.0
    assert summary.mean_temp_max_c == 31.0
    # Heatwave days (>= 38°C) = 1 (39.0)
    assert summary.heatwave_days == 1
    # Heavy rain days (>= 35.5 mm) = 1 (42.0)
    assert summary.heavy_rain_days == 1
    assert summary.data_status == "verified_historical"
    assert summary.is_live is False


def test_fetch_historical_climate_fallback(tmp_path):
    """Verify fallback historical summary when API fails."""
    cache = ClimateCache(cache_dir=tmp_path)
    mock_client = MagicMock(spec=OpenMeteoClient)
    mock_client.fetch_historical_archive.side_effect = IntegrationError("Archive offline")

    summary = fetch_historical_climate(
        latitude=18.5204,
        longitude=73.8567,
        client=mock_client,
        cache=cache,
        use_cache=True,
    )

    assert summary.data_status == "fallback_simulated"
    assert summary.source == "illustrative_fallback"
    assert summary.total_rainfall_mm == 752.4
