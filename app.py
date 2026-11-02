"""Streamlit application for AI-Assisted Climate Adaptation Investment Prioritization.

PCCOE International Grand Challenge 2026
Theme: AI for Climate Change
"""

import streamlit as st
import pandas as pd
from src.data_loader import load_inputs, DataValidationError


st.set_page_config(
    page_title="Pune Climate Adaptation Investment Prioritization",
    page_icon="🌱",
    layout="wide",
)


def main():
    st.title("🌱 AI-Assisted Climate Adaptation Investment Prioritization")
    st.caption("PCCOE International Grand Challenge 2026 | Theme: AI for Climate Change")
    st.markdown(
        "**Core Question:** *Where should the next ₹10 Crore go to make Pune more climate-resilient?*"
    )

    # Data Provenance & Methodology Guardrail Banner
    st.info(
        "ℹ️ **Data Provenance & Policy Notice:** All baseline indicators, project candidate packages, "
        "and costs are currently configured with **simulated/illustrative** planning values for prototype "
        "evaluation. The system functions as a transparent, multi-criteria decision-support aid. Final "
        "capital deployment remains in the authority of municipal stakeholders."
    )

    # Sidebar Controls
    st.sidebar.header("🎯 Municipal Planning Parameters")
    budget_crore = st.sidebar.slider(
        "Total Available Adaptation Budget (₹ Crore)",
        min_value=1.0,
        max_value=15.0,
        value=10.0,
        step=0.5,
        help="Target municipal capital allocation budget for the planning cycle.",
    )

    objective_choice = st.sidebar.selectbox(
        "Policy Priority Preset",
        options=[
            "Balanced Resilience",
            "Flood Priority",
            "Heat Priority",
            "Social & Climate Equity",
        ],
        index=0,
        help="Selects the normative weighting scheme for multi-criteria prioritization.",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Current Milestone:** Milestone 1 (Data Foundation & Skeleton)\n\n"
        "**Next Milestone:** Milestone 2 (Exact Portfolio Optimizer)"
    )

    # Load and validate input datasets
    try:
        zones_df, projects_df = load_inputs("data")
    except DataValidationError as err:
        st.error(f"❌ Data Validation Error: {err}")
        st.stop()
    except Exception as exc:
        st.error(f"❌ Unexpected Error Loading Data: {exc}")
        st.stop()

    # Overview Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Planning Zones", len(zones_df))
    with col2:
        st.metric("Candidate Projects", len(projects_df))
    with col3:
        st.metric("Active Budget", f"₹{budget_crore:.1f} Cr")
    with col4:
        st.metric("Policy Focus", objective_choice)

    # Display Data Tabs
    tab_zones, tab_projects = st.tabs(["📍 Illustrative Planning Zones", "🛠️ Candidate Adaptation Packages"])

    with tab_zones:
        st.subheader("Planning Areas & Baseline Hazard Indices")
        st.markdown(
            "Each zone represents a distinct urban vulnerability typology in Pune. "
            "Scores represent relative planning indices (0–100)."
        )
        display_zones = zones_df[[
            "zone_id", "label", "flood_risk_index", "heat_risk_index",
            "exposure_index", "vulnerability_index", "critical_infrastructure_index",
            "data_status", "source_note"
        ]].copy()
        display_zones.columns = [
            "Zone ID", "Area Name", "Flood Risk", "Heat Risk",
            "Exposure", "Vulnerability", "Critical Infra",
            "Data Status", "Source Note"
        ]
        st.dataframe(display_zones, use_container_width=True, hide_index=True)

    with tab_projects:
        st.subheader("Evaluated Intervention Packages")
        st.markdown(
            "Each zone is assigned exactly two mutually exclusive adaptation alternatives. "
            "Benefit points are relative planning scores (0–100)."
        )
        display_projects = projects_df[[
            "project_id", "zone_id", "project_name", "intervention_type",
            "cost_crore", "feasible", "flood_benefit_score", "heat_benefit_score",
            "equity_benefit_score", "infrastructure_benefit_score", "urgency_score",
            "evidence_quality", "data_status"
        ]].copy()
        display_projects.columns = [
            "Project ID", "Zone ID", "Package Name", "Type",
            "Cost (₹ Cr)", "Feasible", "Flood Pts", "Heat Pts",
            "Equity Pts", "Infra Pts", "Urgency",
            "Evidence", "Data Status"
        ]
        st.dataframe(display_projects, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
