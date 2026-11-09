"""Provenance and Data Disclosures Component.

Renders prototype advisory notices, synthetic data status indicators,
and raw baseline dataset explorer tabs.
"""

import streamlit as st
import pandas as pd


def render_provenance_banner() -> None:
    """Renders prominent disclaimer declaring illustrative data status and advisory scope."""
    st.info(
        "ℹ️ **Data Provenance & Policy Notice:** All baseline indicators, project candidate packages, "
        "and costs are currently configured with **simulated/illustrative** planning values for prototype "
        "evaluation. The system functions as a transparent, multi-criteria decision-support aid. Final "
        "capital deployment remains in the authority of municipal stakeholders."
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
