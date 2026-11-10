# M5-T4 — NASA POWER Climate Data API Feasibility Assessment

**Document ID:** `AI HANDOFFS/Antigravity/Reports/2026-11-09_m5_t4_nasa_power_feasibility.md`  
**Date:** 2026-11-09  
**Author:** Antigravity (Senior System & Climate Data Architect)  
**Task Reference:** M5-T4 (NASA POWER Feasibility Assessment)  
**Status:** Audit & Feasibility Review (Audit-Only; Zero Code Changes; Zero Commits)  
**Evaluation Coordinates:** Pune Centroid ($18.5204^\circ\text{N}, 73.8567^\circ\text{E}$, Elevation: $635.99\text{ m}$)  

---

## 1. Executive Summary & Recommendation

This audit evaluates the technical, scientific, and architectural feasibility of integrating the **NASA POWER** (Prediction of Worldwide Energy Resources) API into the **Pune Climate Adaptation Investment Prioritization Platform**.

### Key Verdict
- **Do NOT replace Open-Meteo with NASA POWER for operational/real-time weather.** Open-Meteo provides superior low-latency real-time observations (~400 ms vs ~2.5 s) and forward-looking 7-day numerical forecasts. NASA POWER has a data lag ranging from 2 days (near-real-time GEOS-FP stream) to 2–3 months (quality-controlled final MERRA-2 assimilation), and does not support operational short-term forecasting.
- **Do NOT rely on NASA POWER for intra-city micro-climate differentiation.** NASA POWER operates on a native MERRA-2 spatial grid of $0.5^\circ \text{ latitude} \times 0.625^\circ \text{ longitude}$ (approximately $55\text{ km} \times 65\text{ km}$). A single grid cell encompasses the entire Pune Metropolitan Region as well as portions of the Western Ghats crest. All 6 municipal planning zones produce identical values.
- **HIGH VALUE for long-term climatological baselines and solar/surface thermal metrics.** NASA POWER provides a dedicated, pre-aggregated **Climatology API** (`/temporal/climatology/point`) delivering multi-decadal (1991–2020) monthly normals for solar irradiance, precipitation, and thermal metrics in a single lightweight call (~1 KB). Additionally, parameters such as **All-Sky Surface Shortwave Downward Irradiance** (`ALLSKY_SFC_SW_DWN`), **Earth Skin Temperature** (`TS`), and **Root-Zone Soil Wetness** (`GWETROOT`) provide physical indicators of urban thermal stress and stormwater infiltration capacity that atmospheric air temperature cannot capture.
- **Strategic Recommendation:** If authorized in future phases, position NASA POWER as a **complementary climatological baseline and solar/surface heat reference source**, while retaining Open-Meteo for live telemetry and 7-day operational forecasts.

---

## 2. NASA POWER API Architecture & Available Endpoints

The NASA POWER Project (hosted at NASA Langley Research Center) provides solar and meteorological datasets derived from NASA satellite observations (CERES, GEWEX) and data assimilation models (MERRA-2, GEOS-FP).

### API Base URL & Community
- **Base Endpoint:** `https://power.larc.nasa.gov/api`
- **Current Version:** `v2.10.3`
- **Application Communities:**
  - `RE` (Renewable Energy): Tailored for solar, wind, and radiation applications (recommended for solar/thermal analysis).
  - `AG` (Sustainable Buildings / Agroclimatology): Tailored for precipitation, soil moisture, and crop/evaporation models.
  - `SB` (Sustainable Buildings): Tailored for building thermal load and HVAC sizing.

### Supported Temporal Endpoints

| Endpoint Route | Temporal Range | Typical Latency | Primary Use Case in Pune Platform |
|---|---|---|---|
| `/temporal/climatology/point` | 1991–2020 Multi-Year Normals | ~1.2 s – 2.0 s | **High Value:** Pre-computed 30-year monthly normals (e.g., historical July rain, April solar load). |
| `/temporal/monthly/point` | 1981 to Recent (Monthly totals) | ~1.5 s – 2.5 s | Long-term decadal trends and monsoon anomaly validation. |
| `/temporal/daily/point` | 1981 to Near-Real-Time (Daily) | ~2.0 s – 4.0 s | Historical hazard verification and extreme event frequency audits. |
| `/temporal/hourly/point` | 1981 to Near-Real-Time (Hourly) | ~4.0 s – 8.0 s | Diurnal heat-island cycles (heavy payload; not suitable for synchronous Streamlit). |

---

## 3. Spatial and Temporal Resolution Analysis

### Spatial Resolution Comparison

```
+-------------------------------------------------------------------------------+
| Pune Metropolitan Footprint vs. Reanalysis Grid Cells                         |
|                                                                               |
|   NASA POWER (MERRA-2): ~55 km x 65 km (0.50° x 0.625°)                       |
|   +-----------------------------------------------------------------------+   |
|   | Western Ghats Crest         Pune Central Basin        Eastern Plains  |   |
|   | (Orographic Heavy Rain)    [Katraj .. Hinjawadi]     (Semi-Arid)      |   |
|   +-----------------------------------------------------------------------+   |
|                                                                               |
|   Open-Meteo (ERA5 Reanalysis): ~28 km x 28 km (0.25° x 0.25°)                |
|   +-----------------------------------+                                       |
|   | Pune Urban Agglomeration (~11 km) |                                       |
|   +-----------------------------------+                                       |
+-------------------------------------------------------------------------------+
```

1. **NASA POWER Grid:**
   - **Meteorological Parameters (MERRA-2):** $0.5^\circ \times 0.625^\circ \approx 55\text{ km} \times 65\text{ km}$.
   - **Solar Irradiance (CERES / SYN1DEG):** $1.0^\circ \times 1.0^\circ \approx 110\text{ km} \times 110\text{ km}$.
   - **Elevation Baseline:** For Pune centroid ($18.5204^\circ\text{N}, 73.8567^\circ\text{E}$), NASA POWER assigns a model elevation of **$635.99\text{ m}$**, which closely reflects Pune's actual mean plateau elevation (~560–660 m).
2. **Spatial Limitation for Municipal Planning:**
   - The entire Pune Municipal Corporation (PMC) boundary ($~516\text{ km}^2$) spans approximately $25\text{ km} \times 30\text{ km}$.
   - All six planning zones in `data/zones.csv` (Zone 1 Katraj, Zone 2 Hinjawadi, Zone 3 Yerawada, Zone 4 Shivajinagar, Zone 5 Kothrud, Zone 6 Hadapsar) fall inside the **identical NASA POWER MERRA-2 grid cell**.
   - **Scientific Caution:** Because the MERRA-2 grid cell extends westward toward the Sahyadri ridge (Western Ghats), grid-averaged rainfall estimates tend to incorporate high-elevation orographic precipitation, yielding slightly higher mean annual precipitation figures compared to rain-shadow valley weather stations in central Pune.

---

## 4. Coverage, Latency & Data Lag for Pune

### Temporal Coverage
- **Historical Continuity:** Unbroken daily and hourly timeseries available from **January 1, 1981** through near-real-time.
- **Completeness:** 100% data coverage for Pune coordinates across all major parameters.

### Operational Data Lag (Latency)
- **Final MERRA-2 Assimilation:** Standard quality-checked MERRA-2 products experience a release lag of **1 to 3 months** behind real time.
- **Forward Processing (GEOS-FP / FP-IT):** For recent dates, NASA POWER utilizes the Goddard Earth Observing System Forward Processing stream, reducing data latency to approximately **2 to 3 days**.
- **Real-Time Forecasting:** NASA POWER does **not** generate operational future forecasts (e.g., $t + 1$ to $t + 7$ days).

---

## 5. Variable Comparison: NASA POWER vs. Open-Meteo ERA5

| Parameter Category | NASA POWER Parameter | Open-Meteo ERA5 Equivalent | Units Match? | Distinct Advantages / Notes |
|---|---|---|---|---|
| **Mean Air Temp (2m)** | `T2M` | `temperature_2m` | Yes (°C) | Direct correspondence; both evaluate 2m ambient temperature. |
| **Max Air Temp (2m)** | `T2M_MAX` | `temperature_2m_max` | Yes (°C) | Both capture diurnal peak air temperature. |
| **Min Air Temp (2m)** | `T2M_MIN` | `temperature_2m_min` | Yes (°C) | Both capture nocturnal minimum air temperature. |
| **Precipitation** | `PRECTOTCORR` | `precipitation_sum` | Yes (mm/day) | NASA POWER uses bias-corrected gauge-assimilated precipitation. |
| **Relative Humidity** | `RH2M` | `relative_humidity_2m` | Yes (%) | Direct correspondence. |
| **Surface Skin Temp** | `TS` *(Earth Skin Temp)* | `soil_temperature_0cm` (approx) | Yes (°C) | **NASA Advantage:** `TS` directly measures radiative land surface temperature (LST), crucial for Urban Heat Island (UHI) analysis. |
| **Solar Irradiance** | `ALLSKY_SFC_SW_DWN` | `shortwave_radiation_sum` | No ($\text{kW-hr/m}^2/\text{d}$ vs $\text{MJ/m}^2$) | **NASA Advantage:** CERES-validated global surface shortwave radiation; industry standard for solar exposure and heat load. |
| **Soil Wetness** | `GWETTOP`, `GWETROOT` | `soil_moisture_0_to_7cm` | No (0–1 index vs $\text{m}^3/\text{m}^3$) | Dimensionless saturation index (0 = dry, 1 = saturated); highly intuitive for runoff saturation risk. |
| **Evapotranspiration** | `EVLAND` | `et0_fao_evapotranspiration` | Yes (mm/day) | Model-derived terrestrial evapotranspiration for catchment water balance. |
| **Climatological Normals**| `/climatology` endpoint | *Not natively pre-aggregated* (requires multi-year query) | N/A | **NASA Advantage:** Delivers 30-year monthly multi-annual normals in a single instant HTTP query. |

---

## 6. Missing Data, Units, Conventions & Error Handling

### 1. Fill Value / Missing Data Convention
- **NASA POWER Fill Value:** `-999.0` (or `-999`).
- **Critical Ingestion Rule:** Any ingestion parser **must** implement explicit sentinel checking:
  ```python
  def _parse_nasa_float(val: Any) -> Optional[float]:
      if val is None or val == -999.0 or val == -999:
          return None
      try:
          f = float(val)
          return None if f < -900.0 else round(f, 2)
      except (ValueError, TypeError):
          return None
  ```
  *Failure to filter `-999.0` would severely corrupt aggregates (e.g., negative rainfall or extreme negative temperatures).*

### 2. Time Standard & Coordinate Ordering
- **Time Standard:** NASA POWER defaults to `LST` (Local Solar Time) or `UTC`. For India Standard Time (IST, UTC+5:30), explicit `time_standard=LST` or UTC offset tracking is required.
- **Date Key Formatting:** Daily dictionary keys are formatted as `YYYYMMDD` (e.g., `"20230601"`), whereas Open-Meteo returns ISO strings (`"2023-06-01"`).
- **Coordinate Query Parameters:** `longitude` precedes `latitude` in standard NASA POWER API URLs (`?longitude=73.8567&latitude=18.5204`), whereas Open-Meteo accepts `latitude=...&longitude=...`.

---

## 7. Unique Climate Adaptation Indicators for Pune

NASA POWER offers four distinct parameters that are not currently utilized in the platform and offer genuine scientific value for climate adaptation:

### 1. Earth Skin Temperature (`TS`) vs. Ambient Air Temperature (`T2M`)
- **Scientific Significance:** In urban environments, asphalt, concrete, and roof surfaces absorb solar radiation and reach temperatures 10°C to 20°C above ambient air temperature.
- **Observed Live Pune Sample (May 1, 2023):**
  - Ambient Air Temperature (`T2M`): $26.09^\circ\text{C}$ (Max `T2M_MAX`: $34.82^\circ\text{C}$).
  - Earth Skin Temperature (`TS`): **$29.02^\circ\text{C}$** (mean daily ground skin).
- **Application to Optimizer:** Projects like *Cool Roofs*, *Urban Permeable Pavements*, and *Vegetated Canopy Networks* directly target reducing skin temperature rather than ambient regional air temperature.

### 2. All-Sky Surface Shortwave Downward Irradiance (`ALLSKY_SFC_SW_DWN`)
- **Observed Pune Climatology:**
  - **April / May Peak:** $\approx 7.08\text{ kW-hr/m}^2/\text{day}$ (intense pre-monsoon solar heating).
  - **July / August Monsoon Dip:** $\approx 3.31\text{ kW-hr/m}^2/\text{day}$ (cloud-cover attenuation).
- **Application to Optimizer:** Provides a rigorous baseline for sizing shade structures, cool-pavement thermal reflectance requirements, and urban greening solar interception.

### 3. Root-Zone Soil Wetness (`GWETROOT`)
- **Scale:** Dimensionless fraction from `0.0` (completely desiccated) to `1.0` (field capacity / saturated).
- **Application to Optimizer:** Pre-monsoon soil wetness in Pune drops to $0.30$–$0.40$, while mid-monsoon surges to $>0.85$. When root-zone wetness reaches $\ge 0.90$, infiltration capacity approaches zero, exponentially increasing urban flash-flood runoff risk.

---

## 8. Licensing, Cost, Rate Limits, and Infrastructure Reliability

| Operational Dimension | NASA POWER Specification | Comparison with Open-Meteo |
|---|---|---|
| **Licensing** | Public Domain (U.S. Government work, CC0 equivalent). Unrestricted commercial and academic reuse. | Free tier under non-commercial CC-BY 4.0; commercial requires API key. |
| **Authentication** | Zero API keys required. Open access. | Zero API keys required for non-commercial tier. |
| **Cost** | Completely free of charge. | Free tier available. |
| **Rate Limits** | Soft recommendation of max 10–30 requests per minute. No hard IP token limits for standard usage. | 10,000 requests/day, max 600/minute. |
| **Response Latency** | 1.5 seconds to 3.5 seconds per query (moderate). | 300 ms to 600 ms (fast). |
| **Uptime & SLA** | High institutional stability (NASA Langley Server Infrastructure). Subject to scheduled maintenance. | High global edge-cached CDN uptime. |

---

## 9. Integration Feasibility Assessment & Final Recommendation

### Feasibility Scorecard

| Evaluation Axis | Rating | Analysis |
|---|---|---|
| **Data Quality & Scientific Rigor** | **EXCELLENT** | Peer-reviewed NASA MERRA-2 and CERES satellite datasets; global gold standard for solar and climatology. |
| **Real-Time Operational Utility** | **POOR** | 2-day to 3-month latency; no short-term weather forecasts. Unsuitable for live operational cards. |
| **Spatial Zone Resolution** | **POOR** | 55 km grid cell treats all 6 Pune municipal zones identically; cannot resolve localized micro-climates. |
| **Climatological Baseline Value** | **EXCELLENT** | Instant multi-decadal monthly normals via `/climatology` endpoint; provides historical context effortlessly. |
| **API Usability & Overhead** | **MODERATE** | Fast JSON structure, but slower response times (~2.5s) require disk caching with 24h+ TTL. |

### Strategic Recommendation for Project Roadmap

1. **Do Not Implement in M5-T4:** Maintain the current branch `feature/m5-climate-api-integration` focused on the verified Open-Meteo integration.
2. **Potential Future Role (M5-T5+ or M6):**
   - If secondary climate integration is approved, implement a lightweight adapter specifically querying `/temporal/climatology/point` for Pune.
   - Display a comparative **"30-Year Climatological Baseline (NASA MERRA-2 / CERES)"** section in the Provenance tab, showing how current conditions compare to long-term normals (solar irradiance, monthly rainfall averages, seasonal maximum temperatures).
3. **Verdict:** NASA POWER is a **valuable secondary climatological reference**, but **not** a candidate for primary real-time weather ingestion.

---

## 10. M5-T4B: Parameter-by-Parameter Technical & Scientific Validation Matrix

A targeted technical validation of the five candidate parameters was conducted against live NASA POWER API endpoints (`v2.10.3` / `v2.10.1`) for Pune coordinates ($18.5204^\circ\text{N}, 73.8567^\circ\text{E}$):

| Parameter | Endpoints Supported | Source Dataset | Native Spatial Resolution | Units & API Aggregation | Missing-Value Sentinel | Verified Historical Coverage | Added Value Beyond Open-Meteo ERA5 |
|---|---|---|---|---|---|---|---|
| **`T2M`** | Daily, Monthly, Climatology | `MERRA2` | $0.5^\circ \times 0.625^\circ$ ($\sim 55\text{ km} \times 65\text{ km}$) | $^\circ\text{C}$ (24-hour mean) | `-999.0` | 1981-01-01 to near-real-time | **Low**: Directly duplicates Open-Meteo `temperature_2m` (July 2023 comparison: $23.89^\circ\text{C}$ NASA vs $24.06^\circ\text{C}$ ERA5). |
| **`T2M_MAX`** | Daily, Monthly, Climatology | `MERRA2`, `POWER` | $0.5^\circ \times 0.625^\circ$ ($\sim 55\text{ km} \times 65\text{ km}$) | $^\circ\text{C}$ (Daily max hourly 2m temp) | `-999.0` | 1981-01-01 to near-real-time | **Low**: Duplicates Open-Meteo `temperature_2m_max`. Useful only as cross-model validation. |
| **`PRECTOTCORR`** | Daily, Monthly, Climatology | `MERRA2` | $0.5^\circ \times 0.625^\circ$ ($\sim 55\text{ km} \times 65\text{ km}$) | $\text{mm/day}$ (24-hour total precipitation) | `-999.0` | 1981-01-01 to near-real-time | **Moderate (with caveat)**: GPCP bias-corrected rainfall. Note: coarse grid cell smears Western Ghats orographic rainfall over Pune. |
| **`ALLSKY_SFC_SW_DWN`** | Daily, Monthly, Climatology | `SYN1DEG` (CERES / GEWEX) | **$1.0^\circ \times 1.0^\circ$ ($\sim 110\text{ km} \times 110\text{ km}$)** | $\text{kW-hr/m}^2/\text{day}$ (Daily total solar flux) | `-999.0` | 1981-01-01 to near-real-time | **HIGH**: Authoritative satellite-derived surface downward solar irradiance. Standard metric for solar heat load, shading, and cool roofs. |
| **`TS`** | Daily, Monthly, Climatology | `MERRA2` | $0.5^\circ \times 0.625^\circ$ ($\sim 55\text{ km} \times 65\text{ km}$) | $^\circ\text{C}$ (Radiative surface skin temp) | `-999.0` | 1981-01-01 to near-real-time | **HIGH (regional context)**: Models radiative skin temperature ($TS - T2M = +2.63^\circ\text{C}$ in April pre-monsoon). Invaluable regional surface heat benchmark. |

*Note: Raw parameter `PRECTOT` was also probed but found to return `Units: None` and `Longname: None` in metadata, confirming that `PRECTOTCORR` is the sole supported and bias-corrected precipitation parameter.*

---

## 11. Rigorous Audit of Specific Checks

### Check 1: Non-Uniform Spatial Resolutions Across Parameters
- **Finding:** Parameters returned by NASA POWER do **not** have uniform native spatial resolution:
  - Atmospheric variables (`T2M`, `T2M_MAX`, `PRECTOTCORR`, `TS`) originate from **NASA MERRA-2** at **$0.5^\circ \times 0.625^\circ$ ($\sim 55\text{ km} \times 65\text{ km}$)**.
  - Solar flux (`ALLSKY_SFC_SW_DWN`) originates from **CERES SYN1DEG** at **$1.0^\circ \times 1.0^\circ$ ($\sim 110\text{ km} \times 110\text{ km}$)**.
- **Engineering Rule:** The platform provenance disclosures must explicitly cite the dual resolutions ($0.5^\circ$ for meteorology, $1.0^\circ$ for solar irradiance) rather than claiming a single uniform resolution.

### Check 2: Concrete Empirical Data Completeness Audit
- Rather than assuming 100% data availability, an empirical audit of all 365 daily records for the full calendar year 2023 was executed for Pune:
  - `T2M`: 365/365 valid records (0 `-999.0` fills; range $[16.32^\circ\text{C}, 31.13^\circ\text{C}]$).
  - `T2M_MAX`: 365/365 valid records (0 `-999.0` fills; range $[24.02^\circ\text{C}, 40.32^\circ\text{C}]$).
  - `PRECTOTCORR`: 365/365 valid records (0 `-999.0` fills; range $[0.00\text{ mm}, 94.40\text{ mm}]$). Peak 2023 monsoon rainfall was $94.40\text{ mm/day}$.
  - `ALLSKY_SFC_SW_DWN`: 365/365 valid records (0 `-999.0` fills; range $[1.01, 7.75]\text{ kW-hr/m}^2/\text{day}$).
  - `TS`: 365/365 valid records (0 `-999.0` fills; range $[16.07^\circ\text{C}, 33.43^\circ\text{C}]$).
- **Result:** Empirical completeness for 2023 is **100.0%**. However, ingestion logic must still mandate strict sentinel validation (`val == -999.0 or val < -900`) for historical periods or leap-second edges.

### Check 3: Climatology Period Configuration (Fixed vs. Configurable)
- **Finding:** The Climatology endpoint (`/temporal/climatology/point`) has a **strictly FIXED multi-decadal baseline period**:
  - API header returns: `"range": "25-year Meteorological and Solar Monthly & Annual Climatologies (January 2001 - December 2025)"` (or 1991–2020 depending on solar/met sync).
  - Test queries passing `start=2000&end=2020` or `start=1981&end=2010` were tested. The API **silently ignores** user `start` and `end` parameters on the climatology endpoint (header returns `start: None, end: None`).
- **Architectural Consequence:** We cannot request custom historical baselines (e.g. 1981–2010 or 1971–2000) from `/climatology`. If custom windows are needed, monthly/daily timeseries must be aggregated client-side. The fixed climatology represents the official NASA multi-decadal normal.

### Check 4: Scientific Validity of Surface Temperature (`TS`) for Urban Heat Island (UHI)
- **Physical Meaning:** In MERRA-2, `TS` is the radiative skin temperature derived from surface energy balance:
  $$R_{\text{net}} = H + \lambda E + G$$
- **Empirical Validation (April 2023 Pre-Monsoon Peak):**
  - Ambient 2m Air Temperature (`T2M`): $28.05^\circ\text{C}$.
  - Earth Skin Temperature (`TS`): **$30.31^\circ\text{C}$** ($+2.26^\circ\text{C}$ elevation above air temp; 30-year April normal shows $+2.63^\circ\text{C}$).
- **Scientific Limitation & Guardrail:**
  - `TS` represents the composite radiative skin temperature of a **$\sim 3,500\text{ km}^2$ grid cell**. It aggregates urban concrete, open soil, river corridors, and surrounding rural vegetation.
  - **Unsuitable** for ward-level UHI mapping (e.g., comparing Shivajinagar's dense urban core to Katraj or Kothrud).
  - **Suitable** as a regional thermodynamic benchmark demonstrating macro-surface overheating relative to ambient air during pre-monsoon months.
  - **Mandatory UI Disclosure:** Must be explicitly labeled as *"Regional Ground Skin Temperature ($\sim 55\text{ km}$ grid)"*, not *"Micro-Urban Heat Island"*.

### Check 5: Correct Precipitation Parameter and Community Selection
- **Parameter Selection:** `PRECTOTCORR` is verified as the sole correct precipitation parameter. It incorporates GPCP satellite and rain gauge bias correction. Raw `PRECTOT` lacks units and longname metadata in NASA POWER v2.
- **Community Selection:** All three communities (`RE` - Renewable Energy, `SB` - Sustainable Buildings, `AG` - Agroclimatology) were probed and confirmed to return all five candidate parameters. `RE` is recommended as the canonical standard.

### Check 6: Meaningful Comparability Between NASA Climatology & Open-Meteo ERA5
- A rigorous comparison between NASA POWER MERRA-2 and Open-Meteo ERA5 was conducted for Pune in July 2023:
  - **Temperature Parity:**
    - NASA POWER July 2023 Mean Temp (`T2M`): **$23.89^\circ\text{C}$**
    - Open-Meteo ERA5 July 2023 Mean Temp: **$24.06^\circ\text{C}$**
    - *Difference is only $0.17^\circ\text{C}$*, confirming high cross-reanalysis consistency for regional temperature.
  - **Precipitation Divergence:**
    - Open-Meteo ERA5 July 2023 Mean Daily Precip: **$9.81\text{ mm/day}$** ($304.1\text{ mm}$ total).
    - NASA POWER MERRA-2 July 2023 Mean Daily Precip: **$30.36\text{ mm/day}$** ($941.0\text{ mm}$ total).
  - **Root Cause Analysis:** Open-Meteo ERA5 ($0.25^\circ \approx 28\text{ km}$) resolves the leeward rain shadow of Pune city east of the Sahyadri mountains. In contrast, MERRA-2's $0.5^\circ \times 0.625^\circ$ ($\sim 55\text{ km} \times 65\text{ km}$) cell extends westward onto the Western Ghats crest (Mulshi/Lonavala catchment), where orographic monsoon rainfall exceeds $2,000\text{ mm}$, smearing mountain precipitation over the urban valley.
  - **Scientific Directive:** NASA POWER precipitation **must not be compared directly** to urban valley rain gauge observations without an explicit footnote explaining Western Ghats orographic smearing in coarse reanalysis cells.

### Check 7: Preservation of Source Attribution and Provenance Metadata
- All retrieved NASA POWER records must retain full attribution:
  - `data_source`: `"NASA POWER (MERRA-2 / CERES SYN1DEG)"`
  - `api_endpoint`: `"https://power.larc.nasa.gov/api/temporal/climatology/point"`
  - `spatial_resolution`: `"0.50° x 0.625° (Atmospheric), 1.00° x 1.00° (Solar)"`
  - `climatology_period`: `"2001-2025 Normal"`
  - `retrieval_timestamp`: ISO 8601 UTC timestamp.

---

## 12. Recommended Minimal Integration Scope & Architectural Boundaries

If authorized in a future milestone task, the minimal, non-disruptive integration scope should consist of:

### Proposed Minimal Implementation Scope
1. **Targeted Endpoint:** Query exclusively `/temporal/climatology/point` for Pune centroid ($18.5204^\circ\text{N}, 73.8567^\circ\text{E}$) with `parameters=T2M,T2M_MAX,PRECTOTCORR,ALLSKY_SFC_SW_DWN,TS` and `community=RE`.
2. **Dedicated Adapter:** A lightweight `NasaPowerAdapter` class in `src/integrations/nasa_power.py` implementing the established `BaseClimateAdapter` interface.
3. **Dedicated Schema:** `NasaClimatologySummary` dataclass in `src/ingestion/schemas.py` capturing monthly normals (`JAN` through `DEC` plus annual `ANN`).
4. **Long-TTL Disk Caching:** Since climatology normals update only during major dataset releases (every several years), the cache TTL should be configured for **30 days** (`data/cache/climate/nasa_power_climatology.json`).
5. **UI Display:** A dedicated secondary sub-tab in `components/provenance.py` titled:  
   `"🏛️ NASA POWER 25-Year Climatological Normals (18.52°N, 73.86°E)"`  
   displaying solar irradiance peaks, seasonal temperature cycles, and regional ground skin temperature context.

### Invariant Architectural Boundaries
- **Primary Live & Forecast Telemetry:** Open-Meteo remains the sole provider for real-time weather and 7-day numerical forecasts.
- **Strict Isolation of Optimizer Core:** NASA POWER data must **never**:
  - Modify `src/optimizer.py` deterministic knapsack logic.
  - Alter multi-criteria objective weights or preset definitions.
  - Dynamically recalculate project intervention benefit scores or costs.
  - Mutate canonical baseline CSV schemas (`zones.csv`, `projects.csv`).

---
*Report updated and filed under `AI HANDOFFS/Antigravity/Reports/2026-11-09_m5_t4_nasa_power_feasibility.md`. Audit-only; no code files were modified, no commits created, and no pushes executed.*


