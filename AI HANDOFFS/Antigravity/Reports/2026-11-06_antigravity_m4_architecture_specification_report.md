# Milestone 4 Architecture Review & Implementation Specification
## UI Component Decomposition & Feature Freeze Specification

- **Milestone:** M4 — Architecture Modularization & Feature Freeze
- **Task ID:** M4-T1 / M4-T3
- **Date:** 2026-11-06
- **Author:** Antigravity (Primary Implementation Agent)
- **Technical Supervisor:** ChatGPT (Project Architect)
- **Final Authority:** Human Project Lead
- **Status:** **Specification Prepared — Awaiting Human Approval**
- **Active Branch:** `feature/m3-t5-ui-review`

---

## 1. Executive Summary & Precondition Audit

This document defines the minimal, low-risk architecture review and implementation specification for decomposing the Streamlit application (`app.py`) into modular presentation components.

### Mandatory Precondition Check
1. **M3-T5 Branch Inspection:** Inspected branch `feature/m3-t5-ui-review` (Commit `bff857f`). All verified M3-T5 findings are fully incorporated:
   - Missing `import plotly.graph_objects as go` fixed in `app.py`.
   - Zero-budget planning bound `min_value=0.0` enabled.
   - Provenance `source_note` preserved in table and CSV export.
   - Dedicated regression suite in `tests/test_ui_regression.py` passing.
   - Full test suite passes: **27/27 tests passing in 18.08s**.
2. **PR Status & Blocker Report:** Branch `feature/m3-t5-ui-review` is committed locally. Because Git Credential Manager on Windows requires interactive browser authentication when communicating with the private remote, pushing requires running `git push -u origin feature/m3-t5-ui-review` in an interactive terminal.
3. **Current Authorization:** Planning and specification are authorized. **No refactoring, file migrations, optimizer modifications, or ADR-009 implementations have been performed.** Code changes remain gated on explicit Human Project Lead approval.

---

## 2. Revised ADR-009 Governance Structure

ADR-009 in [`PROJECT DOCS/DECISIONS.md`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/PROJECT%20DOCS/DECISIONS.md) has been revised to decouple three independent concerns:

```
                               ┌────────────────────────────────────────────────────────┐
                               │                    REVISED ADR-009                     │
                               └──────────────────────────┬─────────────────────────────┘
                                                          │
          ┌───────────────────────────────────────────────┼──────────────────────────────────────────────┐
          │                                               │                                              │
          ▼                                               ▼                                              ▼
┌───────────────────────────────┐           ┌───────────────────────────────┐          ┌───────────────────────────────┐
│     PART A: UI DECOMPOSITION  │           │   PART B: CORE MIGRATION      │          │   PART C: STANDALONE RISK     │
│   (PROPOSED FOR APPROVAL)     │           │         (DEFERRED)            │          │         (DEFERRED)            │
├───────────────────────────────┤           ├───────────────────────────────┤          ├───────────────────────────────┤
│ • Extract presentation logic  │           │ • Retain src/data_loader.py   │          │ • No new composite risk model │
│   into 4 components/ modules  │           │ • Retain src/optimizer.py     │          │ • Retain additive scoring     │
│ • app.py as thin orchestrator │           │ • Retain src/explanations.py  │          │ • Exclude multiplicative risk │
│ • Preserve src/map_view.py    │           │ • Retain src/map_view.py      │          │ • Requires future formal spec │
└───────────────────────────────┘           └───────────────────────────────┘          └───────────────────────────────┘
```

---

## 3. Component Architecture & Responsibility Map

```mermaid
flowchart TD
    subgraph UI Orchestrator
        APP["app.py (Orchestrator)"]
    end

    subgraph Data & Optimization Engine [src/ - Unchanged]
        DL["src/data_loader.py<br/>(load_inputs)"]
        OPT["src/optimizer.py<br/>(solve_portfolio)"]
        EXP["src/explanations.py<br/>(generate_portfolio_explanation)"]
        MAP["src/map_view.py<br/>(render_spatial_view)"]
    end

    subgraph Modular Presentation Components [components/ - Proposed]
        PORT["components/portfolio.py<br/>• render_kpi_metrics()<br/>• render_selected_table()"]
        ANL["components/analytics.py<br/>• render_score_breakdown()<br/>• render_budget_donut()<br/>• render_scenario_matrix()"]
        PROV["components/provenance.py<br/>• render_provenance_banner()<br/>• render_dataset_tabs()"]
        EXP_UI["components/exports.py<br/>• render_portfolio_export()<br/>• render_scenario_export()"]
    end

    APP --> DL
    APP --> OPT
    APP --> EXP
    APP --> MAP

    APP --> PROV
    APP --> PORT
    APP --> ANL
    APP --> EXP_UI
```

### Module Responsibilities:

| Module | Exact Responsibilities | Public Function Signatures |
|---|---|---|
| **`components/portfolio.py`** | Executive KPI metric cards and selected adaptation package table formatting. | `render_kpi_metrics(result: dict, zones_count: int) -> None`<br>`render_selected_table(selected_df: pd.DataFrame, explanation_summary: str) -> pd.DataFrame` |
| **`components/analytics.py`** | Criteria breakdown horizontal bar, budget utilization donut, and 4-preset comparison grouped bar chart. | `render_breakdown_charts(score_breakdown: dict, total_cost: float, rem_budget: float) -> None`<br>`render_scenario_comparison(projects_df: pd.DataFrame, budget_crore: float) -> pd.DataFrame` |
| **`components/provenance.py`** | Header notice declaring simulated data status and baseline fixture explorer tabs. | `render_provenance_banner() -> None`<br>`render_dataset_tabs(zones_df: pd.DataFrame, projects_df: pd.DataFrame) -> None` |
| **`components/exports.py`** | CSV encoding and download buttons with mandatory provenance preservation (`data_status`, `source_note`). | `render_portfolio_export(table_df: pd.DataFrame, objective_id: str, budget_crore: float) -> None`<br>`render_scenario_export(scenario_df: pd.DataFrame, budget_crore: float) -> None` |
| **`app.py`** | Page configuration, sidebar inputs (budget slider, preset selectbox), solver invocation, and top-level layout. | `main() -> None` |

---

## 4. File-Level Implementation Plan

### Step 1: `components/provenance.py` (Lines ~41–47, ~245–255 of `app.py`)
- Extract `render_provenance_banner()`: Renders `st.info` with explicit prototype disclaimer.
- Extract `render_dataset_tabs(zones_df, projects_df)`: Renders tabs for 6 Planning Zones and 12 Intervention Packages.

### Step 2: `components/portfolio.py` (Lines ~98–114, ~127–146 of `app.py`)
- Extract `render_kpi_metrics(current_result, total_zones)`: Renders 4 `st.metric` cards (Funded Areas, Capital Allocated, Resilience Points, Feasible Count).
- Extract `render_selected_table(selected_df, summary)`: Formats and renders `table_df` including `"Source Note"` and `"Status"`. Returns `table_df` for export.

### Step 3: `components/exports.py` (Lines ~147–154, ~236–243 of `app.py`)
- Extract `render_portfolio_export(table_df, objective_id, budget_crore)`: Renders download button for selected portfolio CSV.
- Extract `render_scenario_export(scenario_df, budget_crore)`: Renders download button for scenario comparison CSV.

### Step 4: `components/analytics.py` (Lines ~122–126, ~175–235 of `app.py`)
- Extract `render_breakdown_charts(score_breakdown, total_cost, rem_budget)`: Calls `render_score_breakdown_chart()` and `render_budget_utilization_chart()`.
- Extract `render_scenario_comparison(projects_df, budget_crore)`: Evaluates all 4 presets under identical budget, renders summary table, and builds grouped `go.Figure()` comparison chart.

### Step 5: `app.py` Clean Orchestration
- Reduces `app.py` to ~80 lines: loads datasets, captures sidebar inputs, solves active portfolio, calls spatial map, and invokes the 4 components.

---

## 5. Acceptance Criteria (M4-AC01 to M4-AC10)

| Criterion | Requirement | Verification Method |
|---|---|---|
| **M4-AC01 — Behavioral Equivalence** | Exact match in selected projects, scores, and costs pre- vs post-refactor. | Automated regression test asserting identical dictionary output from `solve_portfolio()`. |
| **M4-AC02 — Optimizer Integrity** | Zero changes to `src/optimizer.py`, weights, or tie-breaking logic. | `git diff src/optimizer.py` must return empty; `tests/test_optimizer.py` (9/9 pass). |
| **M4-AC03 — UI Correctness** | All 9 MVP sections remain available and render identically. | Visual layout verification and component import assertions. |
| **M4-AC04 — Budget Boundaries** | Zero budget (0.0 Cr), low budget (1.4 Cr), and normal budgets work cleanly. | `test_zero_budget_pipeline_behavior()` in `tests/test_ui_regression.py`. |
| **M4-AC05 — Provenance** | Exports preserve `data_status` and `source_note`. | `test_export_preserves_source_note_and_provenance()` passes. |
| **M4-AC06 — Scenario Comparison** | All 4 presets evaluated at identical budget. | `test_scenario_comparison_chart_construction()` passes. |
| **M4-AC07 — Map Fallback** | Retains tabular fallback in `src/map_view.py` on map rendering failure. | `test_data_loader.py` and `src/map_view.py` exception handling verified. |
| **M4-AC08 — Import Stability** | All existing public imports (`src.data_loader`, `src.optimizer`, etc.) work unchanged. | Zero test import modifications; full suite passes. |
| **M4-AC09 — Regression Tests** | Complete pytest suite passes without regressions. | `pytest` runs with 100% pass rate (27/27 passing). |
| **M4-AC10 — Startup Verification** | Application starts without import errors or exceptions. | Headless Streamlit launch on port 8502 exits cleanly. |

---

## 6. Atomic Implementation Sequence (Gated on Approval)

1. **Gate 1:** Human Project Lead reviews this specification and provides explicit approval.
2. **Step 1:** Create `components/provenance.py` -> run `pytest`.
3. **Step 2:** Create `components/portfolio.py` -> run `pytest`.
4. **Step 3:** Create `components/exports.py` -> run `pytest`.
5. **Step 4:** Create `components/analytics.py` -> run `pytest`.
6. **Step 5:** Refactor `app.py` to import and orchestrate components -> run `pytest`.
7. **Step 6:** Run headless Streamlit startup check.
8. **Step 7:** Run complete 27-test regression suite.
9. **Step 8:** Commit to dedicated branch `feature/m4-ui-modularization` and file dated handoff report.

---

## 7. Current Authorization Gate

**STATUS:** **HOLDING FOR HUMAN PROJECT LEAD APPROVAL**

*In accordance with instructions, no application code has been refactored, no core modules have been moved, and no new packages have been created. Implementation will commence only upon explicit authorization from the Human Project Lead.*
