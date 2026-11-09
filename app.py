"""AI-Assisted Climate Adaptation Investment Prioritization — Streamlit Application

PCCOE International Grand Challenge 2026
Theme: AI for Climate Change

Thin application orchestrator coordinating sidebar controls, engine invocation,
spatial mapping, and modular presentation components (ADR-009 Part A).
"""

import streamlit as st
import plotly.graph_objects as go
from src.data_loader import load_inputs, DataValidationError
from src.optimizer import solve_portfolio, OBJECTIVE_WEIGHTS, PRESET_DISPLAY_NAMES
from src.explanations import generate_portfolio_explanation
from src.map_view import render_spatial_view
from components.provenance import render_provenance_banner, render_dataset_tabs
from components.portfolio import render_kpi_metrics, render_selected_portfolio
from components.analytics import (
    render_score_breakdown,
    render_budget_donut,
    render_scenario_comparison,
)


st.set_page_config(
    page_title="Pune Climate Adaptation Investment Prioritization",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_dataset():
    """Cached loader for zone and project data fixtures."""
    return load_inputs("data")


def main():
    # 1. Application Header
    st.title("🌱 AI-Assisted Climate Adaptation Investment Prioritization")
    st.caption("PCCOE International Grand Challenge 2026 | Theme: AI for Climate Change")
    st.markdown(
        "**Core Question:** *Where should the next ₹10 Crore go to make Pune more climate-resilient?*"
    )

    # 2. Provenance Notice Banner
    render_provenance_banner()

    # 3. Ingest and Validate Canonical Data
    try:
        zones_df, projects_df = load_dataset()
    except DataValidationError as err:
        st.error(f"❌ Data Validation Error: {err}")
        st.stop()
    except Exception as exc:
        st.error(f"❌ Unexpected Error Loading Data: {exc}")
        st.stop()

    # 4. Sidebar: Municipal Planning Parameters
    st.sidebar.header("🎯 Municipal Planning Parameters")

    budget_crore = st.sidebar.slider(
        "Total Adaptation Budget (₹ Crore)",
        min_value=0.0,
        max_value=15.0,
        value=10.0,
        step=0.5,
        help="Target municipal capital allocation budget for the planning cycle.",
    )

    preset_keys = list(OBJECTIVE_WEIGHTS.keys())
    preset_labels = [PRESET_DISPLAY_NAMES[k] for k in preset_keys]

    selected_label = st.sidebar.selectbox(
        "Policy Priority Preset",
        options=preset_labels,
        index=2,  # Default to 'Balanced Resilience'
        help="Selects the normative multi-criteria weighting scheme.",
    )

    # Reverse lookup preset key from display label
    objective_id = preset_keys[preset_labels.index(selected_label)]
    active_weights = OBJECTIVE_WEIGHTS[objective_id]

    with st.sidebar.expander("⚖️ Active Weight Distribution", expanded=False):
        for dim, weight in active_weights.items():
            st.write(f"- **{dim.title()}:** `{weight:.2f}` ({int(weight*100)}%)")

    st.sidebar.markdown("---")
    st.sidebar.caption("Exact Deterministic Search: Evaluates all 3⁶ = 729 zone package combinations.")

    # 5. Optimization & Explanation Pipeline Invocation
    current_result = solve_portfolio(projects_df, budget_crore, objective_id)
    explanation = generate_portfolio_explanation(current_result, zones_df, projects_df)
    selected_df = current_result["selected_projects"]

    total_cost = current_result["total_cost_crore"]
    rem_budget = current_result["budget_remaining_crore"]

    # 6. Executive Metrics Row
    render_kpi_metrics(current_result, len(zones_df))

    # 7. Spatial Allocation & Breakdown Analytics Layout
    col_map, col_charts = st.columns([7, 5])
    with col_map:
        st.subheader("📍 Geospatial Allocation Map")
        render_spatial_view(zones_df, selected_df)

    with col_charts:
        st.subheader("📊 Portfolio Breakdown")
        render_score_breakdown(current_result["score_breakdown"])
        render_budget_donut(total_cost, rem_budget)

    # 8. Selected Portfolio Table, Explanations & CSV Export
    render_selected_portfolio(selected_df, explanation, objective_id, budget_crore)

    # 9. Multi-Scenario Policy Comparison Matrix
    render_scenario_comparison(projects_df, budget_crore)

    # 10. Baseline Fixtures & Methodology Explorer Tabs
    render_dataset_tabs(zones_df, projects_df)


if __name__ == "__main__":
    main()
