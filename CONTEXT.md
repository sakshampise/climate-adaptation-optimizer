# AI-Assisted Climate Adaptation Investment Prioritization — Context & Specification

**Authoritative Project Specification — v1.0**
- **Status:** MVP scope frozen; mathematical presets and data fixture values specified.
- **Date:** November 2026.
- **Hackathon:** PCCOE International Grand Challenge: 2026 (Theme: AI for Climate Change).
- **Core Question:** *Where should the next ₹10 Crore (or ₹1 Crore) go to make a city more climate-resilient?*

---

## 1. Product & Scope

### 1.1 Product Goal
Help a municipal decision-maker explore an illustrative Pune dataset and select a budget-feasible, optimal portfolio of climate adaptation project packages under transparent policy priorities.

### 1.2 Frozen MVP Scope
1. **Streamlit Application:** Clean, intuitive decision-support web UI.
2. **Six Illustrative Pune Areas:** Representing diverse urban typologies across Pune (e.g., riverfront, densely populated core, peri-urban growth corridor, industrial belt, hill slope/watershed, slum cluster).
3. **Twelve Intervention Packages:** Exactly two mutually exclusive alternatives per area.
4. **Hazard Indicators:** Flood and extreme-heat indicators alongside exposure, vulnerability, and critical infrastructure indices.
5. **Four Objective Presets:**
   - **Flood Priority**
   - **Heat Priority**
   - **Balanced Resilience**
   - **Social & Climate Equity**
6. **Budget-Constrained Optimization:** User enters budget in Indian Rupees Crore (₹ Cr); exact portfolio optimization subject to budget.
7. **Transparent Explanations:** Clear breakdown of selected interventions, score contributions, trade-offs, and reasons for exclusions.
8. **Scenario Comparison:** Side-by-side comparison across the 4 presets at a fixed budget.
9. **Export:** CSV export of selected portfolios and comparison metrics.
10. **Data Provenance:** Clear labeling of data status (`verified`, `derived`, `simulated`) and source notes.

### 1.3 Out of Scope
- No black-box machine learning or ungrounded generative AI predictions.
- No continuous digital twin or real-time sensor streams.
- No claims of absolute lives saved or validated risk reduction percentages.
- No live external API dependencies for the core decision path.
- No persistent relational database requirement (version-controlled CSV fixtures).

---

## 2. Architecture Baseline

- **Runtime & UI:** Python, Streamlit (single application process).
- **Data Engine:** Pandas, validated CSV files under `data/`.
- **Optimization Engine:** Python deterministic exact enumeration / PuLP integer linear programming formulation.
  - Search space for MVP: 6 zones with 3 choices each (Option A, Option B, or No Project) = $3^6 = 729$ candidate portfolios.
  - Guarantees provably exact global optimum with deterministic tie-breaking.
- **Visualizations:** Plotly charts (trade-offs, score breakdown) and Map/spatial view (PyDeck / Plotly Scattermapbox or tabular fallback).
- **Testing:** Pytest suite covering data integrity, optimizer correctness, and explanation contracts.

---

## 3. Shared Data Contracts

CSV headers and types are strictly versioned interfaces.

### 3.1 `data/zones.csv`
One row per planning area (exactly 6 rows for MVP).

| Column | Type | Allowed Values / Format | Description |
|---|---|---|---|
| `zone_id` | string | Unique, e.g. `Z01` to `Z06` | Stable primary key |
| `label` | string | Non-empty text | Display name (marked "Demo"/"Illustrative" if unverified) |
| `latitude` | float | WGS84 coordinates | Marker latitude |
| `longitude` | float | WGS84 coordinates | Marker longitude |
| `flood_risk_index` | int | 0 – 100 | Relative flood hazard indicator |
| `heat_risk_index` | int | 0 – 100 | Relative extreme heat hazard indicator |
| `exposure_index` | int | 0 – 100 | Relative exposure (population/density) |
| `vulnerability_index` | int | 0 – 100 | Relative socioeconomic vulnerability |
| `critical_infrastructure_index` | int | 0 – 100 | Critical infrastructure sensitivity |
| `data_status` | string | `verified`, `derived`, `simulated` | Conservative status for row values |
| `source_note` | string | Non-empty text | Citation, derivation logic, or assumption |

### 3.2 `data/projects.csv`
Candidate adaptation interventions (exactly 12 rows, 2 per zone).

| Column | Type | Allowed Values / Format | Description |
|---|---|---|---|
| `project_id` | string | Unique, e.g. `P01` to `P12` | Stable package key |
| `zone_id` | string | Matches `zone_id` in `zones.csv` | Foreign key to planning zone |
| `project_name` | string | Non-empty text | Plain-language project package name |
| `intervention_type` | string | e.g. `drainage`, `cool_roofs`, `urban_forestry` | Intervention category |
| `cost_crore` | float | > 0 | Total package capital cost in ₹ Crore |
| `feasible` | bool | `True`, `False` | Implementation feasibility status |
| `flood_benefit_score` | int | 0 – 100 | Relative flood reduction points |
| `heat_benefit_score` | int | 0 – 100 | Relative heat mitigation points |
| `equity_benefit_score` | int | 0 – 100 | Relative benefit to vulnerable communities |
| `infrastructure_benefit_score` | int | 0 – 100 | Relative critical infrastructure protection |
| `urgency_score` | int | 0 – 100 | Policy urgency ranking |
| `evidence_quality` | string | `low`, `medium`, `high` | Qualitative evidence confidence |
| `data_status` | string | `verified`, `derived`, `simulated` | Data provenance status |
| `source_note` | string | Non-empty text | Baseline data notes / citations |

---

## 4. Mathematical & Optimization Contract

### 4.1 Objective Presets & Weights
Weights represent normalized municipal priorities ($\sum w_i = 1.0$):

| Preset ID | Preset Name | $w_{flood}$ | $w_{heat}$ | $w_{equity}$ | $w_{infra}$ | $w_{urgency}$ |
|---|---|---|---|---|---|---|
| `flood` | Flood Priority | 0.60 | 0.10 | 0.15 | 0.10 | 0.05 |
| `heat` | Heat Priority | 0.10 | 0.60 | 0.15 | 0.10 | 0.05 |
| `balanced` | Balanced Resilience | 0.35 | 0.35 | 0.15 | 0.10 | 0.05 |
| `equity` | Social & Climate Equity | 0.15 | 0.15 | 0.50 | 0.15 | 0.05 |

### 4.2 Project Scoring
For an intervention $p$:
$$\text{score}(p) = w_{flood} \cdot S_{flood}(p) + w_{heat} \cdot S_{heat}(p) + w_{equity} \cdot S_{equity}(p) + w_{infra} \cdot S_{infra}(p) + w_{urgency} \cdot S_{urgency}(p)$$

### 4.3 Formulation & Constraints
Maximize the total portfolio resilience score:
$$\max \sum_{p \in P} x_p \cdot \text{score}(p)$$
Subject to:
1. **Budget constraint:**
   $$\sum_{p \in P} x_p \cdot \text{cost\_crore}(p) \le \text{budget\_crore}$$
2. **Mutual exclusivity per zone (at most one project per area):**
   $$\sum_{p \in P_z} x_p \le 1 \quad \forall z \in Z$$
3. **Feasibility:**
   $$x_p = 0 \quad \text{if } \text{feasible}(p) = \text{False}$$
4. **Binary decision:**
   $$x_p \in \{0, 1\} \quad \forall p \in P$$

### 4.4 Deterministic Tie-Breaking
When two or more portfolios achieve identical total score:
1. Choose the portfolio with **lower total cost** (higher cost-efficiency).
2. If still tied, choose **lexicographically** by sorted list of `project_id`.

---

## 5. Module & Interface Contracts

- **`src/data_loader.py`**:
  - `load_inputs(data_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]`
  - Validates schemas, uniqueness, foreign keys, row counts (6 zones, 12 projects), ranges [0, 100], positive costs, and coordinate validity.
- **`src/optimizer.py`**:
  - `OBJECTIVE_WEIGHTS: dict[str, dict[str, float]]`
  - `solve_portfolio(projects: pd.DataFrame, budget_crore: float, objective_id: str) -> dict`
  - Returns selected projects, total cost, remaining budget, total score, breakdown, combination metrics.
- **`src/explanations.py`**:
  - `generate_portfolio_explanation(result: dict, zones: pd.DataFrame, projects: pd.DataFrame) -> dict`
  - Builds human-readable rationale, trade-off summaries, and exclusion reasons without generative hallucination.
- **`src/map_view.py`**:
  - Spatial and visual display functions for zones and selected interventions with graceful tabular fallbacks.
- **`app.py`**:
  - Streamlit UI managing user controls, layout, presentation, scenario comparison, and CSV download.

---

## 6. Guardrails & Claim Discipline

1. **Explicit Simulation Disclaimers:** All synthetic data points are prominently labeled as simulated.
2. **No False Certainty:** Scores are relative planning units, not exact casualty or damage forecasts.
3. **Human-in-the-Loop:** The system serves as a decision-support aid; final allocation decisions rest with municipal authorities.
