"""Portfolio presentation component for the Pune Climate Adaptation Optimizer.

Part of Milestone 4 UI Architecture Modularization (M4-T3 / ADR-009 Part A).
Extracts portfolio presentation responsibilities out of monolithic app.py into
a dedicated, reusable component module:
1. Executive KPI metric cards (funded planning areas, capital allocation,
   additive resilience points, and feasible portfolio count).
2. Selected adaptation portfolio table with audit provenance and data status.
"""

import streamlit as st
import pandas as pd
from components.styles import COLORS, kpi_card_html


def render_kpi_metrics(result: dict, zones_count: int) -> None:
    """Render executive KPI summary cards for the selected adaptation portfolio.

    Renders four responsive cards displaying funded planning areas, total capital
    allocated, aggregated multi-criteria resilience points, and feasible portfolio count.

    Args:
        result: Portfolio optimization result dictionary returned by solve_portfolio.
            Expected keys include 'selected_project_ids', 'total_cost_crore',
            'total_score', 'budget_remaining_crore', 'feasible_portfolio_count',
            and 'combinations_evaluated'.
        zones_count: Total number of planning zones in the baseline dataset.
    """
    num_selected = len(result["selected_project_ids"])
    total_cost = result["total_cost_crore"]
    total_score = result["total_score"]
    rem_budget = result["budget_remaining_crore"]
    feasible_count = result["feasible_portfolio_count"]
    combos_evaluated = result["combinations_evaluated"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            kpi_card_html(
                icon="📍",
                label="Funded Planning Areas",
                value=f"{num_selected} / {zones_count}",
                subtitle="Zones receiving adaptation investment",
                color=COLORS["primary"],
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            kpi_card_html(
                icon="💰",
                label="Capital Allocated",
                value=f"₹{total_cost:.2f} Cr",
                subtitle=f"₹{rem_budget:.2f} Cr remaining of budget",
                color=COLORS["accent"],
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            kpi_card_html(
                icon="📊",
                label="Resilience Score",
                value=f"{total_score:.2f} pts",
                subtitle="Additive multi-criteria planning points",
                color="#2563EB",
            ),
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            kpi_card_html(
                icon="🔍",
                label="Feasible Portfolios",
                value=f"{feasible_count} / {combos_evaluated}",
                subtitle="Budget-feasible combinations evaluated",
                color="#7C3AED",
            ),
            unsafe_allow_html=True,
        )


def render_selected_portfolio_table(
    selected_df: pd.DataFrame, explanation_summary: str
) -> pd.DataFrame:
    """Render the selected adaptation portfolio data table and summary narrative.

    Formats the optimal project package selections into a clean, display-ready
    DataFrame with user-friendly column names, retaining all audit and provenance
    attributes (evidence_quality, data_status, source_note).

    Args:
        selected_df: DataFrame of selected project packages from optimizer result.
        explanation_summary: High-level narrative summary describing the portfolio outcome.

    Returns:
        Formatted DataFrame containing the displayed table rows, or an empty DataFrame
        if no projects were funded.
    """
    st.markdown(f"**Optimization Result:** {explanation_summary}")

    if selected_df.empty:
        st.warning(
            "⚠️ No projects could be funded under the entered budget. "
            "Consider increasing the available budget."
        )
        return pd.DataFrame()

    columns_to_select = [
        "project_id",
        "zone_id",
        "project_name",
        "intervention_type",
        "cost_crore",
        "flood_benefit_score",
        "heat_benefit_score",
        "equity_benefit_score",
        "infrastructure_benefit_score",
        "urgency_score",
        "evidence_quality",
        "data_status",
        "source_note",
    ]

    display_column_names = [
        "Project ID",
        "Zone ID",
        "Project Package",
        "Type",
        "Cost (₹ Cr)",
        "Flood Pts",
        "Heat Pts",
        "Equity Pts",
        "Infra Pts",
        "Urgency",
        "Evidence",
        "Status",
        "Source Note",
    ]

    table_df = selected_df[columns_to_select].copy()
    table_df.columns = display_column_names

    st.dataframe(table_df, use_container_width=True, hide_index=True)

    return table_df
