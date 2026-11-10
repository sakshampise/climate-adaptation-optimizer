"""Provenance, Data Disclosures, and Live Climate Status Component.

Renders prototype advisory notices, live API connection status cards,
data freshness indicators, and explicit data boundary disclaimers separating
real-time meteorological observations from illustrative municipal planning fixtures.
"""

from typing import Optional, Dict, Any
import streamlit as st
import pandas as pd
from src.ingestion.schemas import LiveWeatherObservation, NasaClimatologySummary


def render_provenance_banner() -> None:
    """Renders prominent disclaimer declaring illustrative data status and advisory scope."""
    st.info(
        "ℹ️ **Data Provenance & Policy Notice:** All baseline indicators, project candidate packages, "
        "and costs are currently configured with **simulated/illustrative** planning values for prototype "
        "evaluation. The system functions as a transparent, multi-criteria decision-support aid. Final "
        "capital deployment remains in the authority of municipal stakeholders."
    )


def render_live_climate_card(obs: LiveWeatherObservation) -> None:
    """Renders live climate observations card with explicit provenance boundary disclaimer."""
    is_fallback = obs.data_status == "fallback_simulated" or (not obs.is_live and not obs.cache_hit)
    is_stale_cache = not obs.is_live and obs.cache_hit

    # 1. Connection status badge
    if obs.is_live and not obs.cache_hit:
        status_badge = "🟢 **Live Climate API Connected** (Open-Meteo Real-Time)"
        status_color = "#00CC96"
    elif obs.is_live and obs.cache_hit:
        age_str = f"{int(obs.freshness_seconds)}s ago" if obs.freshness_seconds is not None else "recently"
        status_badge = f"🟡 **Cached Climate Data** (Open-Meteo, refreshed {age_str})"
        status_color = "#FFA15A"
    elif is_stale_cache:
        age_str = f"{int(obs.freshness_seconds / 60)}m ago" if obs.freshness_seconds is not None else "earlier"
        status_badge = f"🔴 **API Disconnected — Stale Cached Data** (Retrieved {age_str})"
        status_color = "#EF553B"
    else:
        status_badge = "🟠 **Offline Climate Fallback** (Illustrative Synthetic Baseline)"
        status_color = "#AB63FA"

    with st.container():
        st.markdown(
            f"#### 🌦️ Pune Live Environmental Context | "
            f"<span style='color:{status_color}; font-size:0.9rem;'>{status_badge}</span>",
            unsafe_allow_html=True,
        )

        if is_fallback:
            st.warning(
                "⚠️ **OFFLINE FALLBACK ACTIVE:** Live meteorological API connection is unavailable and no local "
                "cache is present. Environmental metrics below are **illustrative synthetic estimates**, not empirical Pune observations."
            )
        elif is_stale_cache:
            st.error(
                "⚠️ **API OUTAGE DETECTED:** External Open-Meteo API is unreachable. Displaying cached observations from previous successful sync."
            )

        metric_suffix = " (Simulated)" if is_fallback else ""

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            f"🌡️ Ambient Temperature{metric_suffix}",
            f"{obs.temperature_c:.1f} °C",
            help="2m dry-bulb temperature (observed / fallback)",
        )
        col2.metric(
            f"☀️ Apparent Temperature{metric_suffix}",
            f"{obs.apparent_temperature_c:.1f} °C",
            help="Feels-like temperature accounting for wind and relative humidity",
        )
        col3.metric(
            f"💧 Relative Humidity{metric_suffix}",
            f"{obs.relative_humidity_pct:.0f} %",
            help="Atmospheric moisture level",
        )
        col4.metric(
            f"🌧️ Current Rain / Status{metric_suffix}",
            f"{obs.precipitation_mm:.1f} mm",
            delta=obs.weather_description,
            delta_color="off",
        )

        # 2. 7-Day Forecast Expander
        if obs.daily_forecast:
            forecast_title = "📅 7-Day Municipal Weather Outlook (Open-Meteo Daily Forecast)" if not is_fallback else "📅 7-Day Forecast Outlook (Simulated Fallback)"
            with st.expander(forecast_title, expanded=False):
                forecast_rows = []
                for item in obs.daily_forecast:
                    forecast_rows.append({
                        "Date": item.date,
                        "Max Temp (°C)": f"{item.temp_max_c:.1f}",
                        "Min Temp (°C)": f"{item.temp_min_c:.1f}",
                        "Rain Total (mm)": f"{item.precipitation_sum_mm:.1f}",
                        "Rain Probability (%)": f"{item.precipitation_probability_pct}%",
                        "Rain Duration (hrs)": f"{item.precipitation_hours:.1f}",
                    })
                st.dataframe(pd.DataFrame(forecast_rows), use_container_width=True, hide_index=True)

        # 3. Mandatory Architectural Provenance & Spatial Resolution Boundary Notice
        obs_time_info = f" | Provider Observation Time: `{obs.observation_time}`" if obs.observation_time else ""
        st.warning(
            "⚠️ **Architectural Provenance Boundary & Spatial Resolution Notice:**\n\n"
            f"• **Live Meteorological Feed:** Conditions above are retrieved from the **Open-Meteo Weather API** "
            f"for the central Pune centroid ({obs.latitude:.2f}°N, {obs.longitude:.2f}°E){obs_time_info}.\n"
            "• **Spatial Resolution Limitation:** Data represents an **~11 km grid resolution cell** covering central Pune "
            "(Shivajinagar cluster). Localized micro-climatic variations across peripheral zones (e.g. Katraj hill runoff, "
            "Hinjawadi IT corridor, Hadapsar heat island) are not resolved at this grid scale.\n"
            "• **Illustrative Planning Models:** The six administrative planning areas and twelve adaptation packages "
            "below remain **illustrative synthetic fixtures (`simulated`)**.\n\n"
            "*A connected weather API provides dynamic environmental situational awareness, but **does not alter physical "
            "intervention benefit scores** or validate municipal engineering feasibility.*"
        )


def render_dataset_tabs(
    zones_df: pd.DataFrame,
    projects_df: pd.DataFrame,
    climatology: Optional[NasaClimatologySummary] = None,
) -> None:
    """Renders interactive tabs displaying baseline planning zones, project packages catalog, and climatology."""
    st.markdown("---")
    st.subheader("📚 Baseline Datasets & Methodology")
    tab_titles = [
        "📍 6 Planning Zones (Baseline)",
        "🛠️ 12 Intervention Packages (Catalog)",
    ]
    if climatology is not None:
        tab_titles.append("🏛️ Regional Climatology (NASA POWER)")

    tabs = st.tabs(tab_titles)

    with tabs[0]:
        st.dataframe(zones_df, use_container_width=True, hide_index=True)

    with tabs[1]:
        st.dataframe(projects_df, use_container_width=True, hide_index=True)

    if climatology is not None:
        with tabs[2]:
            render_nasa_climatology_card(climatology)


def render_nasa_climatology_card(clim: NasaClimatologySummary) -> None:
    """Renders NASA POWER multi-decadal solar and surface climatology baseline card with full provenance disclosures."""
    is_fallback = clim.data_status == "fallback_simulated"
    is_cached = clim.data_status == "cached" or clim.cache_hit

    if clim.data_status == "verified_climatology" and not clim.cache_hit:
        status_badge = "🟢 **NASA POWER Climatology Connected** (Direct Feed)"
        status_color = "#00CC96"
    elif is_cached:
        status_badge = "🟡 **Cached Climatology Baseline** (NASA POWER 30-day Cache)"
        status_color = "#FFA15A"
    else:
        status_badge = "🟠 **Offline Climatology Fallback** (Illustrative Baseline)"
        status_color = "#AB63FA"

    st.markdown(
        f"#### 🏛️ Regional Climatological Baseline | "
        f"<span style='color:{status_color}; font-size:0.9rem;'>{status_badge}</span>",
        unsafe_allow_html=True,
    )

    if is_fallback:
        st.warning(
            "⚠️ **OFFLINE FALLBACK ACTIVE:** NASA POWER API connection is unavailable and no local cache was found. "
            "Climatological figures below are **illustrative synthetic estimates**."
        )

    metric_suffix = " (Simulated)" if is_fallback else ""

    solar = clim.solar_irradiance
    temp = clim.surface_temperature
    precip = clim.precipitation

    # Determine peak values for display
    solar_peak_val = max((v for v in solar.monthly_values.values() if v is not None), default=7.08)
    temp_peak_val = max((v for v in temp.monthly_values.values() if v is not None), default=31.56)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            f"☀️ Peak Solar Irradiance{metric_suffix}",
            f"{solar_peak_val:.2f} {solar.units}",
            delta=f"Annual Mean: {solar.annual_value:.2f} {solar.units}" if solar.annual_value else None,
            delta_color="off",
            help=f"Parameter: {solar.parameter_id} ({solar.long_name}). Native resolution: {solar.native_spatial_resolution}. {solar.aggregation_semantics}.",
        )

    with col2:
        st.metric(
            f"🔥 Peak Ground Skin Temp{metric_suffix}",
            f"{temp_peak_val:.1f} °{temp.units}",
            delta=f"Annual Mean: {temp.annual_value:.1f} °{temp.units}" if temp.annual_value else None,
            delta_color="off",
            help=f"Parameter: {temp.parameter_id} ({temp.long_name}). Native resolution: {temp.native_spatial_resolution}. {temp.aggregation_semantics}.",
        )

    with col3:
        annual_total_str = f"~{clim.annual_cumulative_precipitation_mm:.0f} mm/year"
        st.metric(
            f"🌧️ Normal Annual Rainfall{metric_suffix}",
            annual_total_str,
            delta=f"Mean Rate: {precip.annual_value:.2f} {precip.units}" if precip.annual_value else None,
            delta_color="off",
            help=f"Parameter: {precip.parameter_id} ({precip.long_name}). Native resolution: {precip.native_spatial_resolution}. {precip.aggregation_semantics}.",
        )

    # Monthly Climatology Breakdown Table
    with st.expander("📅 Monthly Climatological Normals Breakdown (NASA POWER)", expanded=False):
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        table_rows = []
        for m in months:
            s_val = solar.monthly_values.get(m)
            t_val = temp.monthly_values.get(m)
            p_val = precip.monthly_values.get(m)
            table_rows.append({
                "Month": m,
                f"Solar Irradiance ({solar.units})": f"{s_val:.3f}" if s_val is not None else "N/A",
                f"Ground Skin Temp (°{temp.units})": f"{t_val:.2f}" if t_val is not None else "N/A",
                f"Daily Precipitation ({precip.units})": f"{p_val:.2f}" if p_val is not None else "N/A",
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    # Mandatory Scientific & Spatial Provenance Disclosures
    st.info(
        "ℹ️ **Scientific & Spatial Provenance Disclosures (NASA POWER):**\n\n"
        f"• **Non-Uniform Spatial Resolution:** Meteorological surface temperature and precipitation originate from **NASA MERRA-2** "
        f"at **0.50° x 0.625° (~55 km x 65 km)**. Downward solar irradiance originates from **CERES SYN1DEG** at **1.00° x 1.00° (~110 km)**.\n"
        f"• **Baseline Climatology Period:** Values reflect pre-computed multi-decadal normals (`{solar.climatology_period}`) for Pune centroid ({clim.latitude:.2f}°N, {clim.longitude:.2f}°E).\n"
        "• **Regional Surface-to-Air Temperature Gradient:** The elevation of Earth Skin Temperature above 2m air temperature "
        "(e.g., +2.63 °C in April pre-monsoon) reflects the **regional thermodynamic surface-to-air gradient** across a ~3,500 km² mixed rural/urban cell. "
        "It is **NOT** a measured Urban Heat Island (UHI) intensity; intra-urban micro-climate UHI requires high-resolution spatial sensing.\n"
        "• **Western Ghats Orographic Smearing:** The 55 km MERRA-2 grid cell extends westward onto the Western Ghats crest, smearing mountain orographic rainfall over the urban valley baseline.\n"
        "• **Strict Architectural Decoupling:** NASA POWER data provides macro-environmental context only and **does not modify optimizer portfolio selection**, intervention benefit scores, or municipal capital limits."
    )
