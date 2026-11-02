# Implementation Roadmap & Task Backlog (`TASKS.md`)

Master task tracker for the **AI-Assisted Climate Adaptation Investment Prioritization** platform.

---

## Milestone 1: Baseline Setup & Data Foundation (Target: Nov 3)

- [x] **Task 1.1: Project Baseline & Source of Truth**
  - Initialize Git repository.
  - Establish `CONTEXT.md`, `TASKS.md`, `README.md`, `.gitignore`, `requirements.txt`.
  - Status: Completed.

- [ ] **Task 1.2: Data Fixtures Creation**
  - Create `data/zones.csv` with 6 realistic, illustrative Pune planning areas with exact schema.
  - Create `data/projects.csv` with 12 intervention packages (2 mutually exclusive alternatives per zone).
  - Create `data/sources.md` documenting data provenance, assumptions, and coordinate methodology.
  - Status: Pending.

- [ ] **Task 1.3: Data Loader & Schema Validator**
  - Implement `src/data_loader.py` with `load_inputs(data_dir: str)`.
  - Validate column presence, strict types, unique IDs, foreign keys, row counts, ranges (0-100), positive costs.
  - Status: Pending.

- [ ] **Task 1.4: Data Loader Unit Tests**
  - Implement `tests/test_data_loader.py`.
  - Verify valid fixture loading, error reporting for invalid/missing/malformed data.
  - Run and verify all tests pass.
  - Status: Pending.

- [ ] **Task 1.5: Application Skeleton**
  - Create minimal `app.py` with Streamlit.
  - Display project header, data provenance banner, and raw data overview tables.
  - Verify application launches and executes without errors.
  - Status: Pending.

---

## Milestone 2: Portfolio Optimization Engine (Target: Nov 4)

- [ ] **Task 2.1: Mathematical Optimizer Implementation**
  - Implement `src/optimizer.py` with `OBJECTIVE_WEIGHTS` and `solve_portfolio()`.
  - Implement exact enumeration and PuLP-compatible formulation with constraint enforcement (budget, max 1 per zone, feasibility).
  - Implement deterministic tie-breaking (lower cost, then lexicographical order).
  - Status: Pending.

- [ ] **Task 2.2: Optimizer Unit Tests**
  - Implement `tests/test_optimizer.py`.
  - Test zero budget, unconstrained budget, budget tie-breaking, mutually exclusive zone constraint, infeasible project exclusion.
  - Test hand-calculable test cases against verified manual scores.
  - Status: Pending.

---

## Milestone 3: Explanations, Visualizations & Scenarios (Target: Nov 5 - 6)

- [ ] **Task 3.1: Deterministic Explanation Engine**
  - Implement `src/explanations.py` with structured narratives for selected/unselected interventions.
  - Status: Pending.

- [ ] **Task 3.2: Spatial & Comparative Visualizations**
  - Implement `src/map_view.py` with interactive map and robust fallback table.
  - Add Plotly charts for budget allocation and resilience score breakdowns.
  - Status: Pending.

- [ ] **Task 3.3: Multi-Scenario Comparison & CSV Export**
  - Implement side-by-side comparison across 4 presets in `app.py`.
  - Provide CSV download feature.
  - Status: Pending.

---

## Milestone 4: Feature Freeze & Integration Verification (Target: Nov 7 - 8)

- [ ] **Task 4.1: End-to-End Testing & Hardening**
  - Verify full user flow from slider adjustment to scenario export.
  - Ensure zero unhandled exceptions.
  - Status: Pending.

---

## Milestone 5: Submission & Presentation Readiness (Target: Nov 9 - 10)

- [ ] **Task 5.1: Final Rehearsal & Documentation Polish**
  - Verification on clean browser and deployment check.
  - Presentation slide alignment with prototype demo.
  - Status: Pending.
