"""Analytics and charting component for the Pune Climate Optimizer dashboard.

Renders multi-criteria score breakdowns, budget utilization donut charts,
and cross-policy scenario comparisons with a unified professional color palette.

Guardrail Compliance:
    Per ADR-009, all chart labels and score metrics must refer to scores as
    'Relative Benefit Points' or 'Illustrative' - never as empirical, physical,
    or validated hazard reductions.
"""

from typing import Any, Dict, List
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.styles import COLORS, DIMENSION_COLORS, DIMENSION_LABELS


def render_score_breakdown(score_breakdown: Dict[str, float]) -> None:
    """Renders a horizontal bar chart displaying weighted resilience score by dimension.

    Visualizes relative benefit points across the five evaluation dimensions
    (flood, heat, equity, infrastructure, urgency) according to the active
    policy weighting preset.

    Args:
        score_breakdown: Dictionary mapping dimension keys to float weighted points.
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
        title="Weighted Resilience Score by Dimension",
        xaxis_title="Relative Benefit Points (Illustrative)",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=30, t=45, b=30),
        height=300,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(
            title="Relative Benefit Points (Illustrative)",
            showgrid=True,
            gridcolor="#F1F5F9",
            gridwidth=1,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_budget_donut(total_cost_crore: float, remaining_budget_crore: float) -> None:
    """Renders a donut chart illustrating capital allocation versus remaining budget.

    Displays the allocated capital expenditure against the unallocated reserve
    with the total planning budget highlighted at the center of the donut.

    Args:
        total_cost_crore: Capital cost allocated to selected projects in ₹ Crore.
        remaining_budget_crore: Remaining unallocated capital budget in ₹ Crore.
    """
    total_budget = total_cost_crore + remaining_budget_crore

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Allocated Capital", "Remaining Budget"],
                values=[total_cost_crore, remaining_budget_crore],
                hole=0.65,
                marker=dict(colors=[COLORS["accent"], "#E2E8F0"]),
                textinfo="label+value",
                hoverinfo="label+value+percent",
                textfont=dict(size=12),
            )
        ]
    )

    fig.add_annotation(
        text=f"<b>₹{total_budget:.1f} Cr</b>",
        x=0.5,
        y=0.5,
        font=dict(size=16, family="Inter, sans-serif"),
        showarrow=False,
    )

    fig.update_layout(
        title="Budget Utilization",
        margin=dict(l=10, r=10, t=45, b=10),
        showlegend=False,
        height=300,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_scenario_comparison(
    scenario_rows: List[Dict[str, Any]],
    budget_crore: float,
) -> pd.DataFrame:
    """Renders a comparison table and grouped bar chart across policy presets.

    Compares the optimal portfolios generated under different normative policy
    weighting schemes for the specified budget constraint.

    Args:
        scenario_rows: List of dictionaries containing evaluated scenario metrics.
            Each dictionary contains: 'Preset ID', 'Policy Preset', 'Total Score (pts)',
            'Allocated Cost (₹ Cr)', 'Remaining Budget (₹ Cr)', 'Funded Areas Count',
            'Selected Project IDs', 'Flood Points', 'Heat Points', 'Equity Points',
            'Infra Points'.
        budget_crore: Total municipal adaptation budget allocation in ₹ Crore.

    Returns:
        pd.DataFrame: The constructed scenario comparison DataFrame.
    """
    scenario_df = pd.DataFrame(scenario_rows)

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
    else:
        st.info("No scenario comparison data available.")
        return scenario_df

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=scenario_df["Policy Preset"],
            y=scenario_df["Total Score (pts)"],
            name="Total Score (Relative Benefit Points)",
            marker_color=COLORS["primary"],
            text=[f"{v:.1f}" for v in scenario_df["Total Score (pts)"]],
            textposition="auto",
        )
    )

    fig.add_trace(
        go.Bar(
            x=scenario_df["Policy Preset"],
            y=scenario_df["Allocated Cost (₹ Cr)"],
            name="Allocated Cost (₹ Cr)",
            marker_color=COLORS["accent"],
            text=[f"₹{v:.1f}Cr" for v in scenario_df["Allocated Cost (₹ Cr)"]],
            textposition="auto",
        )
    )

    fig.update_layout(
        barmode="group",
        title="Score vs. Capital Cost Across Policy Presets",
        margin=dict(l=10, r=10, t=45, b=10),
        height=340,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)

    return scenario_df
