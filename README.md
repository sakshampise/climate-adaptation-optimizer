# 🌿 Pune Climate Optimizer

### A decision-support prototype for investing in a more climate-resilient Pune

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/App-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-123%20passing-2E7D32)](#-quality-checks)
[![Status](https://img.shields.io/badge/Project-Prototype-426B52)](#-important-data-boundaries)

> **The question:** If Pune has a limited climate-adaptation budget, which combination of interventions should be funded first—and why?

Pune Climate Optimizer is an interactive municipal planning prototype. It compares flood- and heat-resilience interventions across six illustrative planning areas, then finds the highest-scoring portfolio that fits a user-defined budget. It makes the trade-offs visible through a map, charts, project-level explanations, policy scenarios and downloadable CSVs.

**This is a transparent decision-support prototype, not an automated government allocation system.** Its optimization is deterministic mathematical search; it does not use a generative AI model to choose projects.

---

## ✨ What can I do with it?

- Set an adaptation budget (the default planning example is **₹10 crore**).
- Choose the policy lens: **Flood**, **Heat**, **Balanced Resilience** or **Social & Climate Equity**.
- See which intervention is selected for each planning area, what it costs and how much budget remains.
- Explore the recommended portfolio on an interactive map.
- Understand the weighted score and compare the four policy priorities under the same budget.
- Inspect the illustrative baseline datasets and the provenance of external climate context.
- Export the selected portfolio and scenario comparison as CSV files.

---

## 🧭 How the prototype works

```text
Planning inputs
  6 illustrative Pune areas + 12 intervention packages
                    │
                    ▼
       Budget + policy-priority selection
                    │
                    ▼
       Deterministic portfolio optimizer
       • one package at most per area
       • total cost must fit the budget
       • evaluates 3⁶ = 729 combinations
                    │
                    ▼
       Recommended portfolio + explanations
                    │
          ┌─────────┼──────────┐
          ▼         ▼          ▼
       Map & KPI  Scenarios   CSV exports
                    │
                    ▼
       Live / cached / fallback climate context
       Open-Meteo + NASA POWER climatology
```

### 1. Planning model

The prototype contains:

| Model element | What is represented |
|---|---|
| Planning areas | 6 illustrative Pune areas |
| Intervention packages | 12 candidate packages; 2 per area |
| Hazards | Flood and extreme heat |
| Scoring dimensions | Flood benefit, heat benefit, equity, critical infrastructure and urgency |
| Budget | User-controlled, in ₹ crore |
| Selection rule | At most one intervention per area; total cost cannot exceed budget |

The six demonstration areas are Sangamwadi, Shivajinagar, Hadapsar, Katraj, Yerawada and Hinjawadi. Their map coordinates and risk indicators are illustrative approximations—not official ward boundaries or measured municipal risk scores.

### 2. Policy presets

Each preset changes the relative importance of the five scoring dimensions. The weights are normalized to 1.00.

| Preset | Flood | Heat | Equity | Infrastructure | Urgency |
|---|---:|---:|---:|---:|---:|
| Flood Priority | 60% | 10% | 15% | 10% | 5% |
| Heat Priority | 10% | 60% | 15% | 10% | 5% |
| Balanced Resilience | 35% | 35% | 15% | 10% | 5% |
| Social & Climate Equity | 15% | 15% | 50% | 15% | 5% |

The score for a package is the weighted sum of its five benefit scores. The optimizer evaluates the available choices for every area—including choosing no package—against the budget constraint.

**Tie-breaking is deterministic:** higher total score wins; if scores tie, lower total cost wins; if those tie, the lexicographically smaller sorted project-ID list wins.

### 3. Climate data context

The app keeps the planning model separate from external weather and climatology context.

| Source | Used for | Important distinction |
|---|---|---|
| [Open-Meteo](https://open-meteo.com/) | Current weather context and a 7-day forecast; historical archive summaries are also supported by the ingestion layer | Live/cached meteorological context—not the source of the synthetic zone and project scores |
| [NASA POWER](https://power.larc.nasa.gov/) | Historical climatology parameters: solar radiation, surface/skin temperature and corrected precipitation | Coarse-grid historical climatology—not a local forecast or a street-level measurement |

The app shows source/provenance status and has cache and offline fallback paths. If a provider is unavailable and no usable cache exists, the fallback is explicitly labelled as simulated. **A fallback value must not be interpreted as a live observation.**

---

## 🖥️ What is inside the dashboard?

1. **Municipal Planning Controls** — set the total budget and select the policy-priority preset; inspect the active weight distribution.
2. **Executive KPIs** — review the recommended portfolio's cost, remaining budget and score.
3. **Geospatial Allocation Map** — see which areas receive a selected package; inspect area and package details.
4. **Portfolio Breakdown Analytics** — inspect weighted score contributions and budget utilization.
5. **Selected Portfolio** — review chosen interventions and the deterministic explanation for the recommendation.
6. **Multi-Scenario Policy Comparison** — compare the portfolio outcome under the different objective presets.
7. **Live Climate Intelligence** — view Open-Meteo context, including the 7-day outlook when available.
8. **Baseline Datasets & Methodology** — inspect the six-area and twelve-package inputs and NASA POWER climatology context.
9. **Data Provenance Notice** — see the prototype's data limitations and advisory boundary.

The map uses OpenStreetMap tiles through Plotly's map rendering. If map rendering fails, the application provides a geographic table fallback.

---

## 🚀 Run it locally

### Requirements

- Python 3.10 or newer
- Git
- Internet access for live Open-Meteo and NASA POWER requests (the app also has cache/fallback handling)

### 1. Clone the repository

```bash
git clone https://github.com/sakshampise/climate-adaptation-optimizer.git
cd climate-adaptation-optimizer
```

### 2. Create and activate a virtual environment

**Windows PowerShell**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the dashboard

```bash
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) in the terminal.

### 5. Run the tests

```bash
pytest
```

The integrated release was reported with **123 passing tests**. Run the suite in your own environment to verify your current checkout and dependency versions.

---

## 🧱 Tech stack

| Layer | Tools |
|---|---|
| Interactive application | Python, Streamlit |
| Data handling and validation | Pandas |
| Charts and map | Plotly, OpenStreetMap tiles |
| Portfolio selection | Python exhaustive deterministic search |
| External climate data | Open-Meteo, NASA POWER |
| HTTP and resilience | Requests, caching, retries and fallback handling |
| Tests | Pytest |

### Repository map

```text
.
├── app.py                    # Streamlit entry point and page orchestration
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit theme and app configuration
├── data/
│   ├── zones.csv             # Six illustrative planning areas
│   ├── projects.csv          # Twelve illustrative intervention packages
│   └── ...                   # Supporting data and provenance notes
├── components/
│   ├── styles.py             # Premium civic visual system
│   ├── portfolio.py          # Portfolio and KPI presentation
│   ├── analytics.py          # Charts and scenario comparison
│   ├── provenance.py         # Climate status and methodology disclosures
│   └── exports.py            # CSV export controls
├── src/
│   ├── data_loader.py        # Loads and validates planning inputs
│   ├── optimizer.py          # Exact deterministic portfolio search
│   ├── explanations.py       # Human-readable decision rationale
│   ├── map_view.py           # Spatial allocation map and fallback
│   ├── ingestion/
│   │   ├── fetch.py          # Fetch, parse, cache and fallback orchestration
│   │   ├── cache.py          # Cache handling
│   │   └── schemas.py        # Validated climate data structures
│   └── integrations/
│       ├── base.py           # Shared HTTP client and integration errors
│       ├── open_meteo.py     # Open-Meteo API client
│       └── nasa_power.py     # NASA POWER API client
└── tests/                    # Unit, integration and UI regression tests
```

---

## 🔬 Quality checks

The integrated release was reported as passing **123/123 automated tests**, covering:

- Optimizer constraints, deterministic selection and baseline equivalence
- Open-Meteo parsing, cache and fallback behaviour
- NASA POWER parsing, schema and cache behaviour
- UI reconciliation and regression checks

The optimizer and canonical baseline fixtures were also checked for unintended changes during final integration.

---

## ⚠️ Important data boundaries

Please read this before using screenshots, results or exports in a presentation or decision.

- **Planning inputs are illustrative/synthetic.** Zone risk indices, intervention benefit scores, intervention costs and evidence labels are demonstration inputs, not verified municipal measurements or approved project estimates.
- **The six areas are demo planning zones.** Coordinates and labels are approximations; they are not official administrative boundaries.
- **Scores are relative planning points.** They are not probabilities, measured reductions in flood depth, degrees of cooling, lives saved or validated benefit-cost ratios.
- **NASA POWER is coarse-resolution historical context.** It cannot establish street-level heat exposure or serve as a local weather forecast. Surface/skin temperature is not a direct measurement of the urban heat-island effect.
- **Open-Meteo status matters.** Live, cached and simulated fallback values are different states. Check the status/provenance shown in the app.
- **The optimizer is not an AI oracle.** It performs exact deterministic enumeration using fixed input scores and policy weights. The explanation text is generated from those same model inputs and results.
- **Real allocation requires validation.** Municipal users would need current ward-level data, engineering feasibility, land ownership, cost estimates, community consultation and domain review before acting on any recommendation.

This prototype is intended to demonstrate a transparent workflow for comparing adaptation portfolios—not to replace engineering, climate science or public budgeting processes.

---

## 👥 For teammates

A quick way to understand the project:

1. Start with `app.py` to see how the dashboard is assembled.
2. Read `src/optimizer.py` to understand the actual selection logic and constraints.
3. Read `src/explanations.py` to see how recommendations are explained.
4. Inspect `data/zones.csv` and `data/projects.csv` to understand the demonstration inputs.
5. Read `src/ingestion/fetch.py` and `src/integrations/` for external climate data, caching and fallback behaviour.
6. Run `pytest` before changing the model or UI.

**Rule of thumb:** keep the optimizer's mathematical contract and canonical baseline fixtures stable unless a change is explicitly reviewed and its tests are updated.

---

## 🏁 Project

**PCCOE International Grand Challenge 2026** · **Theme: AI for Climate Change**

Built as a prototype to explore how transparent optimization and climate context can support better-informed urban adaptation planning in Pune.

[View the source code](https://github.com/sakshampise/climate-adaptation-optimizer) · [Open an issue](https://github.com/sakshampise/climate-adaptation-optimizer/issues)
