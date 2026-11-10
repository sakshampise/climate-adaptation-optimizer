"""AI-Assisted Climate Adaptation Investment Prioritization — Streamlit Application

PCCOE International Grand Challenge 2026
Theme: AI for Climate Change

Thin application orchestrator coordinating sidebar controls, engine invocation,
spatial mapping, and modular presentation components (ADR-009 Part A).
Enhanced with the unified civic dashboard design system.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_loader import load_inputs, DataValidationError
from src.optimizer import solve_portfolio, OBJECTIVE_WEIGHTS, PRESET_DISPLAY_NAMES
from src.explanations import generate_portfolio_explanation
from src.map_view import render_spatial_view
from src.ingestion import fetch_live_climate, fetch_nasa_climatology
from components.styles import inject_custom_css, section_header_html, COLORS
from components.provenance import (
    render_provenance_banner,
    render_live_climate_card,
    render_dataset_tabs,
)
from components.portfolio import render_kpi_metrics, render_selected_portfolio
from components.analytics import (
    render_score_breakdown,
    render_budget_donut,
    render_scenario_comparison,
)


st.set_page_config(
    page_title="Pune Climate Adaptation Investment Prioritization",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_dataset():
    """Cached loader for zone and project data fixtures."""
    return load_inputs("data")


def main():
    # Inject global design system CSS
    inject_custom_css()

    # 1. Styled Application Hero Header
    st.markdown(
        """
        <div style="padding: 8px 0 4px;">
            <h1 style="
                font-size: 32px;
                font-weight: 700;
                color: #0F172A;
                margin: 0 0 4px;
                font-family: 'Inter', sans-serif;
            ">
                🌿 Pune Climate Adaptation Investment Prioritization
            </h1>
            <p style="
                font-size: 15px;
                color: #64748B;
                margin: 0;
                font-family: 'Inter', sans-serif;
            ">
                PCCOE International Grand Challenge 2026 &nbsp;·&nbsp; AI for Climate Change
                &nbsp;·&nbsp; <em>Where should the next ₹10 Crore go to make Pune more climate-resilient?</em>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Ingest and Validate Canonical Data
    try:
        zones_df, projects_df = load_dataset()
    except DataValidationError as err:
        st.error(f"❌ Data Validation Error: {err}")
        st.stop()
    except Exception as exc:
        st.error(f"❌ Unexpected Error Loading Data: {exc}")
        st.stop()

    # 3. Sidebar: Municipal Planning Parameters
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 4px 0 12px;">
                <h2 style="
                    font-size: 18px;
                    font-weight: 700;
                    color: #0F172A;
                    margin: 0;
                    font-family: 'Inter', sans-serif;
                ">
                    🎯 Municipal Planning Controls
                </h2>
                <p style="
                    font-size: 12px;
                    color: #64748B;
                    margin: 4px 0 0;
                    font-family: 'Inter', sans-serif;
                ">
                    Configure municipal capital envelope &amp; objective weighting
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        budget_crore = st.slider(
            "Total Adaptation Budget (₹ Crore)",
            min_value=0.0,
            max_value=15.0,
            value=10.0,
            step=0.5,
            help="Target municipal capital allocation budget for the planning cycle.",
        )

        preset_keys = list(OBJECTIVE_WEIGHTS.keys())
        preset_labels = [PRESET_DISPLAY_NAMES[k] for k in preset_keys]

        selected_label = st.selectbox(
            "Policy Priority Preset",
            options=preset_labels,
            index=2,  # Default to 'Balanced Resilience'
            help="Selects the normative multi-criteria weighting scheme.",
        )

        # Reverse lookup preset key from display label
        objective_id = preset_keys[preset_labels.index(selected_label)]
        active_weights = OBJECTIVE_WEIGHTS[objective_id]

        with st.expander("⚖️ Active Weight Distribution", expanded=False):
            for dim, weight in active_weights.items():
                st.write(f"- **{dim.title()}:** `{weight:.2f}` ({int(weight*100)}%)")

        st.markdown("---")
        st.caption("Exact Deterministic Search: Evaluates all 3⁶ = 729 zone package combinations.")

    # 4. Optimization & Explanation Pipeline Invocation
    current_result = solve_portfolio(projects_df, budget_crore, objective_id)
    explanation = generate_portfolio_explanation(current_result, zones_df, projects_df)
    selected_df = current_result["selected_projects"]

    total_cost = current_result["total_cost_crore"]
    rem_budget = current_result["budget_remaining_crore"]

    # 5. Executive Metrics Row
    render_kpi_metrics(current_result, len(zones_df))

    # 6. Spatial Allocation & Breakdown Analytics Layout (Main Decision Workspace)
    col_map, col_charts = st.columns([7, 5])
    with col_map:
        st.markdown(
            section_header_html("📍", "Geospatial Allocation Map"),
            unsafe_allow_html=True,
        )
        render_spatial_view(zones_df, selected_df)

    with col_charts:
        st.markdown(
            section_header_html("📊", "Portfolio Breakdown Analytics"),
            unsafe_allow_html=True,
        )
        render_score_breakdown(current_result["score_breakdown"])
        render_budget_donut(total_cost, rem_budget)

    # 7. Selected Portfolio Table, Explanations & CSV Export
    render_selected_portfolio(selected_df, explanation, objective_id, budget_crore)

    # 8. Multi-Scenario Policy Comparison Matrix
    st.markdown(
        section_header_html("⚖️", "Multi-Scenario Policy Comparison"),
        unsafe_allow_html=True,
    )
    render_scenario_comparison(projects_df, budget_crore)

    # 9. Climate Intelligence & Environmental Context
    st.markdown(
        section_header_html("🌦️", "Live Climate Intelligence (Open-Meteo)"),
        unsafe_allow_html=True,
    )
    climate_obs = fetch_live_climate()
    render_live_climate_card(climate_obs)

    # 10. Baseline Fixtures & Methodology Explorer Tabs (including NASA POWER)
    st.markdown(
        section_header_html("📚", "Baseline Datasets & Methodology"),
        unsafe_allow_html=True,
    )
    climatology_summary = fetch_nasa_climatology(use_cache=True)
    render_dataset_tabs(zones_df, projects_df, climatology=climatology_summary)

    # 11. Data Provenance & Advisory Notice Banner (Bottom Policy Footer)
    st.markdown("---")
    render_provenance_banner()


if __name__ == "__main__":
    main()
