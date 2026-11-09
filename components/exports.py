"""Data Export Presentation Component.

Handles CSV payload encoding and Streamlit download button rendering
for selected portfolio allocations and multi-scenario matrices.
"""

import streamlit as st
import pandas as pd


def generate_portfolio_csv(table_df: pd.DataFrame) -> bytes:
    """Encodes formatted portfolio table into UTF-8 RFC-4180 CSV bytes."""
    return table_df.to_csv(index=False).encode("utf-8")


def render_portfolio_export_button(
    table_df: pd.DataFrame,
    objective_id: str,
    budget_crore: float,
) -> None:
    """Renders download button for selected portfolio CSV export."""
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


def render_scenario_export_button(
    scenario_df: pd.DataFrame,
    budget_crore: float,
) -> None:
    """Renders download button for scenario comparison matrix CSV export."""
    scenario_csv = generate_scenario_csv(scenario_df)
    st.download_button(
        label="📥 Download Scenario Comparison Matrix (CSV)",
        data=scenario_csv,
        file_name=f"pune_climate_scenarios_{budget_crore:.1f}cr.csv",
        mime="text/csv",
    )
