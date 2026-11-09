"""Provenance, Data Disclosures, and Live Climate Status Component.

Renders prototype advisory notices, live API connection status cards,
data freshness indicators, and explicit data boundary disclaimers separating
real-time meteorological observations from illustrative municipal planning fixtures.
"""

from typing import Optional
import streamlit as st
import pandas as pd
from src.ingestion.schemas import LiveWeatherObservation


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
    # 1. Connection status badge
    if obs.is_live and not obs.cache_hit:
        status_badge = "🟢 **Live Climate API Connected** (Open-Meteo Real-Time)"
        status_color = "#00CC96"
    elif obs.cache_hit:
        age_str = f"{int(obs.freshness_seconds)}s ago" if obs.freshness_seconds is not None else "recently"
        status_badge = f"🟡 **Cached Climate Data** (Open-Meteo, refreshed {age_str})"
        status_color = "#FFA15A"
    else:
        status_badge = "🟠 **Offline Climate Fallback** (Illustrative Synthetic Baseline)"
        status_color = "#AB63FA"

    with st.container():
        st.markdown(f"#### 🌦️ Pune Live Environmental Context | <span style='color:{status_color}; font-size:0.9rem;'>{status_badge}</span>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡️ Ambient Temperature", f"{obs.temperature_c:.1f} °C", help="Real-time 2m dry-bulb temperature")
        col2.metric("☀️ Apparent Temperature", f"{obs.apparent_temperature_c:.1f} °C", help="Feels-like temperature accounting for wind and relative humidity")
        col3.metric("💧 Relative Humidity", f"{obs.relative_humidity_pct:.0f} %", help="Atmospheric moisture level")
        col4.metric("🌧️ Current Rain / Status", f"{obs.precipitation_mm:.1f} mm", delta=obs.weather_description, delta_color="off")

        # 2. 7-Day Forecast Expander
        if obs.daily_forecast:
            with st.expander("📅 7-Day Municipal Weather Outlook (Open-Meteo Daily Forecast)", expanded=False):
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

        # 3. Mandatory Architectural Provenance Boundary Warning
        st.warning(
            "⚠️ **Architectural Provenance Boundary Notice:**\n\n"
            "• **Live Empirical Data:** The weather metrics and short-term forecast above are real-time observations "
            f"retrieved from **Open-Meteo API** for Pune coordinates ({obs.latitude:.2f}°N, {obs.longitude:.2f}°E).\n"
            "• **Illustrative Planning Models:** The six administrative planning areas and twelve adaptation packages "
            "below remain **illustrative synthetic fixtures (`simulated`)**.\n\n"
            "*A connected weather API provides dynamic environmental situational awareness, but **does not alter physical "
            "intervention benefit scores** or validate municipal engineering feasibility.*"
        )


def render_dataset_tabs(zones_df: pd.DataFrame, projects_df: pd.DataFrame) -> None:
    """Renders interactive tabs displaying baseline planning zones and project packages catalog."""
    st.markdown("---")
    st.subheader("📚 Baseline Datasets & Methodology")
    tab_z, tab_p = st.tabs(["📍 6 Planning Zones (Baseline)", "🛠️ 12 Intervention Packages (Catalog)"])

    with tab_z:
        st.dataframe(zones_df, use_container_width=True, hide_index=True)

    with tab_p:
        st.dataframe(projects_df, use_container_width=True, hide_index=True)
