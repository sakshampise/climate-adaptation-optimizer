"""Unit tests for the portfolio optimizer module.

Verifies mathematical correctness, constraint satisfaction, and tie-breaking against
the specifications in CONTEXT.md and PROJECT_SPEC.md.
"""

import pytest
import pandas as pd
from src.data_loader import load_inputs
from src.optimizer import solve_portfolio, OBJECTIVE_WEIGHTS, compute_project_score


@pytest.fixture
def baseline_data():
    """Loads validated baseline dataset."""
    zones_df, projects_df = load_inputs("data")
    return zones_df, projects_df


def test_zero_budget_returns_empty_portfolio(baseline_data):
    """Zero budget must select no projects and return zero cost and zero score."""
    _, projects_df = baseline_data
    result = solve_portfolio(projects_df, budget_crore=0.0, objective_id="balanced")

    assert result["selected_project_ids"] == []
    assert result["total_cost_crore"] == 0.0
    assert result["total_score"] == 0.0
    assert result["budget_remaining_crore"] == 0.0
    assert result["selected_projects"].empty
    # Even with budget 0, exactly 1 combination (all None) is feasible
    assert result["feasible_portfolio_count"] >= 1
    assert result["combinations_evaluated"] == 3**6  # 729 combinations


def test_invalid_parameters_raise_value_error(baseline_data):
    """Negative budgets or invalid objective IDs must raise ValueError."""
    _, projects_df = baseline_data

    with pytest.raises(ValueError, match="negative"):
        solve_portfolio(projects_df, budget_crore=-5.0, objective_id="balanced")

    with pytest.raises(ValueError, match="finite"):
        solve_portfolio(projects_df, budget_crore=float("nan"), objective_id="balanced")

    with pytest.raises(ValueError, match="Unknown objective_id"):
        solve_portfolio(projects_df, budget_crore=10.0, objective_id="nonexistent_preset")


def test_never_exceeds_budget(baseline_data):
    """For any budget, the total selected cost must never exceed the budget."""
    _, projects_df = baseline_data
    for test_budget in [1.5, 3.0, 5.0, 7.5, 10.0]:
        result = solve_portfolio(projects_df, budget_crore=test_budget, objective_id="balanced")
        assert result["total_cost_crore"] <= test_budget + 1e-9
        assert result["budget_remaining_crore"] >= -1e-9


def test_at_most_one_project_per_zone(baseline_data):
    """Selected portfolio must never contain more than one project from any zone."""
    _, projects_df = baseline_data
    # Use very large budget so all zones could potentially have a selection
    result = solve_portfolio(projects_df, budget_crore=50.0, objective_id="balanced")
    selected_df = result["selected_projects"]

    assert not selected_df.empty
    zone_counts = selected_df["zone_id"].value_counts()
    for count in zone_counts:
        assert count <= 1


def test_infeasible_projects_are_never_selected():
    """Projects marked feasible=False must never be selected."""
    _, projects_df = load_inputs("data")
    modified_projects = projects_df.copy()
    # Mark all projects infeasible except one cheap project
    modified_projects["feasible"] = False
    modified_projects.loc[modified_projects["project_id"] == "P09", "feasible"] = True

    result = solve_portfolio(modified_projects, budget_crore=10.0, objective_id="balanced")
    assert result["selected_project_ids"] == ["P09"]


def test_exact_budget_selection():
    """A project costing exactly the budget can be selected."""
    # Handcrafted 2-zone fixture
    df = pd.DataFrame([
        {
            "project_id": "PA1",
            "zone_id": "Z01",
            "project_name": "Package A1",
            "intervention_type": "drainage",
            "cost_crore": 5.0,
            "feasible": True,
            "flood_benefit_score": 80,
            "heat_benefit_score": 40,
            "equity_benefit_score": 50,
            "infrastructure_benefit_score": 60,
            "urgency_score": 70,
            "evidence_quality": "high",
            "data_status": "simulated",
            "source_note": "Test note",
        },
        {
            "project_id": "PA2",
            "zone_id": "Z01",
            "project_name": "Package A2",
            "intervention_type": "nature",
            "cost_crore": 6.0,
            "feasible": True,
            "flood_benefit_score": 90,
            "heat_benefit_score": 50,
            "equity_benefit_score": 50,
            "infrastructure_benefit_score": 60,
            "urgency_score": 70,
            "evidence_quality": "high",
            "data_status": "simulated",
            "source_note": "Test note",
        },
    ])

    # Exactly 5.0 budget should select PA1
    res = solve_portfolio(df, budget_crore=5.0, objective_id="flood")
    assert res["selected_project_ids"] == ["PA1"]
    assert res["total_cost_crore"] == 5.0
    assert res["budget_remaining_crore"] == 0.0

    # Budget 4.9 should select neither
    res_under = solve_portfolio(df, budget_crore=4.9, objective_id="flood")
    assert res_under["selected_project_ids"] == []


def test_hand_computable_fixture_exactness():
    """Verifies that an independent manual hand-calculation matches the optimizer."""
    # 2 zones, each with 2 projects
    # Zone 1: P1 (cost 2, flood 90, heat 10), P2 (cost 3, flood 10, heat 90)
    # Zone 2: P3 (cost 2, flood 80, heat 20), P4 (cost 3, flood 20, heat 80)
    # Equity, infra, urgency = 0 for simplicity
    weights_flood = OBJECTIVE_WEIGHTS["flood"]  # flood: 0.60, heat: 0.10
    # Score(P1) = 0.60*90 + 0.10*10 = 54 + 1 = 55
    # Score(P2) = 0.60*10 + 0.10*90 = 6 + 9 = 15
    # Score(P3) = 0.60*80 + 0.10*20 = 48 + 2 = 50
    # Score(P4) = 0.60*20 + 0.10*80 = 12 + 8 = 20

    test_df = pd.DataFrame([
        {
            "project_id": "P1", "zone_id": "Z1", "project_name": "P1", "intervention_type": "typeA",
            "cost_crore": 2.0, "feasible": True, "flood_benefit_score": 90, "heat_benefit_score": 10,
            "equity_benefit_score": 0, "infrastructure_benefit_score": 0, "urgency_score": 0,
            "evidence_quality": "high", "data_status": "simulated", "source_note": "note",
        },
        {
            "project_id": "P2", "zone_id": "Z1", "project_name": "P2", "intervention_type": "typeB",
            "cost_crore": 3.0, "feasible": True, "flood_benefit_score": 10, "heat_benefit_score": 90,
            "equity_benefit_score": 0, "infrastructure_benefit_score": 0, "urgency_score": 0,
            "evidence_quality": "high", "data_status": "simulated", "source_note": "note",
        },
        {
            "project_id": "P3", "zone_id": "Z2", "project_name": "P3", "intervention_type": "typeA",
            "cost_crore": 2.0, "feasible": True, "flood_benefit_score": 80, "heat_benefit_score": 20,
            "equity_benefit_score": 0, "infrastructure_benefit_score": 0, "urgency_score": 0,
            "evidence_quality": "high", "data_status": "simulated", "source_note": "note",
        },
        {
            "project_id": "P4", "zone_id": "Z2", "project_name": "P4", "intervention_type": "typeB",
            "cost_crore": 3.0, "feasible": True, "flood_benefit_score": 20, "heat_benefit_score": 80,
            "equity_benefit_score": 0, "infrastructure_benefit_score": 0, "urgency_score": 0,
            "evidence_quality": "high", "data_status": "simulated", "source_note": "note",
        },
    ])

    # With budget 4.0 under flood preset, optimal is {P1, P3}
    # Cost = 2.0 + 2.0 = 4.0
    # Score = 55.0 + 50.0 = 105.0
    # Total combinations = 3 * 3 = 9
    res = solve_portfolio(test_df, budget_crore=4.0, objective_id="flood")
    assert res["selected_project_ids"] == ["P1", "P3"]
    assert res["total_cost_crore"] == 4.0
    assert res["total_score"] == 105.0
    assert res["combinations_evaluated"] == 9
    assert res["score_breakdown"]["flood"] == round(0.60 * (90 + 80), 4)
    assert res["score_breakdown"]["heat"] == round(0.10 * (10 + 20), 4)

    # Now test with heat preset:
    # weights_heat: flood 0.10, heat 0.60
    # Score(P1) = 0.10*90 + 0.60*10 = 9 + 6 = 15
    # Score(P2) = 0.10*10 + 0.60*90 = 1 + 54 = 55 (cost 3)
    # Score(P3) = 0.10*80 + 0.60*20 = 8 + 12 = 20 (cost 2)
    # Score(P4) = 0.10*20 + 0.60*80 = 2 + 48 = 50 (cost 3)
    # With budget 3.0, optimal single project under heat is P2 (score 55, cost 3)
    res_heat = solve_portfolio(test_df, budget_crore=3.0, objective_id="heat")
    assert res_heat["selected_project_ids"] == ["P2"]
    assert res_heat["total_score"] == 55.0
    assert res_heat["total_cost_crore"] == 3.0


def test_tie_breaking_rules():
    """Verify tie-breaking: prefer lower cost, then lexicographical order."""
    # Two projects with identical score, but P_CHEAP costs 2.0 and P_EXP costs 3.0
    tie_cost_df = pd.DataFrame([
        {
            "project_id": "P_EXP", "zone_id": "Z1", "project_name": "Expensive", "intervention_type": "typeA",
            "cost_crore": 3.0, "feasible": True, "flood_benefit_score": 50, "heat_benefit_score": 50,
            "equity_benefit_score": 50, "infrastructure_benefit_score": 50, "urgency_score": 50,
            "evidence_quality": "high", "data_status": "simulated", "source_note": "note",
        },
        {
            "project_id": "P_CHEAP", "zone_id": "Z1", "project_name": "Cheap", "intervention_type": "typeB",
            "cost_crore": 2.0, "feasible": True, "flood_benefit_score": 50, "heat_benefit_score": 50,
            "equity_benefit_score": 50, "infrastructure_benefit_score": 50, "urgency_score": 50,
            "evidence_quality": "high", "data_status": "simulated", "source_note": "note",
        },
    ])

    res = solve_portfolio(tie_cost_df, budget_crore=5.0, objective_id="balanced")
    assert res["selected_project_ids"] == ["P_CHEAP"]
    assert res["total_cost_crore"] == 2.0

    # Now two projects in different zones with identical score and identical cost
    # Lexicographical tie break should prefer P_ALPHA over P_BETA if budget only allows one
    tie_lex_df = pd.DataFrame([
        {
            "project_id": "P_BETA", "zone_id": "Z1", "project_name": "Beta", "intervention_type": "typeA",
            "cost_crore": 2.0, "feasible": True, "flood_benefit_score": 50, "heat_benefit_score": 50,
            "equity_benefit_score": 50, "infrastructure_benefit_score": 50, "urgency_score": 50,
            "evidence_quality": "high", "data_status": "simulated", "source_note": "note",
        },
        {
            "project_id": "P_ALPHA", "zone_id": "Z2", "project_name": "Alpha", "intervention_type": "typeB",
            "cost_crore": 2.0, "feasible": True, "flood_benefit_score": 50, "heat_benefit_score": 50,
            "equity_benefit_score": 50, "infrastructure_benefit_score": 50, "urgency_score": 50,
            "evidence_quality": "high", "data_status": "simulated", "source_note": "note",
        },
    ])

    res_lex = solve_portfolio(tie_lex_df, budget_crore=2.0, objective_id="balanced")
    assert res_lex["selected_project_ids"] == ["P_ALPHA"]


def test_preset_changes_portfolio(baseline_data):
    """Different presets should change scoring and portfolio priorities."""
    _, projects_df = baseline_data
    # Compare flood priority vs heat priority at budget 6.0
    res_flood = solve_portfolio(projects_df, budget_crore=6.0, objective_id="flood")
    res_heat = solve_portfolio(projects_df, budget_crore=6.0, objective_id="heat")

    # The chosen project sets should differ reflecting the respective hazard priority
    assert res_flood["selected_project_ids"] != res_heat["selected_project_ids"]
    assert res_flood["objective_id"] == "flood"
    assert res_heat["objective_id"] == "heat"
