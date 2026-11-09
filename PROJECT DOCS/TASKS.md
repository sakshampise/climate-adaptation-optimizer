# Master Task Backlog & Implementation Tracker (`TASKS.md`)

**Project:** Pune Climate Optimizer — AI-Assisted Climate Adaptation Investment Prioritization  
**Target Geography:** Pune, Maharashtra, India  
**Governance Model:** Two-Agent Model (ChatGPT + Antigravity with Human Lead Oversight)  
**Reference Date:** November 5, 2026  
**Status:** Active Master Backlog (Reconciled with Two-Agent Transition)

---

## 1. Master Task Schedule

| Task ID | Task Description | Owner | Priority | Target Deadline | Status | Dependencies |
|---|---|---|---|---|---|---|
| **M1-T1** | Project baseline setup, repository initialization, and documentation suite | Antigravity | P0 | 2026-11-03 | **Completed** | None |
| **M1-T2** | Canonical data fixtures creation (`data/reference/`: 6 zones, 12 projects, sources) | Human / Antigravity | P0 | 2026-11-03 | **Completed** | M1-T1 |
| **M1-T3** | Schema ingestion and strict boundary validation module (`src/data_loader.py`) | Antigravity | P0 | 2026-11-03 | **Completed** | M1-T2 |
| **M1-T4** | Data loader unit test suite with 100% boundary check coverage | Antigravity | P0 | 2026-11-03 | **Completed** | M1-T3 |
| **M1-T5** | Initial Streamlit interactive prototype skeleton (`app.py`) | Antigravity | P1 | 2026-11-03 | **Completed** | M1-T3 |
| **M2-T1** | Exact portfolio optimization engine with budget and GUB exclusivity constraints | Antigravity | P0 | 2026-11-04 | **Completed** | M1-T3 |
| **M2-T2** | Objective presets and normalized multi-criteria weighting formulation | ChatGPT / Antigravity | P0 | 2026-11-04 | **Completed** | M2-T1 |
| **M2-T3** | Optimizer unit test suite (budget boundaries, feasibility, deterministic tie-breaking) | Antigravity | P0 | 2026-11-04 | **Completed** | M2-T1 |
| **M3-T1** | Deterministic trade-off and allocation rationale engine (`src/explanations.py`) | Antigravity | P1 | 2026-11-05 | **Completed** | M2-T1 |
| **M3-T2** | Geospatial visualization with graceful tabular fallback (`src/map_view.py`) | Antigravity | P1 | 2026-11-05 | **Completed** | M1-T2 |
| **M3-T3** | Multi-scenario comparison matrix and CSV export in prototype `app.py` | Antigravity | P0 | 2026-11-05 | **Completed** | M2-T1, M3-T1 |
| **M3-T4** | Independent mathematical model audit | Gemini (Audit) / ChatGPT (Review) | P0 | 2026-11-05 | **Reviewed (Formal Supervisor Sign-Off Record Pending)** | M2-T1, M2-T2 |
| **M3-T5** | UI component audit, bug fixes (Plotly import, zero budget, source note) & regression tests | Antigravity | P1 | 2026-11-05 | **Completed (Report Filed, 27/27 Tests Passing)** | M3-T3 |
| **M4-T1** | Formal review & revision of ADR-009 (Scoped UI Component Decomposition) | Human Lead / ChatGPT | P1 | 2026-11-07 | **Approved** | ADR-009 |
| **M4-T2** | Standalone risk model calculation submodule (`src/risk_model/`) | ChatGPT / Antigravity | P1 | 2026-11-07 | **Deferred (Out of Scope for M4)** | M3-T4, M4-T1 |
| **M4-T3** | Decomposition of monolithic `app.py` into modular Streamlit `components/` | ChatGPT / Antigravity | P1 | 2026-11-08 | **Completed (Modularized into components/, 84/84 Tests Passing)** | M3-T5, M4-T1 |
| **M4-T4** | End-to-end regression testing and integration test hardening | Antigravity | P0 | 2026-11-08 | **Completed (24-Scenario Equivalence Verified, 84/84 Passing)** | M4-T2, M4-T3 |
| **M5-T1** | Clean environment deployment verification and packaging audit | Antigravity | P0 | 2026-11-09 | **Active / Handover Ready** | M4-T4 |
| **M5-T2** | Presentation slide deck, demonstration script, and civic impact briefing | Human Lead / All | P0 | 2026-11-10 | **Pending** | M5-T1 |

---

## 2. Milestone Summary & Progress State (as of November 9, 2026)

### Milestone 1: Baseline Setup & Data Foundation
- **Target Deadline:** November 3, 2026
- **Status:** **100% Complete**
- **Artifacts:** `PROJECT DOCS/`, `data/reference/`, `src/data_loader.py`, `tests/test_data_loader.py`.

### Milestone 2: Portfolio Optimization Engine
- **Target Deadline:** November 4, 2026
- **Status:** **100% Complete**
- **Artifacts:** `src/optimizer.py`, `tests/test_optimizer.py`. Exact search over 729 portfolios operational.

### Milestone 3: Explanations, Analytics & Validation
- **Target Deadline:** November 5–6, 2026
- **Status:** **100% Complete**
- **Completed Deliverables:** Working prototype implementations of explanations, map rendering, multi-scenario comparisons, CSV export.
- **Audit Review Status (M3-T4):** Gemini's audit proposal reviewed by ChatGPT; verified exact optimization and mutual exclusivity already exist. Multiplicative risk proposal rejected for frozen MVP (additive model retained).
- **UI Audit & Bug Fixes (M3-T5):** Completed by Antigravity; fixed missing `plotly.graph_objects as go` import, enabled zero-budget slider bound (`min_value=0.0`), preserved `source_note` in table and CSV export, PR merged into `main`.

### Milestone 4: Architecture Modularization & Feature Freeze
- **Target Deadline:** November 7–8, 2026
- **Status:** **100% Complete**
- **Completed Deliverables:** ADR-009 Part A implemented. Presentation decomposed into `components/portfolio.py`, `components/analytics.py`, `components/provenance.py`, `components/exports.py`. `app.py` converted into thin application orchestrator. Created `tests/test_ui_equivalence.py` and `tests/fixtures/m4_baseline_oracle.json` verifying all 24 scenarios with 84/84 passing pytest tests. Core engine files remain strictly frozen.

### Milestone 5: Submission & Presentation Readiness
- **Target Deadline:** November 9–10, 2026
- **Status:** **Active / Video Team Handover Ready**
- **Focus:** Video recording, demonstration script execution, and final submission packaging.
