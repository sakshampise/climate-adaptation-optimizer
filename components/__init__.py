"""Streamlit UI Presentation Components for Pune Climate Adaptation Optimizer.

Decomposed presentation modules conforming to ADR-009 Part A:
- portfolio: Executive KPI cards and selected portfolio table rendering.
- analytics: Score breakdown bar, budget donut, and multi-scenario comparison.
- provenance: Prototype policy banner, live climate context card, and fixture explorer tabs.
- exports: RFC-4180 CSV export payload generation and download buttons.
- styles: Design tokens, color palette, custom CSS, and HTML card helpers.
"""

from .portfolio import (
    render_kpi_metrics,
    render_selected_portfolio,
    render_selected_portfolio_table,
    format_portfolio_table,
    PORTFOLIO_COLUMN_MAP,
)
from .analytics import (
    render_score_breakdown,
    render_budget_donut,
    render_scenario_comparison,
    build_scenario_comparison_df,
    build_scenario_comparison_chart,
)
from .provenance import (
    render_provenance_banner,
    render_live_climate_card,
    render_dataset_tabs,
)
from .exports import (
    render_portfolio_export,
    render_scenario_export,
    render_portfolio_export_button,
    render_scenario_export_button,
    generate_portfolio_csv,
    generate_scenario_csv,
)
from .styles import (
    COLORS,
    DIMENSION_COLORS,
    DIMENSION_LABELS,
    DIMENSION_ICONS,
    inject_custom_css,
    kpi_card_html,
    section_header_html,
)

__all__ = [
    # portfolio
    "render_kpi_metrics",
    "render_selected_portfolio",
    "render_selected_portfolio_table",
    "format_portfolio_table",
    "PORTFOLIO_COLUMN_MAP",
    # analytics
    "render_score_breakdown",
    "render_budget_donut",
    "render_scenario_comparison",
    "build_scenario_comparison_df",
    "build_scenario_comparison_chart",
    # provenance
    "render_provenance_banner",
    "render_live_climate_card",
    "render_dataset_tabs",
    # exports
    "render_portfolio_export",
    "render_scenario_export",
    "render_portfolio_export_button",
    "render_scenario_export_button",
    "generate_portfolio_csv",
    "generate_scenario_csv",
    # styles
    "COLORS",
    "DIMENSION_COLORS",
    "DIMENSION_LABELS",
    "DIMENSION_ICONS",
    "inject_custom_css",
    "kpi_card_html",
    "section_header_html",
]
