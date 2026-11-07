"""Data provenance and transparency component for the Pune Climate Optimizer.

Renders governance disclaimer banners, dataset explorer tabs, and audit metadata
to ensure municipal stakeholders understand baseline data provenance and that
model outputs represent relative multi-criteria benefit points rather than
empirical hazard reductions (in accordance with ADR-003 and ADR-009).
"""

import pandas as pd
import streamlit as st
from components.styles import COLORS

__all__ = ["render_provenance_banner", "render_dataset_tabs"]


def render_provenance_banner() -> None:
    """Render a styled data provenance and policy disclaimer banner.

    Informs decision-makers that all baseline indicators, project candidate
    packages, and costs are configured with simulated/illustrative planning
    values for prototype evaluation. Model outputs represent relative
    multi-criteria benefit points rather than validated physical hazard
    reductions.

    The banner is styled with the `.provenance-banner` CSS class defined in
    `components/styles.py`.
    """
    banner_html = (
        "<div class='provenance-banner'>\n"
        "  <div style='display: flex; align-items: flex-start; gap: 12px;'>\n"
        "    <span class='provenance-icon'>⚠️</span>\n"
        "    <div>\n"
        "      <strong style='font-size: 14px; color: #78350F;'>Data Provenance & Policy Notice</strong>\n"
        "      <p style='margin: 6px 0 0; line-height: 1.5;'>\n"
        "        All baseline indicators, project candidate packages, and costs are currently configured with\n"
        "        <strong>simulated/illustrative</strong> planning values for prototype evaluation.\n"
        "        Model outputs represent relative multi-criteria benefit points, not validated physical\n"
        "        hazard reductions. The system functions as a transparent, multi-criteria decision-support aid.\n"
        "        Final capital deployment remains in the authority of municipal stakeholders.\n"
        "      </p>\n"
        "    </div>\n"
        "  </div>\n"
        "</div>"
    )
    st.markdown(banner_html, unsafe_allow_html=True)


def render_dataset_tabs(zones_df: pd.DataFrame, projects_df: pd.DataFrame) -> None:
    """Render the baseline planning datasets in interactive Streamlit tabs.

    Provides transparent visibility into the underlying planning zones and
    candidate intervention packages, emphasizing their simulated/illustrative
    nature and referencing provenance documentation.

    Parameters
    ----------
    zones_df : pd.DataFrame
        DataFrame containing the 6 municipal planning zones and their baseline indicators.
    projects_df : pd.DataFrame
        DataFrame containing the 12 candidate intervention packages and their attributes.
    """
    tab_zones, tab_projects = st.tabs([
        "📍 6 Planning Zones (Baseline Indicators)",
        "🛠️ 12 Intervention Packages (Candidate Catalog)",
    ])

    with tab_zones:
        st.dataframe(zones_df, use_container_width=True, hide_index=True)
        st.caption(
            "All zone indicators are illustrative planning values (data_status: simulated). "
            "See data/sources.md for methodology notes."
        )

    with tab_projects:
        st.dataframe(projects_df, use_container_width=True, hide_index=True)
        st.caption(
            "Intervention costs and benefit scores are illustrative estimates. "
            "See individual source_note fields for derivation basis."
        )
