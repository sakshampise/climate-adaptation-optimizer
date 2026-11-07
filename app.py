"""AI-Assisted Climate Adaptation Investment Prioritization — Streamlit Application

PCCOE International Grand Challenge 2026
Theme: AI for Climate Change

Application Orchestrator (M4-T3 Architecture — ADR-009 Part A)
Coordinates page configuration, data loading, planning parameter inputs,
solver invocation, and component rendering.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.data_loader import load_inputs, DataValidationError
from src.optimizer import solve_portfolio, OBJECTIVE_WEIGHTS, PRESET_DISPLAY_NAMES
from src.explanations import generate_portfolio_explanation
from src.map_view import render_spatial_view
from components.styles import inject_custom_css, section_header_html, COLORS
from components.portfolio import render_kpi_metrics, render_selected_portfolio_table
from components.analytics import (
    render_score_breakdown,
    render_budget_donut,
    render_scenario_comparison,
)
from components.provenance import render_provenance_banner, render_dataset_tabs
from components.exports import render_portfolio_export, render_scenario_export


st.set_page_config(
    page_title="Pune Climate Adaptation Investment Prioritization",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_dataset():
    """Cached loader for zone and project data fixtures."""
    return load_inputs("data")


def main():
    # Inject custom theme CSS
    inject_custom_css()

    # ── Application Header ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding: 8px 0 4px;">
            <h1 style="
                font-size: 32px;
                font-weight: 700;
                color: #0F172A;
                margin: 0 0 4px;
                font-family: 'Inter', sans-serif;
            ">
                🌿 Pune Climate Adaptation Investment Prioritization
            </h1>
            <p style="
                font-size: 15px;
                color: #64748B;
                margin: 0;
                font-family: 'Inter', sans-serif;
            ">
                PCCOE International Grand Challenge 2026 &nbsp;·&nbsp; AI for Climate Change
                &nbsp;·&nbsp; <em>Where should the next ₹10 Crore go to make Pune more climate-resilient?</em>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Provenance Notice ───────────────────────────────────────────────
    render_provenance_banner()

    # ── Data Ingestion ──────────────────────────────────────────────────
    try:
        zones_df, projects_df = load_dataset()
    except DataValidationError as err:
        st.error(f"❌ Data Validation Error: {err}")
        st.stop()
    except Exception as exc:
        st.error(f"❌ Unexpected Error Loading Data: {exc}")
        st.stop()

    # ── Sidebar: Planning Controls ──────────────────────────────────────
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 4px 0 12px;">
                <h2 style="
                    font-size: 18px;
                    font-weight: 700;
                    color: #0F172A;
                    margin: 0;
                    font-family: 'Inter', sans-serif;
                ">🎯 Municipal Planning Parameters</h2>
                <p style="font-size: 12px; color: #94A3B8; margin: 4px 0 0;">
                    Adjust budget and policy priority to explore adaptation strategies
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        budget_crore = st.slider(
            "Total Adaptation Budget (₹ Crore)",
            min_value=0.0,
            max_value=15.0,
            value=10.0,
            step=0.5,
            help="Target municipal capital allocation budget for the planning cycle.",
        )

        preset_keys = list(OBJECTIVE_WEIGHTS.keys())
        preset_labels = [PRESET_DISPLAY_NAMES[k] for k in preset_keys]

        selected_label = st.selectbox(
            "Policy Priority Preset",
            options=preset_labels,
            index=2,  # Default to 'Balanced Resilience'
            help="Selects the normative multi-criteria weighting scheme.",
        )

        # Reverse lookup key from label
        objective_id = preset_keys[preset_labels.index(selected_label)]
        active_weights = OBJECTIVE_WEIGHTS[objective_id]

        # Display active weights
        with st.expander("⚖️ Active Weight Distribution", expanded=False):
            for dim, weight in active_weights.items():
                pct = int(weight * 100)
                st.markdown(
                    f"""<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;">
                        <span style="font-size:13px;color:#475569;">{dim.title()}</span>
                        <span style="font-size:13px;font-weight:600;color:#0E7C7B;">{pct}%</span>
                    </div>
                    <div style="background:#E2E8F0;border-radius:4px;height:6px;margin-bottom:8px;">
                        <div style="background:#0E7C7B;border-radius:4px;height:6px;width:{pct}%;"></div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.caption(
            "🔢 Exact Deterministic Search: Evaluates all 3⁶ = 729 zone package combinations."
        )

    # ── Run Portfolio Optimization ──────────────────────────────────────
    current_result = solve_portfolio(projects_df, budget_crore, objective_id)
    explanation = generate_portfolio_explanation(current_result, zones_df, projects_df)
    selected_df = current_result["selected_projects"]

    # ── Executive KPI Metrics ───────────────────────────────────────────
    st.markdown(section_header_html("📊", "Executive Summary"), unsafe_allow_html=True)
    render_kpi_metrics(current_result, len(zones_df))

    # ── Spatial & Breakdown Analytics ───────────────────────────────────
    st.markdown("")  # Spacer
    col_map, col_charts = st.columns([7, 5])

    with col_map:
        st.markdown(
            section_header_html("📍", "Geospatial Allocation Map"),
            unsafe_allow_html=True,
        )
        render_spatial_view(zones_df, selected_df)

    with col_charts:
        st.markdown(
            section_header_html("📊", "Portfolio Analytics"),
            unsafe_allow_html=True,
        )
        render_score_breakdown(current_result["score_breakdown"])
        render_budget_donut(
            current_result["total_cost_crore"],
            current_result["budget_remaining_crore"],
        )

    # ── Selected Portfolio Table & Export ────────────────────────────────
    st.markdown(
        section_header_html("📋", "Selected Adaptation Portfolio"),
        unsafe_allow_html=True,
    )
    table_df = render_selected_portfolio_table(selected_df, explanation["summary"])
    render_portfolio_export(table_df, objective_id, budget_crore)

    # ── Transparent Explanations ────────────────────────────────────────
    with st.expander("🔍 Transparent Selection & Exclusion Explanations", expanded=False):
        st.markdown("#### Selected Package Contributions")
        for item in explanation["selected_explanations"]:
            st.markdown(
                f"- **{item['project_id']} — {item['project_name']}** ({item['zone_label']}): "
                f"**₹{item['cost_crore']:.2f} Cr** | {item['score_contribution_narrative']}\n\n"
                f"  *Rationale:* {item['rationale']} *(Source: {item['source_note']})*"
            )

        st.markdown("---")
        st.markdown("#### Excluded Package Rationale")
        for item in explanation["unselected_explanations"]:
            st.markdown(
                f"- **{item['project_id']} — {item['project_name']}** ({item['zone_label']}): "
                f"**₹{item['cost_crore']:.2f} Cr** | {item['reason']}"
            )

    # ── Multi-Scenario Policy Comparison ────────────────────────────────
    st.markdown(
        section_header_html("⚖️", "Multi-Scenario Policy Comparison"),
        unsafe_allow_html=True,
    )
    st.markdown(
        f"Comparing optimal adaptation portfolios across all four policy presets at the current "
        f"**₹{budget_crore:.1f} Crore** budget:"
    )

    scenario_rows = []
    for p_key, p_name in PRESET_DISPLAY_NAMES.items():
        res = solve_portfolio(projects_df, budget_crore, p_key)
        scenario_rows.append(
            {
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
            }
        )

    scenario_df = render_scenario_comparison(scenario_rows, budget_crore)
    render_scenario_export(scenario_df, budget_crore)

    # ── Baseline Datasets & Methodology ─────────────────────────────────
    st.markdown(
        section_header_html("📚", "Baseline Datasets & Methodology"),
        unsafe_allow_html=True,
    )
    render_dataset_tabs(zones_df, projects_df)


if __name__ == "__main__":
    main()
