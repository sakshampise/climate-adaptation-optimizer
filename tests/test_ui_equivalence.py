"""M4-T3 Behavioral Equivalence Test Suite across 24 Pre-Refactor Scenarios.

Verifies that portfolio selection, costs, scores, remaining budgets,
exclusion reason classifications, selected portfolio CSV exports, and
multi-scenario comparison matrices match the frozen pre-refactor golden oracle.
"""

import json
import os
from pathlib import Path
import pandas as pd
import pytest
from src.data_loader import load_inputs
from src.optimizer import solve_portfolio, OBJECTIVE_WEIGHTS, PRESET_DISPLAY_NAMES
from src.explanations import generate_portfolio_explanation

ORACLE_PATH = Path("tests/fixtures/m4_baseline_oracle.json")


@pytest.fixture(scope="session")
def oracle_data():
    """Load pre-refactor golden baseline oracle."""
    assert ORACLE_PATH.exists(), f"Oracle file not found at {ORACLE_PATH}"
    with open(ORACLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def datasets():
    """Load canonical zones and projects datasets."""
    zones_df, projects_df = load_inputs("data")
    return zones_df, projects_df


# 24 scenarios: 4 presets x 6 budgets
BUDGETS = [0.0, 1.4, 15.0, 30.0, 50.0, 100.0]
PRESETS = list(OBJECTIVE_WEIGHTS.keys())
SCENARIO_KEYS = [f"{preset}_{budget}cr" for budget in BUDGETS for preset in PRESETS]


@pytest.mark.parametrize("scenario_key", SCENARIO_KEYS)
def test_optimizer_and_explanation_equivalence(scenario_key, oracle_data, datasets):
    """Verify that solver outputs and explanations match the frozen golden oracle."""
    expected = oracle_data[scenario_key]
    zones_df, projects_df = datasets

    preset_id = expected["preset_id"]
    budget_crore = expected["budget_crore"]

    res = solve_portfolio(projects_df, budget_crore, preset_id)
    exp = generate_portfolio_explanation(res, zones_df, projects_df)

    # 1. Selected Project IDs
    assert res["selected_project_ids"] == expected["selected_project_ids"]

    # 2. Total Cost
    assert res["total_cost_crore"] == pytest.approx(expected["total_cost_crore"], abs=1e-4)

    # 3. Remaining Budget
    assert res["budget_remaining_crore"] == pytest.approx(expected["budget_remaining_crore"], abs=1e-4)

    # 4. Total Score
    assert res["total_score"] == pytest.approx(expected["total_score"], abs=1e-4)

    # 5. Score Breakdown
    for dim, score_val in expected["score_breakdown"].items():
        assert res["score_breakdown"][dim] == pytest.approx(score_val, abs=1e-4)

    # 6. Exclusion Reasons per project
    actual_reasons = {
        item["project_id"]: item["reason_type"]
        for item in exp["unselected_explanations"]
    }
    assert actual_reasons == expected["unselected_reasons"]

    # 7. Summary Narrative
    assert exp["summary"] == expected["summary_narrative"]


@pytest.mark.parametrize("scenario_key", SCENARIO_KEYS)
def test_selected_portfolio_export_equivalence(scenario_key, oracle_data, datasets):
    """Verify that selected portfolio table columns and CSV export match the golden oracle."""
    expected = oracle_data[scenario_key]
    _, projects_df = datasets

    res = solve_portfolio(projects_df, expected["budget_crore"], expected["preset_id"])
    selected_df = res["selected_projects"]

    if selected_df.empty:
        assert expected["portfolio_csv"] == ""
    else:
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
        actual_csv = table_df.to_csv(index=False)
        assert actual_csv == expected["portfolio_csv"]


@pytest.mark.parametrize("budget", BUDGETS)
def test_scenario_comparison_matrix_equivalence(budget, oracle_data, datasets):
    """Verify that multi-scenario comparison matrix and CSV export match golden oracle."""
    _, projects_df = datasets
    reference_key = f"balanced_{budget}cr"
    expected_scenario_csv = oracle_data[reference_key]["scenario_csv"]

    scenario_rows = []
    for p_key, p_name in PRESET_DISPLAY_NAMES.items():
        res = solve_portfolio(projects_df, budget, p_key)
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
    actual_scenario_csv = scenario_df.to_csv(index=False)

    assert actual_scenario_csv == expected_scenario_csv
