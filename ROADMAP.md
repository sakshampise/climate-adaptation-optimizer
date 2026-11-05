# AI-Assisted Climate Adaptation Investment Prioritization — Project Roadmap

**Hackathon Theme:** AI for Climate Change — *PCCOE International Grand Challenge 2026*  
**Core Problem Statement:** *Where should the next ₹10 Crore (or municipal adaptation tranche) go to maximize climate resilience across vulnerable urban areas in Pune?*

---

## 1. Project Vision & Governance

The platform provides a transparent, mathematically rigorous decision-support tool for municipal policymakers, urban planners, and disaster management cells. It avoids black-box generative assumptions, relying instead on deterministic multi-criteria optimization, strict data provenance labeling, and explainable trade-off analytics.

---

## 2. Agreed MVP Scope Boundary

The Minimum Viable Product (MVP) is strictly bounded by the following commitments:
- **Application Interface:** Single-page interactive [Streamlit](https://streamlit.io/) dashboard.
- **Geographic Coverage:** Six representative, illustrative Pune planning areas (`Z01`–`Z06`) with verified centroid coordinates and simulated planning indicators.
- **Intervention Inventory:** Twelve adaptation intervention packages (`P01`–`P12`), offering exactly two mutually exclusive alternatives per planning area (e.g., Nature-Based Solutions vs. Grey Engineering).
- **Hazard Focus:** Multi-hazard modeling focusing on Monsoon Flooding and Extreme Urban Heat, combined with socioeconomic vulnerability and critical infrastructure sensitivity.
- **Objective Presets:** Four deterministic policy presets:
  1. *Flood Priority* (60% Flood weight)
  2. *Heat Priority* (60% Heat weight)
  3. *Balanced Resilience* (35% Flood, 35% Heat)
  4. *Social & Climate Equity* (50% Equity weight)
- **Mathematical Optimization:** Exact budget-constrained 0-1 integer linear programming / combinatorial search over the $3^6 = 729$ candidate portfolio space with deterministic tie-breaking (cost minimization, then lexicographical ID).
- **Explainability & Export:** Deterministic trade-off explanations, investment rationale, budget utilization breakdown, and standard CSV portfolio export.

---

## 3. Milestones & Delivery Schedule

```
[Milestone 1: Data & Baseline] ──> [Milestone 2: Optimization Engine] ──> [Milestone 3: Explanations & Viz]
                                                                                   │
[Milestone 5: Submission & Demo] <── [Milestone 4: Streamlit Integration & Scenarios] ┘
```

### Milestone 1: Baseline Setup & Data Foundation
- **Goal:** Establish reliable repository baseline, versioned schemas, data provenance framework, and input validation.
- **Deliverables:**
  - Standardized repository documentation (`CONTEXT.md`, `ROADMAP.md`, `TASKS.md`, `DECISIONS.md`, `CHANGELOG.md`).
  - Canonical data fixtures: `data/zones.csv` (6 zones) and `data/projects.csv` (12 interventions).
  - Provenance catalog in `data/sources.md` with explicit data status classifications (`verified`, `derived`, `simulated`).
  - Schema ingestion and integrity validation module (`src/data_loader.py`).
  - Unit test suite for schema enforcement and data boundary rules (`tests/test_data_loader.py`).

### Milestone 2: Mathematical Optimization Engine
- **Goal:** Build the deterministic multi-criteria portfolio optimization engine.
- **Deliverables:**
  - Optimization module (`src/optimizer.py`) supporting exact search and PuLP solver integration.
  - Hard constraint enforcement:
    - Capital budget ceiling $\sum x_p \cdot c_p \le B$.
    - Mutually exclusive choice per zone $\sum_{p \in Z_i} x_p \le 1$.
    - Feasibility filter $x_p \in \{0, 1\}$ with $x_p = 0$ if unfeasible.
  - Policy preset matrix defining normalized weights across 5 resilience criteria.
  - Deterministic tie-breaking logic (lower cost first, then lexicographical order).
  - Optimizer unit test suite covering boundary budgets, edge cases, and hand-computed scenarios (`tests/test_optimizer.py`).

### Milestone 3: Explanations, Analytics & Visualizations
- **Goal:** Translate mathematical solutions into transparent narratives, geospatial maps, and comparison charts.
- **Deliverables:**
  - Rationale generator (`src/explanations.py`) producing structured, hallucination-free explanations of selected packages and exclusion causes (budget limit, zone exclusivity, low objective rank).
  - Spatial visualization module (`src/map_view.py`) rendering interactive maps with fallback tables for offline/restricted environments.
  - Multi-criteria score decomposition and budget utilization charts using Plotly.
  - Acceptance tests for explanation structure and trade-off logic (`tests/test_explanations.py`).

### Milestone 4: Streamlit Application & Multi-Scenario Comparison
- **Goal:** Assemble the complete user-facing interactive decision platform.
- **Deliverables:**
  - Interactive Streamlit frontend (`app.py`) featuring:
    - Dynamic budget slider with currency formatting in Indian Rupees Crore (₹ Cr).
    - Objective preset selector with immediate reactive recalculation.
    - Portfolio summary metrics (Total Resilience Score, Capital Invested, Remaining Budget, Projects Deployed).
    - Side-by-side scenario comparison table contrasting all 4 policy presets at the chosen budget.
    - Export button for one-click CSV download of optimized allocations.
  - End-to-end integration and smoke tests (`tests/test_integration.py`).

### Milestone 5: Submission Hardening & Presentation Readiness
- **Goal:** Verify end-to-end quality, code hygiene, and presentation alignment for the PCCOE Grand Challenge.
- **Deliverables:**
  - End-to-end test run with 100% test pass rate across all modules.
  - Clean environment replication verification (install from `requirements.txt`).
  - Demo script and presentation slide alignment documenting methodology, mathematical rigor, and civic impact.

---

## 4. Technical Architecture Interfaces

| Module | Primary Interface | Inputs | Outputs |
|---|---|---|---|
| `src/data_loader.py` | `load_inputs(data_dir: str)` | Directory containing CSVs | `tuple[pd.DataFrame, pd.DataFrame]` (zones, projects) |
| `src/optimizer.py` | `solve_portfolio(projects, budget, objective)` | Projects DataFrame, budget (₹ Cr), preset ID | Dict with `selected_projects`, `total_cost`, `total_score`, etc. |
| `src/explanations.py` | `generate_portfolio_explanation(result, zones, projects)` | Optimization result dict, DataFrames | Structured dict with highlights, trade-offs, and exclusion reasons |
| `src/map_view.py` | `render_spatial_view(zones, selected_ids)` | Zones DataFrame, list of selected IDs | PyDeck / Plotly map figure or display container |
| `app.py` | Streamlit Application Main Loop | User inputs (budget slider, preset radio) | Rendered dashboard, metrics, charts, tables, CSV export |

---

## 5. Risk Assessment & Mitigations

| Risk | Impact | Mitigation Strategy |
|---|---|---|
| Unverified data presented as factual | High (Misleading civic claims) | Strict 3-tier provenance classification (`verified`, `derived`, `simulated`) displayed in UI and CSV exports. |
| Non-deterministic optimization outputs | High (Inconsistent municipal advice) | Guaranteed exact combinatorial evaluation over all 729 states with strict deterministic tie-breakers. |
| Map rendering failure in offline environments | Medium (Broken UI during judging) | Dual-layer visualization: Interactive map with automatic graceful fallback to formatted tabular summaries. |
| Budget infeasibility or zero allocation | Low (User confusion) | Explicit handling of sub-minimum budgets with actionable UI warnings and recommendations. |

---

## 6. Post-MVP Future Horizons (Out of Scope for Hackathon)

The following capabilities are reserved for Phase 2 and are intentionally excluded from the hackathon release:
- Integration with live PMC GIS layers, sensor streams, and automatic weather stations.
- Continuous hydrological hydrodynamic modeling (e.g., SWMM / HEC-RAS coupling).
- Machine learning surrogate models for multi-decade climate projection uncertainty.
- Multi-year phased capital budgeting with discount rates and operational expenditure (OPEX) tracking.
