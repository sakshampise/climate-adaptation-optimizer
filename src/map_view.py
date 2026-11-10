"""Spatial and chart visualization module for Climate Adaptation Investment Prioritization.

Generates interactive maps and charts with robust fallback tables,
adhering to the visualization contract in CONTEXT.md and PROJECT_SPEC.md.
"""

from typing import Dict, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_spatial_view(
    zones_df: pd.DataFrame,
    selected_projects_df: Optional[pd.DataFrame] = None,
) -> None:
    """Renders an interactive map of Pune planning zones with status-based markers.

    If mapping fails for any reason, falls back to a structured tabular representation.
    """
    st.caption("🗺️ *Coordinates and boundaries are illustrative approximations for demonstration purposes.*")

    try:
        plot_df = zones_df.copy()

        # Join selected project information if available
        if selected_projects_df is not None and not selected_projects_df.empty:
            sel_map = {row["zone_id"]: row["project_name"] for _, row in selected_projects_df.iterrows()}
            cost_map = {row["zone_id"]: row["cost_crore"] for _, row in selected_projects_df.iterrows()}
            plot_df["funded"] = plot_df["zone_id"].apply(lambda zid: "Funded (Project Selected)" if zid in sel_map else "Unfunded in Active Portfolio")
            plot_df["selected_project"] = plot_df["zone_id"].apply(lambda zid: sel_map.get(zid, "None"))
            plot_df["allocated_cost"] = plot_df["zone_id"].apply(lambda zid: f"₹{cost_map[zid]:.2f} Cr" if zid in cost_map else "₹0.00 Cr")
        else:
            plot_df["funded"] = "Baseline (No Projects Selected)"
            plot_df["selected_project"] = "None"
            plot_df["allocated_cost"] = "₹0.00 Cr"

        # Create Plotly Scattermapbox or standard Scatter plot
        # Use open-street-map free style with zero external token requirement
        fig = px.scatter_mapbox(
            plot_df,
            lat="latitude",
            lon="longitude",
            hover_name="label",
            hover_data={
                "latitude": False,
                "longitude": False,
                "funded": True,
                "selected_project": True,
                "allocated_cost": True,
                "flood_risk_index": True,
                "heat_risk_index": True,
                "exposure_index": True,
            },
            color="funded",
            color_discrete_map={
                "Funded (Project Selected)": "#00CC96",
                "Unfunded in Active Portfolio": "#FFA15A",
                "Baseline (No Projects Selected)": "#636EFA",
            },
            size=[25] * len(plot_df),
            zoom=11,
            center={"lat": 18.5204, "lon": 73.8567},  # Pune center coordinates
            mapbox_style="open-street-map",
            height=450,
        )

        fig.update_layout(
            margin={"r": 0, "t": 20, "l": 0, "b": 0},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as err:
        st.warning(f"Map rendering unavailable ({err}). Displaying geographic table fallback.")
        fallback_df = zones_df[[
            "zone_id", "label", "latitude", "longitude",
            "flood_risk_index", "heat_risk_index", "data_status"
        ]].copy()
        st.dataframe(fallback_df, use_container_width=True, hide_index=True)


def render_score_breakdown_chart(score_breakdown: Dict[str, float]) -> None:
    """Renders a horizontal bar chart displaying contribution by resilience dimension."""
    dimension_labels = {
        "flood": "🌊 Flood Mitigation",
        "heat": "☀️ Heat Abatement",
        "equity": "🤝 Social & Equity",
        "infrastructure": "🏗️ Critical Assets",
        "urgency": "⚡ Urgency Priority",
    }

    labels = [dimension_labels.get(k, k.title()) for k in score_breakdown.keys()]
    values = [float(v) for v in score_breakdown.values()]

    fig = go.Figure(
        data=[
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker=dict(color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]),
                text=[f"{v:.2f} pts" for v in values],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Weighted Resilience Points Breakdown",
        xaxis_title="Weighted Planning Points",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=20, t=40, b=30),
        height=280,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_budget_utilization_chart(total_cost_crore: float, remaining_budget_crore: float) -> None:
    """Renders a donut chart of allocated vs remaining capital budget."""
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Allocated Capital", "Remaining Budget"],
                values=[total_cost_crore, remaining_budget_crore],
                hole=0.6,
                marker=dict(colors=["#00CC96", "#E5ECF6"]),
                textinfo="label+value",
                hoverinfo="label+value+percent",
            )
        ]
    )

    fig.update_layout(
        title=f"Budget Allocation (Total: ₹{total_cost_crore + remaining_budget_crore:.2f} Cr)",
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False,
        height=280,
    )

    st.plotly_chart(fig, use_container_width=True)
