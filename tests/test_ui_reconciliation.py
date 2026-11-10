"""Tests for reconciled UI components, design tokens, and backward-compatible interfaces.

Task: M5-UI-Reconciliation
Validates the reconciled design system from components.styles and verifies
backward-compatible adapters for Ayush's PR #2 component interfaces.
"""

import pandas as pd
import pytest
from src.data_loader import load_inputs
from src.optimizer import solve_portfolio
import components.styles as cs
import components.portfolio as cp
import components.analytics as ca
import components.provenance as cprov
import components.exports as ce
import components as c


def test_styles_palette_and_dimensions_defined():
    """Verify color tokens and dimension mappings in components.styles."""
    required_colors = ["primary", "accent", "warning", "danger", "text_primary", "bg_card", "border"]
    for color in required_colors:
        assert color in cs.COLORS
        assert cs.COLORS[color].startswith("#")

    dimensions = ["flood", "heat", "equity", "infrastructure", "urgency"]
    for dim in dimensions:
        assert dim in cs.DIMENSION_COLORS
        assert dim in cs.DIMENSION_LABELS
        assert dim in cs.DIMENSION_ICONS


def test_kpi_card_html_generation():
    """Verify kpi_card_html produces expected HTML structure."""
    html = cs.kpi_card_html(
        label="Test Metric",
        value="42",
        subtitle="Test Subtitle",
        icon="🎯",
        color="#0E7C7B",
    )
    assert "class=\"kpi-card\"" in html
    assert "Test Metric" in html
    assert "42" in html
    assert "Test Subtitle" in html
    assert "🎯" in html
    assert "border-left: 4px solid #0E7C7B;" in html


def test_section_header_html_generation():
    """Verify section_header_html produces expected HTML markup."""
    html = cs.section_header_html("📊", "Analytics Overview")
    assert "class=\"section-header\"" in html
    assert "📊" in html
    assert "Analytics Overview" in html


def test_reconciled_component_exports():
    """Verify that all core and reconciled interfaces are accessible from top-level package."""
    assert hasattr(c, "COLORS")
    assert hasattr(c, "inject_custom_css")
    assert hasattr(c, "kpi_card_html")
    assert hasattr(c, "section_header_html")

    # Ayush PR #2 adapters
    assert hasattr(c, "render_selected_portfolio_table")
    assert hasattr(c, "render_portfolio_export")
    assert hasattr(c, "render_scenario_export")

    # M4-T3 / M5 contracts
    assert hasattr(c, "render_kpi_metrics")
    assert hasattr(c, "render_selected_portfolio")
    assert hasattr(c, "format_portfolio_table")
    assert hasattr(c, "render_score_breakdown")
    assert hasattr(c, "render_budget_donut")
    assert hasattr(c, "render_scenario_comparison")
    assert hasattr(c, "build_scenario_comparison_df")
    assert hasattr(c, "render_provenance_banner")
    assert hasattr(c, "render_live_climate_card")
    assert hasattr(c, "render_dataset_tabs")
    assert hasattr(c, "generate_portfolio_csv")
    assert hasattr(c, "generate_scenario_csv")


def test_portfolio_table_backward_compatibility():
    """Verify render_selected_portfolio_table helper returns formatted DataFrame."""
    _, projects_df = load_inputs("data")
    res = solve_portfolio(projects_df, budget_crore=10.0, objective_id="balanced")
    selected_df = res["selected_projects"]

    table_df = cp.render_selected_portfolio_table(selected_df, "Test summary")
    assert isinstance(table_df, pd.DataFrame)
    assert not table_df.empty
    assert "Project Package" in table_df.columns
    assert "Cost (₹ Cr)" in table_df.columns
    assert "Status" in table_df.columns
    assert "Source Note" in table_df.columns

    # Test with empty selection
    empty_df = cp.render_selected_portfolio_table(pd.DataFrame(), "No projects funded")
    assert isinstance(empty_df, pd.DataFrame)
    assert empty_df.empty


def test_scenario_comparison_dual_signature_compatibility():
    """Verify render_scenario_comparison works with both canonical projects_df and precomputed rows."""
    _, projects_df = load_inputs("data")

    # 1. Calling with canonical projects_df (existing pattern)
    df1 = ca.render_scenario_comparison(projects_df, budget_crore=10.0)
    assert isinstance(df1, pd.DataFrame)
    assert len(df1) == 4
    assert "Policy Preset" in df1.columns
    assert "Total Score (pts)" in df1.columns

    # 2. Calling with precomputed list of dicts (Ayush PR #2 pattern)
    scenario_rows = df1.to_dict(orient="records")
    df2 = ca.render_scenario_comparison(scenario_rows, budget_crore=10.0)
    assert isinstance(df2, pd.DataFrame)
    assert len(df2) == 4
    assert list(df1["Total Score (pts)"]) == list(df2["Total Score (pts)"])


def test_export_null_safe_guards():
    """Verify render_portfolio_export and render_scenario_export handle None and empty gracefully."""
    # Should not raise exception
    ce.render_portfolio_export(None, "balanced", 10.0)
    ce.render_portfolio_export(pd.DataFrame(), "balanced", 10.0)
    ce.render_scenario_export(None, 10.0)
    ce.render_scenario_export(pd.DataFrame(), 10.0)


def test_dual_yaxis_scenario_chart_structure():
    """Verify that build_scenario_comparison_chart constructs clean dual Y-axes for mixed units."""
    _, projects_df = load_inputs("data")
    scenario_df = ca.build_scenario_comparison_df(projects_df, budget_crore=10.0)
    fig = ca.build_scenario_comparison_chart(scenario_df)

    # 1. Verify trace presence, ordering, and names
    assert len(fig.data) == 2
    assert fig.data[0].name == "Total Resilience Score"
    assert fig.data[1].name == "Capital Cost (₹ Cr)"

    # 2. Verify dual Y-axis separation
    assert fig.data[0].yaxis == "y"
    assert fig.data[1].yaxis == "y2"

    # 3. Verify distinct axis titles for points vs currency
    assert "Relative Points" in fig.layout.yaxis.title.text
    assert "Crore" in fig.layout.yaxis2.title.text

    # 4. Verify non-overlapping bar offset groups
    assert fig.data[0].offsetgroup != fig.data[1].offsetgroup


