"""End-to-end integration tests for Climate Adaptation Investment Prioritization.

Verifies end-to-end workflow from data ingestion to optimization,
explanation generation, and scenario matrix compilation.
"""

import io
import pandas as pd
from src.data_loader import load_inputs
from src.optimizer import solve_portfolio, OBJECTIVE_WEIGHTS, PRESET_DISPLAY_NAMES
from src.explanations import generate_portfolio_explanation


def test_full_pipeline_end_to_end():
    """Verify that entire workflow runs seamlessly from data loading to CSV export."""
    # 1. Load inputs
    zones_df, projects_df = load_inputs("data")
    assert len(zones_df) == 6
    assert len(projects_df) == 12

    # 2. Test optimization across multiple budgets
    for budget in [3.0, 7.5, 10.0, 12.0]:
        for preset_id in OBJECTIVE_WEIGHTS:
            res = solve_portfolio(projects_df, budget_crore=budget, objective_id=preset_id)

            # Assert constraints
            assert res["total_cost_crore"] <= budget + 1e-9
            assert res["budget_remaining_crore"] >= -1e-9
            assert res["combinations_evaluated"] == 729

            # Assert explanation validity
            exp = generate_portfolio_explanation(res, zones_df, projects_df)
            assert len(exp["summary"]) > 0
            assert len(exp["selected_explanations"]) == len(res["selected_project_ids"])

            # Verify CSV export generation
            if not res["selected_projects"].empty:
                buf = io.StringIO()
                res["selected_projects"].to_csv(buf, index=False)
                exported_csv = buf.getvalue()
                assert "project_id" in exported_csv
                assert "cost_crore" in exported_csv


def test_scenario_comparison_matrix():
    """Verify that multi-scenario comparison compiles correctly for all presets."""
    zones_df, projects_df = load_inputs("data")
    budget = 10.0

    scenario_rows = []
    for p_key, p_name in PRESET_DISPLAY_NAMES.items():
        res = solve_portfolio(projects_df, budget_crore=budget, objective_id=p_key)
        scenario_rows.append({
            "Policy Preset": p_name,
            "Total Score": res["total_score"],
            "Allocated Cost": res["total_cost_crore"],
            "Funded Areas Count": len(res["selected_project_ids"]),
        })

    df = pd.DataFrame(scenario_rows)
    assert len(df) == 4
    assert set(df["Policy Preset"]) == set(PRESET_DISPLAY_NAMES.values())
    assert (df["Allocated Cost"] <= budget).all()
    assert (df["Total Score"] > 0).all()
