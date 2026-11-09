"""Portfolio Presentation Component.

Renders executive KPI metrics, selected adaptation package tables,
and transparent selection/exclusion trade-off narratives.
"""

from typing import Dict, Any
import streamlit as st
import pandas as pd
from .exports import render_portfolio_export_button


PORTFOLIO_COLUMN_MAP = [
    ("project_id", "Project ID"),
    ("zone_id", "Zone ID"),
    ("project_name", "Project Package"),
    ("intervention_type", "Type"),
    ("cost_crore", "Cost (₹ Cr)"),
    ("flood_benefit_score", "Flood Pts"),
    ("heat_benefit_score", "Heat Pts"),
    ("equity_benefit_score", "Equity Pts"),
    ("infrastructure_benefit_score", "Infra Pts"),
    ("urgency_score", "Urgency"),
    ("evidence_quality", "Evidence"),
    ("data_status", "Status"),
    ("source_note", "Source Note"),
]


def format_portfolio_table(selected_df: pd.DataFrame) -> pd.DataFrame:
    """Formats selected projects dataframe with human-readable headers and preserved provenance."""
    raw_cols = [src for src, _ in PORTFOLIO_COLUMN_MAP]
    display_cols = [dst for _, dst in PORTFOLIO_COLUMN_MAP]

    table_df = selected_df[raw_cols].copy()
    table_df.columns = display_cols
    return table_df


def render_kpi_metrics(result: Dict[str, Any], zones_count: int) -> None:
    """Renders 4-column executive KPI metrics row."""
    num_selected = len(result.get("selected_project_ids", []))
    total_cost = result.get("total_cost_crore", 0.0)
    total_score = result.get("total_score", 0.0)
    rem_budget = result.get("budget_remaining_crore", 0.0)
    feasible_count = result.get("feasible_portfolio_count", 0)
    evaluated_count = result.get("combinations_evaluated", 729)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(
            "Funded Planning Areas",
            f"{num_selected} / {zones_count}",
            help="Number of zones allocated an intervention",
        )
    with kpi2:
        st.metric(
            "Total Capital Allocated",
            f"₹{total_cost:.2f} Cr",
            delta=f"-₹{rem_budget:.2f} Cr remaining",
            delta_color="normal",
        )
    with kpi3:
        st.metric(
            "Resilience Points Score",
            f"{total_score:.2f} pts",
            help="Additive multi-criteria planning score",
        )
    with kpi4:
        st.metric(
            "Feasible Portfolios",
            f"{feasible_count} / {evaluated_count}",
            help="Portfolios within budget limit",
        )


def render_selected_portfolio(
    selected_df: pd.DataFrame,
    explanation: Dict[str, Any],
    objective_id: str,
    budget_crore: float,
) -> None:
    """Renders optimal portfolio table, export button, and decision explanations."""
    st.subheader("📋 Selected Adaptation Portfolio")
    st.markdown(f"**Optimization Result:** {explanation.get('summary', '')}")

    if not selected_df.empty:
        table_df = format_portfolio_table(selected_df)
        st.dataframe(table_df, use_container_width=True, hide_index=True)
        render_portfolio_export_button(table_df, objective_id, budget_crore)
    else:
        st.warning("⚠️ No projects could be funded under the entered budget. Consider increasing the available budget.")

    # Transparent Selection & Exclusion Explanations Expander
    with st.expander("🔍 Transparent Selection & Exclusion Explanations", expanded=False):
        st.markdown("#### Selected Package Contributions")
        for item in explanation.get("selected_explanations", []):
            st.markdown(
                f"- **{item['project_id']} — {item['project_name']}** ({item['zone_label']}): "
                f"**₹{item['cost_crore']:.2f} Cr** | {item['score_contribution_narrative']}\n\n"
                f"  *Rationale:* {item['rationale']} *(Source: {item['source_note']})*"
            )

        st.markdown("---")
        st.markdown("#### Excluded Package Rationale")
        for item in explanation.get("unselected_explanations", []):
            st.markdown(
                f"- **{item['project_id']} — {item['project_name']}** ({item['zone_label']}): "
                f"**₹{item['cost_crore']:.2f} Cr** | {item['reason']}"
            )
