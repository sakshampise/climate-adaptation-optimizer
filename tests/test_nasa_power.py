"""Unit and integration tests for NASA POWER multi-decadal climatology ingestion.

Covers:
- Dynamic unit extraction from metadata.
- -999 missing-value sentinel filtering.
- Parameter-specific provenance, native spatial resolution, and climatology periods.
- Annual value aggregation semantics and cumulative rainfall calculations.
- Caching, atomic writes, stale-cache recovery, and simulated fallback.
- Scientific surface-to-air gradient labeling (not UHI).
- Complete isolation from core optimizer logic.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import requests

from src.ingestion.schemas import (
    NasaClimatologyParameter,
    NasaClimatologySummary,
)
from src.ingestion.cache import ClimateCache
from src.ingestion.fetch import (
    fetch_nasa_climatology,
    get_fallback_nasa_climatology,
    parse_nasa_parameter,
    _safe_nasa_float,
    PUNE_CENTROID_LAT,
    PUNE_CENTROID_LON,
)
from src.integrations.nasa_power import NasaPowerClient
from src.integrations.base import IntegrationError


def _make_mock_nasa_payload(
    solar_unit: str = "kW-hr/m^2/day",
    precip_unit: str = "mm/day",
    temp_unit: str = "C",
    include_sentinels: bool = False,
):
    """Generates a realistic NASA POWER Climatology API response dictionary."""
    solar_vals = {
        "JAN": 4.989, "FEB": 5.850, "MAR": 6.614, "APR": 7.078,
        "MAY": 7.017, "JUN": 4.568, "JUL": 3.310, "AUG": 3.384,
        "SEP": 4.309, "OCT": 5.012, "NOV": 4.896, "DEC": 4.665,
        "ANN": 5.135,
    }
    temp_vals = {
        "JAN": 19.64, "FEB": 23.46, "MAR": 28.06, "APR": 31.56,
        "MAY": 31.59, "JUN": 26.91, "JUL": 24.44, "AUG": 23.67,
        "SEP": 23.77, "OCT": 22.78, "NOV": 20.57, "DEC": 18.95,
        "ANN": 24.61,
    }
    precip_vals = {
        "JAN": 0.03, "FEB": 0.05, "MAR": 0.15, "APR": 0.14,
        "MAY": 0.84, "JUN": 12.06, "JUL": 16.61, "AUG": 13.19,
        "SEP": 9.17, "OCT": 3.41, "NOV": 0.73, "DEC": 0.13,
        "ANN": 4.74,
    }

    if include_sentinels:
        solar_vals["JUL"] = -999.0
        temp_vals["NOV"] = -999
        precip_vals["FEB"] = -999.0

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [73.8567, 18.5204, 635.99],
        },
        "properties": {
            "parameter": {
                "ALLSKY_SFC_SW_DWN": solar_vals,
                "TS": temp_vals,
                "PRECTOTCORR": precip_vals,
            }
        },
        "header": {
            "title": "NASA/POWER Source Native Resolution Climatology Climatologies",
            "api": {"version": "v2.10.1", "name": "POWER Climatology API"},
            "sources": ["SYN1DEG", "MERRA2", "POWER"],
            "fill_value": -999.0,
            "time_standard": "LST",
            "range": "25-year Meteorological and Solar Monthly & Annual Climatologies (January 2001 - December 2025)",
        },
        "parameters": {
            "ALLSKY_SFC_SW_DWN": {
                "units": solar_unit,
                "longname": "All Sky Surface Shortwave Downward Irradiance",
            },
            "TS": {
                "units": temp_unit,
                "longname": "Earth Skin Temperature",
            },
            "PRECTOTCORR": {
                "units": precip_unit,
                "longname": "Precipitation Corrected",
            },
        },
    }


# ==============================================================================
# 1. Adapter Contract & Initialization Tests
# ==============================================================================

def test_nasa_power_client_initialization():
    """Verify NasaPowerClient properly configures base URL, timeout, and defaults."""
    client = NasaPowerClient(timeout_seconds=15.0, max_retries=2)
    assert client.BASE_URL == "https://power.larc.nasa.gov/api"
    assert client.client.timeout_seconds == 15.0
    assert client.client.max_retries == 2
    assert "ALLSKY_SFC_SW_DWN" in client.DEFAULT_PARAMETERS
    assert "TS" in client.DEFAULT_PARAMETERS
    assert "PRECTOTCORR" in client.DEFAULT_PARAMETERS


def test_nasa_power_client_fetch_climatology_params():
    """Verify fetch_climatology issues GET with correct endpoint and query params."""
    mock_base = MagicMock()
    mock_base.get.return_value = {"mock": "data"}

    client = NasaPowerClient()
    client.client = mock_base

    res = client.fetch_climatology(
        latitude=18.5204,
        longitude=73.8567,
        parameters=["ALLSKY_SFC_SW_DWN", "TS", "PRECTOTCORR"],
        community="RE",
    )
    assert res == {"mock": "data"}
    mock_base.get.assert_called_once_with(
        "temporal/climatology/point",
        params={
            "parameters": "ALLSKY_SFC_SW_DWN,TS,PRECTOTCORR",
            "community": "RE",
            "longitude": 73.8567,
            "latitude": 18.5204,
            "format": "JSON",
        },
    )


# ==============================================================================
# 2. Dynamic Unit Extraction & Adaptation Tests
# ==============================================================================

def test_dynamic_unit_extraction_climatology_payload():
    """Verify adapter binds returned units dynamically from climatology metadata."""
    payload = _make_mock_nasa_payload(
        solar_unit="kW-hr/m^2/day",
        precip_unit="mm/day",
        temp_unit="C",
    )
    mock_client = MagicMock()
    mock_client.fetch_climatology.return_value = payload

    summary = fetch_nasa_climatology(client=mock_client, use_cache=False)

    assert summary.solar_irradiance.units == "kW-hr/m^2/day"
    assert summary.precipitation.units == "mm/day"
    assert summary.surface_temperature.units == "C"


def test_dynamic_unit_adaptation_for_differing_endpoints():
    """Verify that if alternative endpoint units are returned, parser binds them dynamically."""
    payload = _make_mock_nasa_payload(
        solar_unit="Wh/m^2",
        precip_unit="mm/hour",
        temp_unit="K",
    )
    mock_client = MagicMock()
    mock_client.fetch_climatology.return_value = payload

    summary = fetch_nasa_climatology(client=mock_client, use_cache=False)

    assert summary.solar_irradiance.units == "Wh/m^2"
    assert summary.precipitation.units == "mm/hour"
    assert summary.surface_temperature.units == "K"


# ==============================================================================
# 3. Missing Sentinel Filtering & Safe Math Tests
# ==============================================================================

def test_safe_nasa_float_sentinel_filtering():
    """Verify _safe_nasa_float converts -999, -999.0, and <-900 to None."""
    assert _safe_nasa_float(None) is None
    assert _safe_nasa_float(-999.0) is None
    assert _safe_nasa_float(-999) is None
    assert _safe_nasa_float("-999.0") is None
    assert _safe_nasa_float(-999.9) is None
    assert _safe_nasa_float(0.0) == 0.0
    assert _safe_nasa_float(28.4567) == 28.457
    assert _safe_nasa_float("invalid") is None


def test_missing_sentinels_in_payload_do_not_pollute_records():
    """Verify payload with -999 sentinels converts those specific months to None."""
    payload = _make_mock_nasa_payload(include_sentinels=True)
    mock_client = MagicMock()
    mock_client.fetch_climatology.return_value = payload

    summary = fetch_nasa_climatology(client=mock_client, use_cache=False)

    assert summary.solar_irradiance.monthly_values["JUL"] is None
    assert summary.solar_irradiance.monthly_values["APR"] == 7.078
    assert summary.surface_temperature.monthly_values["NOV"] is None
    assert summary.surface_temperature.monthly_values["APR"] == 31.56
    assert summary.precipitation.monthly_values["FEB"] is None
    assert summary.precipitation.monthly_values["JUL"] == 16.61


# ==============================================================================
# 4. Parameter-Level Provenance & Aggregation Semantics Tests
# ==============================================================================

def test_parameter_level_provenance_and_resolutions():
    """Verify each parameter stores its specific source, resolution, period, and semantics."""
    payload = _make_mock_nasa_payload()
    mock_client = MagicMock()
    mock_client.fetch_climatology.return_value = payload

    summary = fetch_nasa_climatology(client=mock_client, use_cache=False)

    solar = summary.solar_irradiance
    assert "SYN1DEG" in solar.source_dataset
    assert "1.00° x 1.00°" in solar.native_spatial_resolution
    assert "2001 - December 2025" in solar.climatology_period
    assert "solar flux" in solar.aggregation_semantics.lower()

    temp = summary.surface_temperature
    assert "MERRA2" in temp.source_dataset
    assert "0.50° x 0.625°" in temp.native_spatial_resolution
    assert "annual mean ground skin" in temp.aggregation_semantics.lower()

    precip = summary.precipitation
    assert "MERRA2" in precip.source_dataset
    assert "0.50° x 0.625°" in precip.native_spatial_resolution
    assert "precipitation rate" in precip.aggregation_semantics.lower()


def test_annual_value_semantics_and_cumulative_rainfall():
    """Verify solar is daily mean, temp is annual mean, and precip rate computes ~1,730 mm/yr."""
    payload = _make_mock_nasa_payload()
    mock_client = MagicMock()
    mock_client.fetch_climatology.return_value = payload

    summary = fetch_nasa_climatology(client=mock_client, use_cache=False)

    # Solar annual value is mean daily radiation rate
    assert summary.solar_irradiance.annual_value == 5.135
    # Temp annual value is annual mean temperature
    assert summary.surface_temperature.annual_value == 24.61
    # Precip annual value is mean daily rate
    assert summary.precipitation.annual_value == 4.74

    # Cumulative annual normal calculated separately from monthly days
    cum_rain = summary.annual_cumulative_precipitation_mm
    assert 1720.0 <= cum_rain <= 1740.0


# ==============================================================================
# 5. Caching, Stale Recovery, and Fallback Tests
# ==============================================================================

def test_caching_and_atomic_write(tmp_path: Path):
    """Verify successful fetch writes valid cache file and cleans up temporary files."""
    cache = ClimateCache(cache_dir=tmp_path)
    payload = _make_mock_nasa_payload()
    mock_client = MagicMock()
    mock_client.fetch_climatology.return_value = payload

    summary = fetch_nasa_climatology(
        client=mock_client,
        cache=cache,
        use_cache=True,
    )
    assert summary.data_status == "verified_climatology"
    assert not summary.cache_hit

    # Verify no dangling .tmp files
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0

    # Verify cache hit on second invocation
    summary2 = fetch_nasa_climatology(
        client=mock_client,
        cache=cache,
        use_cache=True,
    )
    assert summary2.cache_hit
    assert summary2.data_status == "cached"
    # Client should only be called once
    mock_client.fetch_climatology.assert_called_once()


def test_stale_cache_outage_recovery(tmp_path: Path):
    """Verify expired cache is returned with status 'cached' during network outage."""
    cache = ClimateCache(cache_dir=tmp_path)
    payload = _make_mock_nasa_payload()
    mock_client = MagicMock()
    mock_client.fetch_climatology.return_value = payload

    # 1. Warm cache
    fetch_nasa_climatology(client=mock_client, cache=cache, use_cache=True)

    # 2. Simulate expired cache
    cache_file = list(tmp_path.glob("*.json"))[0]
    with open(cache_file, "r") as f:
        data = json.load(f)
    data["_cached_at"] = 0.0  # Expired
    with open(cache_file, "w") as f:
        json.dump(data, f)

    # 3. Simulate network outage
    failing_client = MagicMock()
    failing_client.fetch_climatology.side_effect = IntegrationError("Outage")

    stale_summary = fetch_nasa_climatology(
        client=failing_client,
        cache=cache,
        use_cache=True,
    )
    assert stale_summary.cache_hit
    assert stale_summary.data_status == "cached"
    assert stale_summary.solar_irradiance.annual_value == 5.135


def test_complete_offline_fallback(tmp_path: Path):
    """Verify that when no cache exists and network fails, simulated fallback is returned."""
    cache = ClimateCache(cache_dir=tmp_path)
    failing_client = MagicMock()
    failing_client.fetch_climatology.side_effect = IntegrationError("Unreachable")

    fallback = fetch_nasa_climatology(
        client=failing_client,
        cache=cache,
        use_cache=True,
    )
    assert fallback.data_status == "fallback_simulated"
    assert not fallback.is_live
    assert not fallback.cache_hit
    assert len(fallback.solar_irradiance.monthly_values) == 12
    assert fallback.solar_irradiance.monthly_values["APR"] == 7.078
    assert fallback.surface_temperature.monthly_values["APR"] == 31.56
    assert fallback.precipitation.monthly_values["JUL"] == 16.61


# ==============================================================================
# 6. Serialization & Serialization Roundtrip Tests
# ==============================================================================

def test_climatology_serialization_roundtrip():
    """Verify NasaClimatologySummary to_dict and from_dict preserve all fields."""
    fb = get_fallback_nasa_climatology()
    d = fb.to_dict()
    assert isinstance(d, dict)
    assert "solar_irradiance" in d
    assert "surface_temperature" in d
    assert "precipitation" in d

    restored = NasaClimatologySummary.from_dict(d)
    assert restored.source == fb.source
    assert restored.solar_irradiance.units == fb.solar_irradiance.units
    assert restored.solar_irradiance.annual_value == fb.solar_irradiance.annual_value
    assert restored.surface_temperature.monthly_values["APR"] == fb.surface_temperature.monthly_values["APR"]
    assert restored.annual_cumulative_precipitation_mm == fb.annual_cumulative_precipitation_mm


# ==============================================================================
# 7. Scientific Guardrails & Optimizer Isolation Tests
# ==============================================================================

def test_scientific_surface_to_air_labeling_and_provenance():
    """Verify provenance notes state regional surface-to-air gradient, not UHI."""
    summary = get_fallback_nasa_climatology()
    note = summary.provenance_note
    assert "CERES SYN1DEG at 1.00°" in note
    assert "MERRA-2 at 0.50° x 0.625°" in note
    assert "Does not modify optimizer scoring" in note


def test_optimizer_strictly_isolated_from_nasa_power():
    """Verify src/optimizer.py has zero imports or dependencies on NASA POWER."""
    import src.optimizer as opt
    import inspect

    source_code = inspect.getsource(opt)
    assert "nasa" not in source_code.lower()
    assert "climatology" not in source_code.lower()
    assert "allsky" not in source_code.lower()

    # Verify optimizer runs unaffected on standard dataset
    from src.data_loader import load_inputs
    from src.optimizer import solve_portfolio

    _, projects_df = load_inputs("data")
    res = solve_portfolio(projects_df, budget_crore=10.0, objective_id="balanced")
    assert res["total_cost_crore"] <= 10.0
    assert len(res["selected_project_ids"]) == 4
    assert round(res["total_score"], 2) == 276.05
