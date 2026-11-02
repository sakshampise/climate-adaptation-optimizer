"""AI-Assisted Climate Adaptation Investment Prioritization — Streamlit Application

PCCOE International Grand Challenge 2026
Theme: AI for Climate Change
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_loader import load_inputs, DataValidationError
from src.optimizer import solve_portfolio, OBJECTIVE_WEIGHTS, PRESET_DISPLAY_NAMES
from src.explanations import generate_portfolio_explanation
from src.map_view import (
    render_spatial_view,
    render_score_breakdown_chart,
    render_budget_utilization_chart,
)


st.set_page_config(
    page_title="Pune Climate Adaptation Investment Prioritization",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_dataset():
    """Cached loader for zone and project data fixtures."""
    return load_inputs("data")


def main():
    # Application Header
    st.title("🌱 AI-Assisted Climate Adaptation Investment Prioritization")
    st.caption("PCCOE International Grand Challenge 2026 | Theme: AI for Climate Change")
    st.markdown(
        "**Core Question:** *Where should the next ₹10 Crore go to make Pune more climate-resilient?*"
    )

    # Provenance Notice Banner
    st.info(
        "ℹ️ **Data Provenance & Policy Notice:** All baseline indicators, project candidate packages, "
        "and costs are currently configured with **simulated/illustrative** planning values for prototype "
        "evaluation. The system functions as a transparent, multi-criteria decision-support aid. Final "
        "capital deployment remains in the authority of municipal stakeholders."
    )

    # Ingest and validate data
    try:
        zones_df, projects_df = load_dataset()
    except DataValidationError as err:
        st.error(f"❌ Data Validation Error: {err}")
        st.stop()
    except Exception as exc:
        st.error(f"❌ Unexpected Error Loading Data: {exc}")
        st.stop()

    # Sidebar: Planning Controls
    st.sidebar.header("🎯 Municipal Planning Parameters")

    budget_crore = st.sidebar.slider(
        "Total Adaptation Budget (₹ Crore)",
        min_value=1.0,
        max_value=15.0,
        value=10.0,
        step=0.5,
        help="Target municipal capital allocation budget for the planning cycle.",
    )

    preset_keys = list(OBJECTIVE_WEIGHTS.keys())
    preset_labels = [PRESET_DISPLAY_NAMES[k] for k in preset_keys]

    selected_label = st.sidebar.selectbox(
        "Policy Priority Preset",
        options=preset_labels,
        index=2,  # Default to 'Balanced Resilience'
        help="Selects the normative multi-criteria weighting scheme.",
    )

    # Reverse lookup key from label
    objective_id = preset_keys[preset_labels.index(selected_label)]
    active_weights = OBJECTIVE_WEIGHTS[objective_id]

    # Display active weights in sidebar expander
    with st.sidebar.expander("⚖️ Active Weight Distribution", expanded=False):
        for dim, weight in active_weights.items():
            st.write(f"- **{dim.title()}:** `{weight:.2f}` ({int(weight*100)}%)")

    st.sidebar.markdown("---")
    st.sidebar.caption("Exact Deterministic Search: Evaluates all 3⁶ = 729 zone package combinations.")

    # 1. Run Portfolio Optimization for Current Selection
    current_result = solve_portfolio(projects_df, budget_crore, objective_id)
    explanation = generate_portfolio_explanation(current_result, zones_df, projects_df)
    selected_df = current_result["selected_projects"]

    # 2. Executive Metrics Row
    num_selected = len(current_result["selected_project_ids"])
    total_cost = current_result["total_cost_crore"]
    total_score = current_result["total_score"]
    rem_budget = current_result["budget_remaining_crore"]
    feasible_count = current_result["feasible_portfolio_count"]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Funded Planning Areas", f"{num_selected} / {len(zones_df)}", help="Number of zones allocated an intervention")
    with kpi2:
        st.metric("Total Capital Allocated", f"₹{total_cost:.2f} Cr", delta=f"-₹{rem_budget:.2f} Cr remaining", delta_color="normal")
    with kpi3:
        st.metric("Resilience Points Score", f"{total_score:.2f} pts", help="Additive multi-criteria planning score")
    with kpi4:
        st.metric("Feasible Portfolios", f"{feasible_count} / {current_result['combinations_evaluated']}", help="Portfolios within budget limit")

    # 3. Spatial & Breakdown Analytics Layout
    col_map, col_charts = st.columns([7, 5])

    with col_map:
        st.subheader("📍 Geospatial Allocation Map")
        render_spatial_view(zones_df, selected_df)

    with col_charts:
        st.subheader("📊 Portfolio Breakdown")
        render_score_breakdown_chart(current_result["score_breakdown"])
        render_budget_utilization_chart(total_cost, rem_budget)

    # 4. Optimal Portfolio Projects Table & CSV Export
    st.subheader("📋 Selected Adaptation Portfolio")
    st.markdown(f"**Optimization Result:** {explanation['summary']}")

    if not selected_df.empty:
        # Format table for display
        table_df = selected_df[[
            "project_id", "zone_id", "project_name", "intervention_type",
            "cost_crore", "flood_benefit_score", "heat_benefit_score",
            "equity_benefit_score", "infrastructure_benefit_score", "urgency_score",
            "evidence_quality", "data_status"
        ]].copy()
        table_df.columns = [
            "Project ID", "Zone ID", "Project Package", "Type",
            "Cost (₹ Cr)", "Flood Pts", "Heat Pts", "Equity Pts",
            "Infra Pts", "Urgency", "Evidence", "Status"
        ]
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        # CSV Export button for the selected portfolio
        csv_data = table_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Selected Portfolio (CSV)",
            data=csv_data,
            file_name=f"pune_climate_portfolio_{objective_id}_{budget_crore:.1f}cr.csv",
            mime="text/csv",
        )
    else:
        st.warning("⚠️ No projects could be funded under the entered budget. Consider increasing the available budget.")

    # 5. Deterministic Explanations Section
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

    # 6. Multi-Scenario Comparison across all 4 Presets at Current Budget
    st.markdown("---")
    st.subheader("⚖️ Multi-Scenario Policy Comparison")
    st.markdown(
        f"Comparing optimal adaptation investment portfolios across all four policy presets under the current "
        f"**₹{budget_crore:.1f} Crore** budget allocation:"
    )

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

    scenario_df = pd.DataFrame(scenario_rows)
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

    # Scenario CSV Export
    scenario_csv = scenario_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Scenario Comparison Matrix (CSV)",
        data=scenario_csv,
        file_name=f"pune_climate_scenarios_{budget_crore:.1f}cr.csv",
        mime="text/csv",
    )

    # 7. Underlying Data Explorer Tabs
    st.markdown("---")
    st.subheader("📚 Baseline Datasets & Methodology")
    tab_z, tab_p = st.tabs(["📍 6 Planning Zones (Baseline)", "🛠️ 12 Intervention Packages (Catalog)"])

    with tab_z:
        st.dataframe(zones_df, use_container_width=True, hide_index=True)

    with tab_p:
        st.dataframe(projects_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
