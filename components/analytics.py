"""Resilience Analytics & Multi-Scenario Comparison Component.

Renders criteria breakdown charts, budget utilization donuts,
cross-policy scenario comparison tables, and Plotly comparative visualizations.
"""

from typing import Dict, Any
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.optimizer import solve_portfolio, PRESET_DISPLAY_NAMES
from src.map_view import render_score_breakdown_chart, render_budget_utilization_chart
from .exports import render_scenario_export_button


def render_score_breakdown(score_breakdown: Dict[str, float]) -> None:
    """Renders score breakdown horizontal bar chart across 5 benefit criteria."""
    render_score_breakdown_chart(score_breakdown)


def render_budget_donut(total_cost: float, rem_budget: float) -> None:
    """Renders budget utilization donut chart (Allocated vs. Remaining)."""
    render_budget_utilization_chart(total_cost, rem_budget)


def build_scenario_comparison_df(
    projects_df: pd.DataFrame,
    budget_crore: float,
) -> pd.DataFrame:
    """Computes optimal portfolios across all 4 policy presets under identical budget."""
    scenario_rows = []
    for p_key, p_name in PRESET_DISPLAY_NAMES.items():
        res = solve_portfolio(projects_df, budget_crore, p_key)
        scenario_rows.append({
            "Preset ID": p_key,
            "Policy Preset": p_name,
            "Total Score (pts)": res["total_score"],
            "Allocated Cost (₹ Cr)": res["total_cost_crore"],
            "Remaining Budget (₹ Cr)": res["budget_remaining_crore"],
            "Funded Areas Count": len(res["selected_project_ids"]),
            "Selected Project IDs": ", ".join(res["selected_project_ids"]),
            "Flood Points": res["score_breakdown"]["flood"],
            "Heat Points": res["score_breakdown"]["heat"],
            "Equity Points": res["score_breakdown"]["equity"],
            "Infra Points": res["score_breakdown"]["infrastructure"],
        })
    return pd.DataFrame(scenario_rows)


def render_scenario_comparison(
    projects_df: pd.DataFrame,
    budget_crore: float,
) -> None:
    """Renders multi-scenario comparison matrix, comparative bar chart, and CSV export."""
    st.markdown("---")
    st.subheader("⚖️ Multi-Scenario Policy Comparison")
    st.markdown(
        f"Comparing optimal adaptation investment portfolios across all four policy presets under the current "
        f"**₹{budget_crore:.1f} Crore** budget allocation:"
    )

    scenario_df = build_scenario_comparison_df(projects_df, budget_crore)

    st.dataframe(
        scenario_df[[
            "Policy Preset", "Total Score (pts)", "Allocated Cost (₹ Cr)",
            "Remaining Budget (₹ Cr)", "Funded Areas Count", "Selected Project IDs"
        ]],
        use_container_width=True,
        hide_index=True,
    )

    # Comparative Plotly Bar Chart across Scenarios
    chart_scenario = go.Figure()
    chart_scenario.add_trace(go.Bar(
        x=scenario_df["Policy Preset"],
        y=scenario_df["Total Score (pts)"],
        name="Total Resilience Score",
        marker_color="#636EFA",
        text=[f"{v:.1f}" for v in scenario_df["Total Score (pts)"]],
        textposition="auto",
    ))
    chart_scenario.add_trace(go.Bar(
        x=scenario_df["Policy Preset"],
        y=scenario_df["Allocated Cost (₹ Cr)"],
        name="Capital Cost (₹ Cr)",
        marker_color="#00CC96",
        text=[f"₹{v:.1f}Cr" for v in scenario_df["Allocated Cost (₹ Cr)"]],
        textposition="auto",
    ))
    chart_scenario.update_layout(
        barmode="group",
        title="Comparison of Score & Cost by Policy Preset",
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
    )
    st.plotly_chart(chart_scenario, use_container_width=True)

    # Download button for scenario comparison matrix
    render_scenario_export_button(scenario_df, budget_crore)
