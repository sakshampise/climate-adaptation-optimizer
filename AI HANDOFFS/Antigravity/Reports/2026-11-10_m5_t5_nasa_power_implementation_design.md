# M5-T5: NASA POWER Implementation Design Specification

**Document ID:** `AI HANDOFFS/Antigravity/Reports/2026-11-10_m5_t5_nasa_power_implementation_design.md`  
**Date:** 2026-11-10  
**Author:** Antigravity (Senior System & Climate Data Architect)  
**Task Reference:** M5-T5 (NASA POWER Implementation Design)  
**Status:** Design Specification (Pre-Implementation; Zero Code Changes; Awaiting Approval)  
**Target Coordinates:** Pune Centroid ($18.5204^\circ\text{N}, 73.8567^\circ\text{E}$, Elevation: $635.99\text{ m}$)  

---

## 1. Executive Design Overview & Core Principles

This specification defines the minimal, robust implementation design for integrating **NASA POWER** as a secondary climatological baseline provider for the **Pune Climate Adaptation Investment Prioritization Platform**.

### Core Architectural Principles
1. **Zero Redundancy (No Duplicate Temperature Variables):**
   - The candidate variables `T2M` (Mean Air Temperature) and `T2M_MAX` (Maximum Air Temperature) are **strictly excluded**. Open-Meteo ERA5 already provides superior higher-resolution ($~11\text{ km} \text{ vs } 55\text{ km}$) air temperature telemetry.
   - NASA POWER is integrated exclusively for the **three parameters that add genuine physical and climatological value**:
     1. **`ALLSKY_SFC_SW_DWN`**: Downward solar shortwave irradiance.
     2. **`TS`**: Earth skin / radiative ground surface temperature.
     3. **`PRECTOTCORR`**: Bias-corrected precipitation normal (with explicit Western Ghats orographic footnote).
2. **Dynamic Unit Ingestion (No Hardcoded Units):**
   - NASA POWER returns units dynamically in its top-level `parameters` metadata dictionary. The unit varies by temporal endpoint:
     - `PRECTOTCORR`: `mm/day` in `/climatology` and `/daily`, but `mm/hour` in `/hourly`.
     - `ALLSKY_SFC_SW_DWN`: `kW-hr/m^2/day` in `/climatology` and `/daily`, but `Wh/m^2` in `/hourly`.
     - `TS`: `C` across all endpoints.
   - The adapter will **dynamically parse and bind the units returned by the specific endpoint's response metadata**, preventing unit mismatch bugs.
3. **Strict Optimizer & Policy Invariants:**
   - NASA POWER data is strictly read-only and serves purely as explanatory context.
   - It will **never** modify `src/optimizer.py`, objective weight presets, project benefit scores, or canonical CSV datasets (`zones.csv`, `projects.csv`).
4. **Primary vs. Secondary Responsibilities:**
   - **Open-Meteo**: Sole provider for real-time weather and 7-day municipal forecasts.
   - **NASA POWER**: Secondary provider for multi-decadal climatological normals (2001–2025 baseline).

---

## 2. Parameter Scope, Climatology Periods & Annual Aggregation Semantics

The integration focuses strictly on the three non-redundant parameters queried from the `/temporal/climatology/point` endpoint with `community=RE`. Each parameter retains its specific source dataset, native spatial resolution, verified climatology period, and mathematical aggregation semantics:

| Parameter ID | Parameter Long Name | Source Dataset | Native Grid Resolution | Documented Climatology Period | API Returned Unit | Annual Value (`ANN`) Aggregation Semantics | Added Scientific Value |
|---|---|---|---|---|---|---|---|
| **`ALLSKY_SFC_SW_DWN`** | All Sky Surface Shortwave Downward Irradiance | `SYN1DEG` (CERES satellite & GEWEX SRB) | **$1.00^\circ \times 1.00^\circ$ ($\sim 110\text{ km} \times 110\text{ km}$)** | `January 2001 - December 2025 (25-year)` *(CERES Terra/Aqua period)* | Dynamically extracted (e.g. `kW-hr/m^2/day`) | **Day-weighted mean daily flux** ($\text{kW-hr/m}^2/\text{day}$) across the annual cycle: $\sum (\text{monthly\_mean} \times \text{days}) / 365.25$. Reported: $5.135\text{ kW-hr/m}^2/\text{day}$. | Surface solar heat load baseline for cool roofs, shade corridors, and tree canopy design. |
| **`TS`** | Earth Skin Temperature | `MERRA2` (NASA global reanalysis) | **$0.50^\circ \times 0.625^\circ$ ($\sim 55\text{ km} \times 65\text{ km}$)** | `January 2001 - December 2025 (25-year)` *(Aligned POWER climatology normal)* | Dynamically extracted (e.g. `C`) | **Day-weighted annual mean ground skin temperature** ($^\circ\text{C}$) across the annual cycle: $\sum (\text{monthly\_mean} \times \text{days}) / 365.25$. Reported: $24.61^\circ\text{C}$. | Evaluates regional radiative ground surface heating and macro-surface thermal stress. |
| **`PRECTOTCORR`** | Precipitation Corrected | `MERRA2` (GPCP gauge-adjusted) | **$0.50^\circ \times 0.625^\circ$ ($\sim 55\text{ km} \times 65\text{ km}$)** | `January 2001 - December 2025 (25-year)` *(Aligned POWER climatology normal)* | Dynamically extracted (e.g. `mm/day`) | **Day-weighted mean daily rainfall rate** ($\text{mm/day}$): reported $4.74\text{ mm/day}$. Cumulative annual normal equivalent: $\sum (\text{monthly\_rate} \times \text{days}) \approx 1,729.6\text{ mm/year}$. | Multi-decadal rainfall normal (with explicit Western Ghats orographic smearing footnote). |

### Scientific Guardrail on Temperature Differences
> [!IMPORTANT]
> **Surface-to-Air Temperature Difference vs. Urban Heat Island (UHI):**  
> The difference between Earth Skin Temperature and Ambient 2m Air Temperature ($TS - T2M = +2.63^\circ\text{C}$ in April pre-monsoon) represents the **regional thermodynamic surface-to-air temperature gradient** over a $55\text{ km} \times 65\text{ km}$ grid footprint.  
> It **must not** be described or marketed as a "measured Urban Heat Island (UHI) intensity" or "intra-urban UHI index". UHI measures localized micro-urban thermal anomalies between built city centers and rural reference baselines, which requires high-resolution satellite thermal imagery (e.g. Landsat TIRS or ECOSTRESS at 30m–70m) or urban canopy weather station networks.

---

## 3. Data Schema & Contracts (`src/ingestion/schemas.py`)

Two strongly-typed, immutable dataclasses will be added to `src/ingestion/schemas.py`. Notice that `climatology_period`, `source_dataset`, `native_spatial_resolution`, and `aggregation_semantics` are encapsulated **directly on each individual parameter**, ensuring granular provenance tracking:

```python
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

@dataclass(frozen=True)
class NasaClimatologyParameter:
    """Represents a single climatological parameter with monthly values, units, and granular source metadata."""
    parameter_id: str                          # e.g. "ALLSKY_SFC_SW_DWN"
    long_name: str                             # e.g. "All Sky Surface Shortwave Downward Irradiance"
    units: str                                 # Dynamically extracted from API response metadata
    source_dataset: str                        # e.g. "SYN1DEG" (CERES) vs "MERRA2"
    native_spatial_resolution: str             # "1.00° x 1.00°" vs "0.50° x 0.625°"
    climatology_period: str                    # Parameter-specific baseline (e.g. "January 2001 - December 2025")
    aggregation_semantics: str                 # "Day-weighted daily mean flux" vs "Day-weighted daily mean rate"
    monthly_values: Dict[str, Optional[float]] # {"JAN": 4.989, ... "DEC": 4.665}
    annual_value: Optional[float]              # e.g. 5.135 (from "ANN")

@dataclass(frozen=True)
class NasaClimatologySummary:
    """Multi-decadal climatological baseline summary for Pune from NASA POWER."""
    solar_irradiance: NasaClimatologyParameter    # ALLSKY_SFC_SW_DWN
    surface_temperature: NasaClimatologyParameter # TS
    precipitation: NasaClimatologyParameter       # PRECTOTCORR
    
    # Root Metadata & Provenance
    source: str                                   # "NASA POWER (MERRA-2 / CERES SYN1DEG)"
    latitude: float                               # 18.5204
    longitude: float                              # 73.8567
    elevation_m: float                            # 635.99
    data_status: str                              # "verified_live" | "cached" | "fallback_simulated"
    retrieval_timestamp: str                      # ISO 8601 UTC timestamp
    provenance_note: str = field(
        default=(
            "Climatological normals are derived from NASA POWER v2.10 multi-decadal baselines. "
            "Solar products utilize CERES SYN1DEG at 1.00° resolution; meteorological products "
            "utilize MERRA-2 at 0.50° x 0.625° resolution. Does not modify optimizer portfolio selection."
        )
    )
```

---

## 4. Adapter & Ingestion Architecture (`src/integrations/nasa_power.py` & `src/ingestion/fetch.py`)

### 4.1. NASA POWER Adapter Class (`src/integrations/nasa_power.py`)

Inherits from `BaseClimateAdapter` (`src/integrations/base.py`) to maintain unified timeout, retry, and error logging standards:

```python
"""NASA POWER API client adapter conforming to BaseClimateAdapter interface."""

from typing import Dict, Any, List
from src.integrations.base import BaseClimateAdapter, IntegrationError

class NasaPowerAdapter(BaseClimateAdapter):
    BASE_URL = "https://power.larc.nasa.gov/api"
    
    def __init__(self, timeout: float = 12.0, max_retries: int = 2):
        super().__init__(
            base_url=self.BASE_URL,
            source_name="NASA POWER",
            timeout=timeout,
            max_retries=max_retries,
        )

    def get_climatology(
        self,
        lat: float,
        lon: float,
        parameters: List[str],
        community: str = "RE",
    ) -> Dict[str, Any]:
        """Fetch multi-decadal climatology normals for a geographic point."""
        endpoint = "/temporal/climatology/point"
        params = {
            "parameters": ",".join(parameters),
            "community": community,
            "longitude": lon,
            "latitude": lat,
            "format": "JSON",
        }
        return self.get(endpoint, params=params)
```

### 4.2. Parsing with Dynamic Units and Sentinel Filtering (`src/ingestion/fetch.py`)

```python
MONTH_KEYS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# Parameter-specific source datasets, native resolutions, and aggregation semantics
NASA_PARAMETER_METADATA_SPEC = {
    "ALLSKY_SFC_SW_DWN": {
        "source_dataset": "SYN1DEG (CERES / GEWEX)",
        "native_spatial_resolution": "1.00° x 1.00° (~110 km)",
        "aggregation_semantics": "Day-weighted mean daily downward solar flux (kW-hr/m²/day)",
    },
    "TS": {
        "source_dataset": "MERRA2",
        "native_spatial_resolution": "0.50° x 0.625° (~55 km)",
        "aggregation_semantics": "Day-weighted annual mean ground skin temperature (°C)",
    },
    "PRECTOTCORR": {
        "source_dataset": "MERRA2 (GPCP-adjusted)",
        "native_spatial_resolution": "0.50° x 0.625° (~55 km)",
        "aggregation_semantics": "Day-weighted mean daily precipitation rate (mm/day); annual sum ~1,730 mm/year",
    },
}

def _safe_nasa_float(val: Any) -> Optional[float]:
    """Parse numeric float while strictly filtering NASA -999.0 fill values."""
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
    
    # DYNAMIC UNIT EXTRACTION: never assume static unit string
    units = param_meta.get("units", "unknown")
    long_name = param_meta.get("longname", param_id)
    
    # Documented climatology period from header range (fallback to documented standard)
    climatology_period = header_info.get("range", "January 2001 - December 2025 (25-year)")
    
    param_data = raw_props.get("parameter", {}).get(param_id, {})
    
    monthly_vals = {}
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
```

---

## 5. Caching Strategy (`src/ingestion/cache.py`)

Climatological normals are static multi-decadal aggregates that update only upon major dataset re-releases (once every several years).

1. **Cache Key & Directory:**
   - Path: `data/cache/climate/nasa_power_climatology.json`
2. **Cache TTL:**
   - **30 days** ($2,592,000\text{ seconds}$).
3. **Atomic Temporary File Writes:**
   - Utilizes `tempfile.mkstemp` and `os.replace` to prevent race conditions and Windows `WinError 32` file locking collisions.
4. **Three-Tier Fallback Strategy:**
   - **Tier 1 (Fresh Cache):** If cache is $< 30$ days old, serve immediately ($< 5\text{ ms}$).
   - **Tier 2 (Stale Cache on Outage):** If NASA POWER API is unreachable, serve existing cache regardless of age with `data_status="cached"` and stale warning.
   - **Tier 3 (Simulated Offline Fallback):** If no cache file exists on disk and network is down, serve verified offline synthetic climatology fixture clearly tagged `(Simulated)`.

---

## 6. Provenance & UI Presentation Design (`components/provenance.py`)

A new tab will be added to the Provenance component in `components/provenance.py`:

```
+---------------------------------------------------------------------------------------------------+
| 🏛️ Regional Climatology (NASA POWER)                                                             |
| Status: 🟢 Live 25-Year Climatology (January 2001 - December 2025)                                 |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [☀️ Solar Irradiance Peak]       [🔥 Surface Skin Temp Peak]       [🌧️ Annual Rainfall Normal]    |
|  7.08 kW-hr/m²/day (April)         31.56 °C (April Mean Skin)       1,730 mm/year (Annual Normal) |
|  Pre-monsoon solar loading         +2.63 °C above 2m air temp       *Subject to orographic smear* |
|  Source: CERES SYN1DEG (1.0°)      Source: MERRA-2 (0.50°x0.625°)   Source: MERRA-2 (0.50°x0.625°)|
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
| ℹ️ Scientific & Spatial Disclosures:                                                              |
| • Spatial Resolution: Surface Temp & Rainfall at ~55 km grid; Solar Irradiance at ~110 km grid.   |
| • Surface-to-Air Temperature Gradient: The +2.63 °C difference reflects regional thermodynamic   |
|   ground surface heating across a ~3,500 km² mixed rural/urban cell. It is NOT a measured Urban   |
|   Heat Island (UHI) intensity; intra-urban micro-climate UHI requires high-resolution sensing.    |
| • Precipitation Note: MERRA-2 grid cell extends westward into Western Ghats crest, smearing mountain |
|   orographic rainfall over urban valley baseline.                                                 |
| • Integration Boundary: Purely informational reference; does not modify optimizer scoring.        |
+---------------------------------------------------------------------------------------------------+
```

---

## 7. Verification & Automated Test Strategy (`tests/test_nasa_power.py`)

A dedicated automated test suite comprising 10 unit and edge-case tests will be introduced:

1. **`test_nasa_power_adapter_contract`**: Verifies adapter initializes with base URL, timeout, and parameters.
2. **`test_dynamic_unit_binding_climatology`**: Verifies dynamic parsing extracts `kW-hr/m^2/day`, `C`, and `mm/day` directly from climatology metadata.
3. **`test_dynamic_unit_binding_hourly_adaptation`**: Verifies that if hourly data is fed, units dynamically switch to `Wh/m^2` and `mm/hour` without parser crash.
4. **`test_parameter_level_provenance_metadata`**: Asserts each `NasaClimatologyParameter` independently stores its verified `climatology_period`, `source_dataset`, `native_spatial_resolution`, and `aggregation_semantics`.
5. **`test_safe_float_missing_sentinel`**: Validates `-999.0` and `-999` are converted to `None` while valid values like `0.0` or `31.5` are preserved.
6. **`test_climatology_cache_atomic_write`**: Asserts unique temp file creation and atomic rename without orphaned `.tmp` files.
7. **`test_stale_cache_outage_recovery`**: Verifies that when network fails, expired cache is served with `data_status="cached"`.
8. **`test_simulated_fallback_tagged`**: Asserts fallback payload is generated with `data_status="fallback_simulated"`.
9. **`test_surface_to_air_gradient_labeling`**: Verifies UI helper texts accurately label `TS - T2M` as regional surface-to-air temperature differences rather than measured UHI.
10. **`test_optimizer_isolation_contract`**: Verifies `src/optimizer.py` and `solve_portfolio` have zero imports or runtime dependencies on NASA POWER.

---

## 8. Summary of Files Created & Modified (M5-T6 Implementation)

| Target File | Change Type | Purpose |
|---|---|---|
| `src/integrations/nasa_power.py` | New file | `NasaPowerClient` implementing resilient HTTP client for NASA POWER Climatology endpoint. |
| `src/integrations/__init__.py` | Modified | Export `NasaPowerClient`. |
| `src/ingestion/schemas.py` | Modified | `NasaClimatologyParameter` and `NasaClimatologySummary` dataclasses with granular parameter provenance. |
| `src/ingestion/fetch.py` | Modified | Dynamic unit parser, sentinel filter, fallback generator, and `fetch_nasa_climatology()`. |
| `src/ingestion/__init__.py` | Modified | Export `fetch_nasa_climatology`, `NasaClimatologySummary`, `NasaClimatologyParameter`. |
| `components/provenance.py` | Modified | `render_nasa_climatology_card` and optional climatology tab in `render_dataset_tabs()`. |
| `components/__init__.py` | Modified | Export `render_nasa_climatology_card`. |
| `tests/test_nasa_power.py` | New test file | 14 comprehensive unit, edge-case, and optimizer isolation tests. |

---

## 9. M5-T6 Implementation & Verification Report

### 1. Actual Files Implemented
All 8 components from the approved design scope were implemented without altering optimizer mathematics, weights, or canonical CSV fixtures:
- Client adapter: [`src/integrations/nasa_power.py`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/src/integrations/nasa_power.py)
- Domain contracts: [`src/ingestion/schemas.py`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/src/ingestion/schemas.py#L115-L195)
- Orchestration & caching: [`src/ingestion/fetch.py`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/src/ingestion/fetch.py#L420-L635)
- Presentation & disclosures: [`components/provenance.py`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/components/provenance.py#L145-L245)
- Automated verification: [`tests/test_nasa_power.py`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/tests/test_nasa_power.py)

### 2. Live API Response Evidence (Pune Centroid: 18.5204°N, 73.8567°E)
- **Endpoint**: `https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN,TS,PRECTOTCORR&community=RE&longitude=73.8567&latitude=18.5204&format=JSON`
- **Dynamic Units Extracted**:
  - `ALLSKY_SFC_SW_DWN`: `"kW-hr/m^2/day"` (Peak April: $7.078$, May: $7.017$, Annual Mean: $5.135$)
  - `TS`: `"C"` (Peak April: $31.56^\circ\text{C}$, May: $31.59^\circ\text{C}$, Annual Mean: $24.61^\circ\text{C}$)
  - `PRECTOTCORR`: `"mm/day"` (Peak July: $16.61\text{ mm/day}$, Annual Mean: $4.74\text{ mm/day}$, Annual Cumulative: $\sim 1,729.6\text{ mm/year}$)
- **Missing Value Sentinel Handling**: Empirically verified converting `-999.0` and `-999` sentinels to `None` without polluting calculations.

### 3. Automated Test Suite Execution Results
```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: C:\Users\saksh\OneDrive\Documents\Desktop\pccoe indradhanu
plugins: anyio-4.10.0
collected 114 items

tests\test_data_loader.py .........                                      [  7%]
tests\test_explanations.py ..                                            [  9%]
tests\test_integration.py ..                                             [ 11%]
tests\test_nasa_power.py ..............                                  [ 23%]
tests\test_open_meteo.py ................                                [ 37%]
tests\test_optimizer.py .........                                        [ 45%]
tests\test_ui_equivalence.py ........................................... [ 83%]
...........                                                              [ 92%]
tests\test_ui_regression.py ........                                     [100%]

============================= 114 passed in 5.75s =============================
```
- **14/14 new NASA POWER tests passed** in `tests/test_nasa_power.py`.
- **100/100 existing unit, equivalence, regression, and Open-Meteo tests passed**.
- **Total: 114/114 passing** with zero failures or regressions.

### 4. Remaining Scientific & Operational Limitations
1. **Spatial Resolution**: NASA POWER parameters operate at coarse spatial scales ($1.0^\circ \approx 110\text{ km}$ for solar; $0.5^\circ \approx 55\text{ km}$ for skin temp and rain) encompassing the entire municipal territory. Intra-city ward comparisons are not supported.
2. **Orographic Rainfall Smearing**: The $55\text{ km}$ MERRA-2 cell extends into the Western Ghats crest, producing higher annual precipitation totals than urban valley gauges.
3. **Surface-to-Air Gradient vs. UHI**: The elevation of Earth Skin Temperature above ambient air ($+2.63^\circ\text{C}$ in April) represents a regional surface thermodynamic difference, not a micro-urban heat island measurement.

### 5. Git Commit & Branch Status
- **Branch**: `feature/m5-climate-api-integration`
- **Commit Hash**: `0d84684` (`feat(integrations): implement NASA POWER climatology integration for solar, surface temp, and precipitation (M5-T6)`)
- **Git Push Status**: Committed locally; **not pushed** to remote pending project lead review.
- **Working Tree**: Clean on `feature/m5-climate-api-integration`.


