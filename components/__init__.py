"""Streamlit UI Presentation Components for Pune Climate Adaptation Optimizer.

Decomposed presentation modules conforming to ADR-009 Part A:
- portfolio: Executive KPI cards and selected portfolio table rendering.
- analytics: Score breakdown bar, budget donut, and multi-scenario comparison.
- provenance: Prototype policy banner, live climate context card, and fixture explorer tabs.
- exports: RFC-4180 CSV export payload generation and download buttons.
"""

from .portfolio import (
    render_kpi_metrics,
    render_selected_portfolio,
    format_portfolio_table,
    PORTFOLIO_COLUMN_MAP,
)
from .analytics import (
    render_score_breakdown,
    render_budget_donut,
    render_scenario_comparison,
    build_scenario_comparison_df,
)
from .provenance import (
    render_provenance_banner,
    render_live_climate_card,
    render_nasa_climatology_card,
    render_dataset_tabs,
)
from .exports import (
    render_portfolio_export_button,
    render_scenario_export_button,
    generate_portfolio_csv,
    generate_scenario_csv,
)

__all__ = [
    "render_kpi_metrics",
    "render_selected_portfolio",
    "format_portfolio_table",
    "PORTFOLIO_COLUMN_MAP",
    "render_score_breakdown",
    "render_budget_donut",
    "render_scenario_comparison",
    "build_scenario_comparison_df",
    "render_provenance_banner",
    "render_live_climate_card",
    "render_nasa_climatology_card",
    "render_dataset_tabs",
    "render_portfolio_export_button",
    "render_scenario_export_button",
    "generate_portfolio_csv",
    "generate_scenario_csv",
]
