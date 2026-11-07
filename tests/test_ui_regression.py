"""Regression tests for Streamlit UI logic, Plotly rendering, and export integrity.

Task ID: M3-T5
Scope: Verify UI bug fixes (Plotly go import, zero budget, source_note in export).
"""

import io
import pandas as pd
import pytest
import plotly.graph_objects as go
from src.data_loader import load_inputs
from src.optimizer import solve_portfolio, OBJECTIVE_WEIGHTS, PRESET_DISPLAY_NAMES
from src.explanations import generate_portfolio_explanation
from src.map_view import render_budget_utilization_chart, render_score_breakdown_chart


def test_app_imports_and_plotly_go_defined():
    """Verify that app module imports cleanly and exposes plotly.graph_objects as go."""
    import app
    assert hasattr(app, "go"), "app module must import plotly.graph_objects as go"
    assert app.go is go, "app.go must be plotly.graph_objects"


def test_zero_budget_pipeline_behavior():
    """Verify that zero budget executes safely without exceptions across all presets."""
    zones_df, projects_df = load_inputs("data")

    for preset_id in OBJECTIVE_WEIGHTS:
        res = solve_portfolio(projects_df, budget_crore=0.0, objective_id=preset_id)
        assert res["total_cost_crore"] == 0.0
        assert res["total_score"] == 0.0
        assert res["budget_remaining_crore"] == 0.0
        assert len(res["selected_project_ids"]) == 0
        assert res["selected_projects"].empty

        exp = generate_portfolio_explanation(res, zones_df, projects_df)
        assert "summary" in exp
        assert len(exp["selected_explanations"]) == 0
        assert len(exp["unselected_explanations"]) == 12


def test_export_preserves_source_note_and_provenance():
    """Verify that selected portfolio export preserves source_note, data_status, and all fields."""
    zones_df, projects_df = load_inputs("data")
    res = solve_portfolio(projects_df, budget_crore=10.0, objective_id="balanced")
    selected_df = res["selected_projects"]
    assert not selected_df.empty

    # Replicate app.py export formatting
    table_df = selected_df[[
        "project_id", "zone_id", "project_name", "intervention_type",
        "cost_crore", "flood_benefit_score", "heat_benefit_score",
        "equity_benefit_score", "infrastructure_benefit_score", "urgency_score",
        "evidence_quality", "data_status", "source_note"
    ]].copy()
    table_df.columns = [
        "Project ID", "Zone ID", "Project Package", "Type",
        "Cost (₹ Cr)", "Flood Pts", "Heat Pts", "Equity Pts",
        "Infra Pts", "Urgency", "Evidence", "Status", "Source Note"
    ]

    buf = io.StringIO()
    table_df.to_csv(buf, index=False)
    csv_text = buf.getvalue()

    assert "Source Note" in csv_text
    assert "Status" in csv_text
    assert "simulated" in csv_text
    for note in selected_df["source_note"]:
        assert note in csv_text


def test_scenario_comparison_chart_construction():
    """Verify that multi-scenario bar chart builds using go.Figure and go.Bar without error."""
    zones_df, projects_df = load_inputs("data")
    budget_crore = 10.0

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
        })

    scenario_df = pd.DataFrame(scenario_rows)
    assert len(scenario_df) == 4

    # Build the Plotly figure exactly as in app.py
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
    chart_scenario.update_layout(barmode="group", height=320)

    assert len(chart_scenario.data) == 2
    assert chart_scenario.data[0].name == "Total Resilience Score"
    assert chart_scenario.data[1].name == "Capital Cost (₹ Cr)"


def test_budget_constraints_and_zone_exclusivity_across_budgets():
    """Verify strict budget constraint and mutual exclusivity across range of budgets."""
    _, projects_df = load_inputs("data")

    for budget in [0.0, 1.4, 2.5, 5.0, 8.0, 10.0, 15.0]:
        for preset_id in OBJECTIVE_WEIGHTS:
            res = solve_portfolio(projects_df, budget_crore=budget, objective_id=preset_id)
            assert res["total_cost_crore"] <= budget + 1e-9
            selected_df = res["selected_projects"]

            if not selected_df.empty:
                # Assert at most one project per zone
                assert selected_df["zone_id"].is_unique
                # Assert all selected projects are marked feasible
                assert selected_df["feasible"].all()
