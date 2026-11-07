"""CSV Export Component for Pune Climate Adaptation Investment Optimizer.

This module provides download button components for exporting selected adaptation
portfolios and multi-scenario policy comparison matrices to RFC-4180 compliant CSVs.

Governance & Data Provenance (ADR-003 & ADR-009 Part A):
    - Export artifacts MUST preserve all columns passed from the solver/presentation
      layers, specifically including `data_status` (provenance taxonomy: verified,
      derived, simulated) and `source_note` (methodological justification).
    - Preserving these fields ensures complete civic auditability and prevents
      unlabeled simulated figures from circulating as official municipal determinations.
"""

from typing import Optional
import pandas as pd
import streamlit as st


def render_portfolio_export(
    table_df: Optional[pd.DataFrame],
    objective_id: str,
    budget_crore: float,
) -> None:
    """Render a Streamlit download button for the selected portfolio CSV.

    Exports the complete selected adaptation project portfolio under the active
    policy preset and budget envelope. Preserves all audit trail fields including
    `data_status` and `source_note` per ADR-003 and ADR-009.

    Args:
        table_df: DataFrame containing selected project details and scores.
            If None or empty, the function returns immediately without rendering.
        objective_id: Identifier for the active objective preset (e.g., 'balanced',
            'flood_first', 'heat_resilience', 'equity_focus').
        budget_crore: Budget constraint in Crores of INR (₹ Cr).

    Returns:
        None
    """
    if table_df is None or table_df.empty:
        return

    csv_data = table_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Selected Portfolio (CSV)",
        data=csv_data,
        file_name=f"pune_climate_portfolio_{objective_id}_{budget_crore:.1f}cr.csv",
        mime="text/csv",
    )


def render_scenario_export(
    scenario_df: Optional[pd.DataFrame],
    budget_crore: float,
) -> None:
    """Render a Streamlit download button for the scenario comparison matrix CSV.

    Exports comparative metrics across all policy presets (Balanced, Flood-First,
    Heat-First, Equity-First) under the specified budget envelope. Preserves all
    evaluation metrics and score decompositions per ADR-003 and ADR-009.

    Args:
        scenario_df: DataFrame comparing portfolio outcomes across policy presets.
            If None or empty, the function returns immediately without rendering.
        budget_crore: Budget constraint in Crores of INR (₹ Cr).

    Returns:
        None
    """
    if scenario_df is None or scenario_df.empty:
        return

    csv_data = scenario_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Scenario Comparison Matrix (CSV)",
        data=csv_data,
        file_name=f"pune_climate_scenarios_{budget_crore:.1f}cr.csv",
        mime="text/csv",
    )


# Backward-compatible aliases per ADR-009 Part A naming specification
render_portfolio_export_button = render_portfolio_export
render_scenario_export_button = render_scenario_export

__all__ = [
    "render_portfolio_export",
    "render_scenario_export",
    "render_portfolio_export_button",
    "render_scenario_export_button",
]
