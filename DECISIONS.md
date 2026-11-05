# Architecture Decision Records (ADRs)

Project: **AI-Assisted Climate Adaptation Investment Prioritization for Pune**  
Theme: **AI for Climate Change — PCCOE International Grand Challenge 2026**

This document records the architectural and design decisions made for the project, following the standard Architecture Decision Record (ADR) format.

---

## Index of Decisions

- [ADR-001: Selection of Streamlit as Primary Application Framework](#adr-001-selection-of-streamlit-as-primary-application-framework)
- [ADR-002: Deterministic Mathematical Optimization over Black-Box AI](#adr-002-deterministic-mathematical-optimization-over-black-box-ai)
- [ADR-003: Strict Three-Tier Data Provenance Taxonomy (`verified`, `derived`, `simulated`)](#adr-003-strict-three-tier-data-provenance-taxonomy-verified-derived-simulated)
- [ADR-004: Mutually Exclusive Interventions per Zone (Multiple-Choice Knapsack Problem)](#adr-004-mutually-exclusive-interventions-per-zone-multiple-choice-knapsack-problem)
- [ADR-005: Deterministic Tie-Breaking Strategy for Optimal Portfolios](#adr-005-deterministic-tie-breaking-strategy-for-optimal-portfolios)
- [ADR-006: Rule-Based Explanations over Generative Large Language Models for Core Decisions](#adr-006-rule-based-explanations-over-generative-large-language-models-for-core-decisions)
- [ADR-007: Version-Controlled CSV Data Fixtures with Strict Schema Validation](#adr-007-version-controlled-csv-data-fixtures-with-strict-schema-validation)
- [ADR-008: Dual-Mode Spatial Visualization with Tabular Graceful Fallback](#adr-008-dual-mode-spatial-visualization-with-tabular-graceful-fallback)
- [ADR-009: Proposal for Application Modularization and Submodule Architecture](#adr-009-proposal-for-application-modularization-and-submodule-architecture)

---

## ADR-001: Selection of Streamlit as Primary Application Framework

### Context
Municipal decision-makers require an intuitive, reactive, and presentation-ready web interface to adjust capital budgets, switch policy presets, inspect trade-offs, and export findings during hackathon evaluation. The framework must support Python-native integration with numerical optimization and visualization libraries without heavyweight frontend-backend build infrastructure.

### Decision
Adopt **Streamlit** (Python) as the single-process application stack.

### Consequences
- **Positive:** Rapid reactive UI updates, zero JavaScript/CSS build dependencies, seamless rendering of Pandas DataFrames, Plotly charts, and PyDeck maps, clean deployment.
- **Negative:** Limited custom state management compared to full React/Node setups; acceptable for a focused decision-support tool.

### Status
Accepted and Implemented.

---

## ADR-002: Deterministic Mathematical Optimization over Black-Box AI

### Context
Public climate adaptation spending of crores of rupees requires transparent, auditable, and reproducible decisions. Using generative LLMs or opaque neural networks to select project portfolios introduces risks of non-deterministic outputs, hallucinations, and unprovable trade-offs.

### Decision
Formulate the portfolio allocation problem as a **deterministic 0-1 Integer Linear Program (Multiple-Choice Knapsack Problem)**:
$$\max \sum_{p \in P} x_p \cdot \text{score}(p)$$
subject to:
1. $\sum_{p \in P} x_p \cdot \text{cost\_crore}(p) \le \text{budget\_crore}$
2. $\sum_{p \in P_z} x_p \le 1 \quad \forall z \in Z$
3. $x_p \in \{0, 1\}$ and $x_p = 0$ if $\text{feasible}(p) = \text{False}$

For the 6-zone MVP ($3^6 = 729$ candidate combinations), solve via provably exact combinatorial enumeration with PuLP formulation compatibility.

### Consequences
- **Positive:** 100% reproducibility, guaranteed global optimality, mathematical defensibility for municipal audits.
- **Negative:** Combinatorial explosion for hundreds of zones (can be transitioned to Branch-and-Cut integer solvers in Phase 2).

### Status
Accepted and Implemented.

---

## ADR-003: Strict Three-Tier Data Provenance Taxonomy (`verified`, `derived`, `simulated`)

### Context
Hackathons often suffer from ungrounded synthetic data presented as factual reality. For urban resilience planning, presenting simulated risk indices as verified municipal statistics damages credibility.

### Decision
Enforce a mandatory `data_status` column in all data tables using a strict three-tier classification:
1. `verified`: Ground-truth data sourced directly from official municipal, state, or national records (e.g., official census records, validated coordinates).
2. `derived`: Statistically or mathematically computed from verified base metrics using published methodologies.
3. `simulated`: Realistic, literature-informed illustrative estimates generated specifically for prototype modeling and testing.

Every dataset must include a corresponding `source_note` explaining its derivation or literature reference. The UI must prominently flag simulated data.

### Consequences
- **Positive:** Uncompromising civic data ethics, complete transparency, protects project from false accuracy claims.
- **Negative:** Requires rigorous labeling and validation for every row in data fixtures.

### Status
Accepted and Implemented.

---

## ADR-004: Mutually Exclusive Interventions per Zone (Multiple-Choice Knapsack Problem)

### Context
In any single municipal zone (e.g., Sangamwadi river confluence), committing to two large conflicting adaptation interventions (e.g., large-scale wetland restoration vs. massive hard-engineered floodwalls occupying the same riverfront) can cause site conflict, double-counting of benefits, and inefficient capital allocation.

### Decision
Model projects under Generalized Upper Bound (GUB) constraints: each zone $z$ has candidate projects $P_z$, and at most one project may be selected from $P_z$:
$$\sum_{p \in P_z} x_p \le 1 \quad \forall z \in Z$$
The decision for zone $z$ is either Project A, Project B, or No Project (deferred investment).

### Consequences
- **Positive:** Mirrors realistic municipal capital programming where competing master plans must choose between distinct intervention strategies.
- **Negative:** Restricts combining multiple small modular interventions in the same zone within the MVP scope.

### Status
Accepted and Implemented.

---

## ADR-005: Deterministic Tie-Breaking Strategy for Optimal Portfolios

### Context
When optimizing across multi-criteria scoring functions, multiple portfolio combinations may achieve the exact same maximum resilience score. Without a deterministic tie-breaker, the returned solution may fluctuate based on internal iteration order, non-deterministic sets, or platform differences.

### Decision
Adopt a two-tier deterministic tie-breaking hierarchy:
1. **Cost Minimization (Efficiency):** Between portfolios with identical total resilience score, choose the portfolio with lower total cost (preserving municipal capital).
2. **Lexicographical Order (Determinism):** If still tied, sort the selected project IDs in ascending alphanumeric order and select the lexicographically smaller portfolio tuple.

### Consequences
- **Positive:** Guarantees bitwise-identical results across Python versions, operating systems, and repeated executions.
- **Negative:** None.

### Status
Accepted and Implemented.

---

## ADR-006: Rule-Based Explanations over Generative Large Language Models for Core Decisions

### Context
Decision-makers need to know *why* a project was selected or rejected. Relying on an ungrounded generative LLM prompt introduces latency, external API dependencies, token costs, and potential hallucinations of non-existent budget trade-offs.

### Decision
Implement `src/explanations.py` using deterministic, rule-based narrative templates that directly query the optimization results, zone attributes, and policy weights.
Specifically categorize exclusions into:
- **Budget Exceeded:** Cost exceeds remaining allocatable budget.
- **Zone Exclusivity Conflict:** An alternative project in the same zone provided higher score per rupee.
- **Objective Weight Mismatch:** Project scored low on dimensions emphasized by the selected preset.

### Consequences
- **Positive:** Instantaneous generation (< 5 ms), 100% grounded in model outputs, zero API token cost, completely testable via unit tests.
- **Negative:** Output follows structured templates rather than conversational variability.

### Status
Accepted and Implemented.

---

## ADR-007: Version-Controlled CSV Data Fixtures with Strict Schema Validation

### Context
The MVP requires 6 illustrative zones and 12 intervention packages. Introducing an external SQL or NoSQL database adds setup friction, network dependencies, and deployment overhead for hackathon judges.

### Decision
Store canonical data in flat, version-controlled CSV files (`data/zones.csv`, `data/projects.csv`) and validate schemas strictly at ingestion time via `src/data_loader.py`.
The validator strictly checks:
- Required column presence and exact data types.
- Key uniqueness (`zone_id`, `project_id`).
- Foreign key integrity (`projects.zone_id` $\in$ `zones.zone_id`).
- Value range constraints ($0 \le \text{index} \le 100$, $\text{cost} > 0$).
- Geographic coordinates within plausible Pune bounding boxes.

### Consequences
- **Positive:** Frictionless setup (`git clone` and run), zero database provisioning, human-readable inspection.
- **Negative:** Not designed for live multi-user write transactions (not required for MVP decision support).

### Status
Accepted and Implemented.

---

## ADR-008: Dual-Mode Spatial Visualization with Tabular Graceful Fallback

### Context
Streamlit spatial mapping components (e.g. PyDeck, Folium, Scattermapbox) can fail in environments with restricted WebGL support, air-gapped corporate firewalls, or headless test runners.

### Decision
Implement `src/map_view.py` with dual-mode rendering:
1. Attempt interactive map rendering showing zone markers colored by hazard and selection status.
2. If map rendering raises an exception or the user opts for tabular view, immediately display a styled, comprehensive spatial breakdown table.

### Consequences
- **Positive:** Zero risk of blank screens or crashed UI during jury demonstrations.
- **Negative:** Dual rendering code paths to maintain.

### Status
Accepted and Implemented.

---

## ADR-009: Proposal for Application Modularization and Submodule Architecture

### Context
The application originated as an end-to-end prototype with modules situated directly at the root of `src/` (`src/data_loader.py`, `src/optimizer.py`, `src/explanations.py`, `src/map_view.py`) and a single script entry point (`app.py`).

During workspace organization, a scalable target directory hierarchy was established:
- `src/data_processing/`: Ingestion, schema validation, and normalization.
- `src/risk_model/`: Standalone calculations for multi-hazard, exposure, and vulnerability indices.
- `src/optimizer/`: Combinatorial and integer linear programming portfolio solvers.
- `src/utils/`: Shared narrative generators, formatting, and spatial visualizers.
- `components/`: Modular, reusable Streamlit UI widgets (`metric_cards.py`, `scenario_table.py`, `charts.py`, `provenance_banner.py`).

To prevent breaking existing test imports during initial workspace organization, temporary mirror files and re-export `__init__.py` bridges were introduced:
- `src/data_loader.py` and `src/data_processing/loader.py`
- `src/optimizer.py` and `src/optimizer/portfolio_optimizer.py`
- `src/explanations.py` & `src/map_view.py` and `src/utils/`

This duality creates temporary file duplication and technical debt that must be resolved systematically.

### Proposed Future Structure

1. **Source Package Migration:**
   - Migrate `src/data_loader.py` exclusively to `src/data_processing/loader.py`.
   - Introduce standalone composite risk calculations in `src/risk_model/engine.py` (incorporating Gemini's mathematical audit).
   - Retain optimizer logic in `src/optimizer/portfolio_optimizer.py` with clean public API exposed via `src/optimizer/__init__.py`.
   - House narrative explanations and spatial map renderers in `src/utils/`.
2. **UI Component Decomposition:**
   - Deconstruct monolithic rendering blocks in `app.py` into dedicated modules in `components/`:
     - `components/metric_cards.py`: Portfolio summary KPI cards.
     - `components/scenario_table.py`: 4-preset comparative matrix rendering.
     - `components/charts.py`: Plotly multi-criteria radar and budget breakdown charts.
     - `components/provenance_banner.py`: Standardized 3-tier data provenance badges and disclaimers.
   - Refactor `app.py` to act strictly as a thin orchestrator.
3. **Data Path Canonicalization:**
   - Update data loader default path to point to `data/reference/`.

### Benefits and Risks

- **Benefits:**
  - **High Cohesion & Separation of Concerns:** UI rendering separated from core mathematical optimization and data processing.
  - **Reusability & Testability:** UI components and risk algorithms can be tested independently with isolated mocks.
  - **Clean Team Division:** ChatGPT can work on `components/`, Gemini on `src/risk_model/` and `src/optimizer/`, Antigravity on test hardening.
- **Risks:**
  - **Import Breakages:** Tests currently import from `src.data_loader`, `src.optimizer`, `src.explanations`. Removing root modules abruptly without compatibility shims would cause test collection failures.
  - **Regression Risk:** Moving rendering logic from `app.py` into `components/` could introduce Streamlit session state or reactivity regressions.

### Potential Impact on Existing Imports and Tests
- All test files (`tests/test_data_loader.py`, `tests/test_optimizer.py`, `tests/test_explanations.py`, `tests/test_integration.py`) must either:
  1. Be updated to import from the new modular subpackages (`src.data_processing`, `src.optimizer`, `src.utils`), OR
  2. Be supported via clean backwards-compatibility aliases in `src/__init__.py`.
- Refactoring must only take place in a dedicated milestone with 100% test pass verification after each atomic step.

### Status
**PROPOSED — NOT APPROVED.** Implementation is deferred until formal approval by the team.

