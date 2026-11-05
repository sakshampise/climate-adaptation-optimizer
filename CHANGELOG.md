# Changelog

All notable changes to the **AI-Assisted Climate Adaptation Investment Prioritization** platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-11-05

### Added
- **Formal Documentation Suite:**
  - `CONTEXT.md` (v1.0): Authoritative project specification, mathematical formulations, data contracts, and guardrails.
  - `ROADMAP.md`: Strategic roadmap spanning 5 milestones from data foundation to hackathon presentation.
  - `TASKS.md`: Task backlog, progress tracker, and verification log.
  - `DECISIONS.md`: Architecture Decision Records (ADR-001 through ADR-008) covering Streamlit UI, exact optimization, provenance taxonomy, GUB knapsack constraints, and fallback strategies.
  - `CHANGELOG.md`: Historical change tracking and version audit trail.
- **Three-Tier Data Provenance System:**
  - Standardized `data_status` taxonomy across all datasets: `verified`, `derived`, and `simulated`.
  - Added `data/sources.md` detailing methodological grounding, coordinate references, and risk indices.

---

## [0.1.3] - 2026-11-04

### Added
- **Deterministic Explanation Engine (`src/explanations.py`):**
  - Rule-based narrative generator explaining portfolio selections, benefit trade-offs, and exclusion reasons (budget ceiling, zone exclusivity, objective misalignment).
  - Unit tests in `tests/test_explanations.py` validating output structure and trade-off summaries.
- **Spatial Mapping & Visualization Module (`src/map_view.py`):**
  - Interactive map visualization for Pune planning zones with status markers.
  - Graceful tabular fallback for headless or restricted WebGL execution environments.
- **Multi-Scenario Comparison & CSV Export in `app.py`:**
  - Side-by-side benchmarking matrix across all 4 policy presets (Flood, Heat, Balanced, Equity).
  - One-click CSV download of optimized portfolio allocations and metrics.
- **Integration Test Suite (`tests/test_integration.py`):**
  - End-to-end testing verifying end-to-end data pipeline from CSV ingestion to optimization, narrative generation, and export readiness.

---

## [0.1.2] - 2026-11-03

### Added
- **Mathematical Optimization Engine (`src/optimizer.py`):**
  - Formulation of multiple-choice budget-constrained portfolio optimization.
  - Implementation of four normalized policy presets (`flood`, `heat`, `balanced`, `equity`).
  - Two-stage deterministic tie-breaker: cost minimization followed by lexicographical project ordering.
  - Exact combinatorial evaluation over all 729 candidate portfolios ($3^6$).
- **Optimizer Unit Tests (`tests/test_optimizer.py`):**
  - Test coverage for zero budget, unconstrained budget, boundary budgets, feasibility filtering, mutual exclusivity, and tie-breaking.

---

## [0.1.1] - 2026-11-03

### Added
- **Canonical Data Fixtures (`data/`):**
  - `data/zones.csv`: 6 illustrative Pune planning areas (`Z01`–`Z06`) representing varied urban typologies (Sangamwadi, Shivajinagar, Hadapsar, Katraj, Yerawada, Hinjawadi).
  - `data/projects.csv`: 12 adaptation intervention packages (`P01`–`P12`) with cost in ₹ Crore, feasibility, and benefit dimensions.
- **Data Ingestion & Schema Validation (`src/data_loader.py`):**
  - Validates required columns, types, foreign key relationships, 0–100 index bounds, positive costs, and geographic coordinate validity.
- **Data Loader Unit Tests (`tests/test_data_loader.py`):**
  - Comprehensive negative and positive tests verifying schema integrity.
- **Application Skeleton (`app.py`):**
  - Initial Streamlit dashboard displaying data overview and provenance banners.

---

## [0.1.0] - 2026-11-03

### Added
- Initial repository setup.
- Basic `.gitignore` and `requirements.txt` dependencies (streamlit, pandas, plotly, pulp, pytest).
- Initial project README.md with problem statement and architecture overview.
