"""CSV Export Component for Pune Climate Adaptation Investment Optimizer.

This module provides download button components for exporting selected adaptation
portfolios and multi-scenario policy comparison matrices to RFC-4180 compliant CSVs.

Governance & Data Provenance (ADR-003 & ADR-009 Part A):
    - Export artifacts MUST preserve all columns passed from solver/presentation
      layers, specifically including `data_status` and `source_note`.
"""

from typing import Optional
import streamlit as st
import pandas as pd


def generate_portfolio_csv(table_df: pd.DataFrame) -> bytes:
    """Encodes formatted portfolio table into UTF-8 RFC-4180 CSV bytes."""
    return table_df.to_csv(index=False).encode("utf-8")


def render_portfolio_export(
    table_df: Optional[pd.DataFrame],
    objective_id: str,
    budget_crore: float,
) -> None:
    """Render a Streamlit download button for the selected portfolio CSV."""
    if table_df is None or table_df.empty:
        return

    csv_data = generate_portfolio_csv(table_df)
    st.download_button(
        label="📥 Download Selected Portfolio (CSV)",
        data=csv_data,
        file_name=f"pune_climate_portfolio_{objective_id}_{budget_crore:.1f}cr.csv",
        mime="text/csv",
    )


def generate_scenario_csv(scenario_df: pd.DataFrame) -> bytes:
    """Encodes multi-scenario comparison matrix into UTF-8 RFC-4180 CSV bytes."""
    return scenario_df.to_csv(index=False).encode("utf-8")


def render_scenario_export(
    scenario_df: Optional[pd.DataFrame],
    budget_crore: float,
) -> None:
    """Render a Streamlit download button for the scenario comparison matrix CSV."""
    if scenario_df is None or scenario_df.empty:
        return

    scenario_csv = generate_scenario_csv(scenario_df)
    st.download_button(
        label="📥 Download Scenario Comparison Matrix (CSV)",
        data=scenario_csv,
        file_name=f"pune_climate_scenarios_{budget_crore:.1f}cr.csv",
        mime="text/csv",
    )


# Backward-compatible aliases per ADR-009 Part A naming specification
render_portfolio_export_button = render_portfolio_export
render_scenario_export_button = render_scenario_export

__all__ = [
    "generate_portfolio_csv",
    "generate_scenario_csv",
    "render_portfolio_export",
    "render_scenario_export",
    "render_portfolio_export_button",
    "render_scenario_export_button",
]
