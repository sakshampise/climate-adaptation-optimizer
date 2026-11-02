"""Unit tests for the explanations module."""

import pytest
from src.data_loader import load_inputs
from src.optimizer import solve_portfolio
from src.explanations import generate_portfolio_explanation


@pytest.fixture
def test_setup():
    zones_df, projects_df = load_inputs("data")
    return zones_df, projects_df


def test_explanation_structure(test_setup):
    """Verify that generate_portfolio_explanation returns required keys and non-empty narratives."""
    zones_df, projects_df = test_setup
    res = solve_portfolio(projects_df, budget_crore=10.0, objective_id="balanced")
    exp = generate_portfolio_explanation(res, zones_df, projects_df)

    assert "summary" in exp
    assert "selected_explanations" in exp
    assert "unselected_explanations" in exp
    assert "trade_off_analysis" in exp

    assert len(exp["selected_explanations"]) == len(res["selected_project_ids"])
    assert len(exp["selected_explanations"]) + len(exp["unselected_explanations"]) == len(projects_df)

    for item in exp["selected_explanations"]:
        assert "project_id" in item
        assert "score_contribution_narrative" in item
        assert "source_note" in item
        assert item["cost_crore"] > 0

    for item in exp["unselected_explanations"]:
        assert "reason" in item
        assert "reason_type" in item
        assert item["reason_type"] in {
            "infeasible",
            "same_zone_alternative_chosen",
            "budget_exceeded",
            "portfolio_tradeoff",
        }


def test_zero_budget_explanation(test_setup):
    """Zero budget should yield zero selected and valid explanations for all unselected."""
    zones_df, projects_df = test_setup
    res = solve_portfolio(projects_df, budget_crore=0.0, objective_id="flood")
    exp = generate_portfolio_explanation(res, zones_df, projects_df)

    assert len(exp["selected_explanations"]) == 0
    assert len(exp["unselected_explanations"]) == len(projects_df)
    assert "0 planning zones" in exp["summary"]
