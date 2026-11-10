"""Resilience Analytics & Multi-Scenario Comparison Component.

Renders criteria breakdown charts, budget utilization donuts,
cross-policy scenario comparison tables, and Plotly comparative visualizations.
Conforms to ADR-009 and the design system in components.styles.
"""

from typing import Dict, Any, List, Union, Optional
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.optimizer import solve_portfolio, PRESET_DISPLAY_NAMES
from .styles import COLORS, DIMENSION_COLORS, DIMENSION_LABELS
from .exports import render_scenario_export_button


def render_score_breakdown(score_breakdown: Dict[str, float]) -> None:
    """Renders a horizontal bar chart displaying weighted resilience score by dimension.

    Visualizes relative benefit points across the five evaluation dimensions
    (flood, heat, equity, infrastructure, urgency) according to active policy preset.
    """
    if not score_breakdown:
        st.info("No score breakdown data available.")
        return

    labels = [DIMENSION_LABELS.get(k, k.title()) for k in score_breakdown.keys()]
    values = [float(v) for v in score_breakdown.values()]
    colors = [DIMENSION_COLORS.get(k, COLORS.get("primary", "#0E7C7B")) for k in score_breakdown.keys()]
    texts = [f"{v:.2f} pts" for v in values]

    fig = go.Figure(
        data=[
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker=dict(color=colors),
                text=texts,
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Weighted Resilience Score by Dimension",
            font=dict(family="Newsreader, Georgia, serif", size=18, color="#252B27"),
        ),
        xaxis_title=dict(
            text="Relative Benefit Points (Illustrative Planning Points)",
            font=dict(family="Inter, sans-serif", size=11, color="#575F59"),
        ),
        yaxis=dict(autorange="reversed", tickfont=dict(family="Inter, sans-serif", size=12, color="#252B27")),
        margin=dict(l=10, r=30, t=45, b=30),
        height=320,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#EAE6DC",
            gridwidth=1,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_budget_donut(total_cost_crore: float, remaining_budget_crore: float) -> None:
    """Renders a donut chart illustrating capital allocation versus remaining budget."""
    total_budget = total_cost_crore + remaining_budget_crore
    alloc_pct = (total_cost_crore / total_budget * 100.0) if total_budget > 0 else 0.0

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Allocated Capital", "Remaining Budget"],
                values=[total_cost_crore, remaining_budget_crore],
                hole=0.68,
                marker=dict(colors=[COLORS["primary"], "#DCD7CC"]),
                text=[f"₹{total_cost_crore:.2f} Cr", f"₹{remaining_budget_crore:.2f} Cr"],
                textinfo="text",
                textposition="inside",
                insidetextorientation="horizontal",
                hoverinfo="label+text+percent",
                textfont=dict(size=12, color=["#FFFFFF", "#252B27"], family="Inter, sans-serif"),
                sort=False,
            )
        ]
    )

    fig.add_annotation(
        text=f"<b>₹{total_cost_crore:.2f} Cr</b><br><span style='font-size:11px;color:#575F59;'>Allocated ({alloc_pct:.0f}%)</span>",
        x=0.5,
        y=0.5,
        font=dict(size=14, family="Newsreader, Georgia, serif", color="#252B27"),
        showarrow=False,
    )

    fig.update_layout(
        title=dict(
            text="Budget Utilization",
            font=dict(family="Newsreader, Georgia, serif", size=18, color="#252B27"),
        ),
        margin=dict(l=10, r=10, t=45, b=25),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11, family="Inter, sans-serif", color="#575F59"),
        ),
        height=320,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
    )

    st.plotly_chart(fig, use_container_width=True)


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


def build_scenario_comparison_chart(scenario_df: pd.DataFrame) -> go.Figure:
    """Builds a Plotly grouped bar chart comparing policy presets with clean dual Y-axes.

    Resolves the mixed-unit dilemma (relative score points vs ₹ Crore capital cost)
    by rendering Total Resilience Score on the primary Y-axis (left) and Capital Cost
    on the secondary Y-axis (right), with non-overlapping offset groups.
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=scenario_df["Policy Preset"],
            y=scenario_df["Total Score (pts)"],
            name="Total Resilience Score",
            marker_color=COLORS["primary"],
            text=[f"{v:.1f} pts" for v in scenario_df["Total Score (pts)"]],
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Resilience Score: %{y:.2f} relative pts<extra></extra>",
            offsetgroup=1,
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(
            x=scenario_df["Policy Preset"],
            y=scenario_df["Allocated Cost (₹ Cr)"],
            name="Capital Cost (₹ Cr)",
            marker_color=COLORS["terracotta"],
            text=[f"₹{v:.1f}Cr" for v in scenario_df["Allocated Cost (₹ Cr)"]],
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Capital Cost: ₹%{y:.2f} Cr<extra></extra>",
            offsetgroup=2,
        ),
        secondary_y=True,
    )

    fig.update_layout(
        barmode="group",
        title=dict(
            text="Score & Capital Cost by Policy Preset (Dual Y-Axis)",
            font=dict(family="Newsreader, Georgia, serif", size=18, color="#252B27"),
        ),
        margin=dict(l=10, r=10, t=45, b=10),
        height=340,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(showgrid=False, tickfont=dict(family="Inter, sans-serif", size=11, color="#252B27")),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Inter, sans-serif", size=11, color="#575F59"),
        ),
    )

    fig.update_yaxes(
        title_text="Resilience Score (Relative Points)",
        secondary_y=False,
        showgrid=True,
        gridcolor="#EAE6DC",
        title_font=dict(family="Inter, sans-serif", size=11, color="#575F59"),
        tickfont=dict(family="Inter, sans-serif", size=11, color="#575F59"),
    )

    fig.update_yaxes(
        title_text="Allocated Cost (₹ Crore)",
        secondary_y=True,
        showgrid=False,
        title_font=dict(family="Inter, sans-serif", size=11, color="#575F59"),
        tickfont=dict(family="Inter, sans-serif", size=11, color="#575F59"),
    )

    return fig


def render_scenario_comparison(
    scenario_data: Union[pd.DataFrame, List[Dict[str, Any]]],
    budget_crore: float,
) -> pd.DataFrame:
    """Renders multi-scenario comparison matrix, comparative bar chart, and CSV export.

    Accepts either:
    1. canonical projects_df (computes scenario comparison internally)
    2. pre-computed scenario_rows or scenario_df (Ayush's PR #2 pattern)
    """
    if isinstance(scenario_data, pd.DataFrame) and "project_id" in scenario_data.columns:
        scenario_df = build_scenario_comparison_df(scenario_data, budget_crore)
    elif isinstance(scenario_data, list):
        scenario_df = pd.DataFrame(scenario_data)
    elif isinstance(scenario_data, pd.DataFrame):
        scenario_df = scenario_data.copy()
    else:
        st.info("No scenario comparison data available.")
        return pd.DataFrame()

    display_columns = [
        "Policy Preset",
        "Total Score (pts)",
        "Allocated Cost (₹ Cr)",
        "Remaining Budget (₹ Cr)",
        "Funded Areas Count",
        "Selected Project IDs",
    ]

    if not scenario_df.empty and all(col in scenario_df.columns for col in display_columns):
        st.dataframe(
            scenario_df[display_columns],
            use_container_width=True,
            hide_index=True,
        )
    elif not scenario_df.empty:
        st.dataframe(
            scenario_df,
            use_container_width=True,
            hide_index=True,
        )

    # Comparative Plotly Bar Chart across Scenarios with clean dual Y-axes
    fig = build_scenario_comparison_chart(scenario_df)
    st.plotly_chart(fig, use_container_width=True)

    # Download button for scenario comparison matrix
    render_scenario_export_button(scenario_df, budget_crore)

    return scenario_df
