# AI-Assisted Climate Adaptation Investment Prioritization

Decision-support platform for municipal climate adaptation planning under strict budget constraints.

**Theme:** AI for Climate Change — *PCCOE International Grand Challenge: 2026*  
**Core Question:** *Where should the next ₹10 Crore go to make a city more climate-resilient?*

---

## Overview

Cities face compounding climate threats (flooding, extreme heat, environmental degradation) with strictly finite public adaptation budgets. This platform provides an AI-assisted, mathematically sound, transparent decision-support system that:
1. Profiles planning zones across hazards (flood, heat) and vulnerabilities (exposure, equity, critical assets).
2. Evaluates intervention packages across multiple resilience dimensions.
3. Formulates budget-constrained portfolio optimization using deterministic multi-criteria mathematical programming.
4. Explains trade-offs and policy scenario impacts (Flood vs. Heat vs. Balanced vs. Equity) for decision-makers.

---

## Architecture & Technology Stack

- **Frontend & App:** [Streamlit](https://streamlit.io/)
- **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
- **Visualizations:** [Plotly](https://plotly.com/)
- **Mathematical Optimization:** Deterministic Exact Solver / [PuLP](https://coin-or.github.io/pulp/)
- **Quality Assurance:** [Pytest](https://pytest.org/)

---

## Directory Structure

```text
PCCOE Indradhanu/
│
├── README.md                      # Project overview and setup instructions
├── requirements.txt               # Project dependencies
├── app.py                         # Streamlit interactive application entry point
│
├── PROJECT DOCS/                  # Project source of truth
│   ├── CONTEXT.md                 # Authoritative project specification and data contracts
│   ├── ROADMAP.md                 # Development milestones and delivery roadmap
│   ├── TASKS.md                   # Task backlog and implementation progress
│   ├── DECISIONS.md               # Architecture Decision Records (ADRs)
│   ├── DATA POLICY.md             # Data governance, provenance, and 9 project rules
│   └── CHANGELOG.md               # Version history and change log
│
├── AI HANDOFFS/                   # Communication archive across AI agents and team
│   ├── ChatGPT/                   # Specifications and reviews
│   ├── Gemini/                    # Mathematical proposals and reviews
│   └── Antigravity/               # Implementation reports and debug logs
│
├── data/                          # Data lifecycle assets
│   ├── raw/                       # Immutable raw datasets
│   ├── processed/                 # Cleaned and standardized data
│   ├── reference/                 # Canonical baseline fixtures (zones.csv, projects.csv)
│   ├── zones.csv                  # 6 illustrative planning zones in Pune
│   ├── projects.csv               # 12 adaptation intervention packages
│   ├── sources.md                 # Data provenance and methodology notes
│   └── README.md                  # Data manifest and lifecycle guide
│
├── src/                           # Application core logic
│   ├── data_processing/           # Ingestion, validation, and schema enforcement
│   ├── risk_model/                # Multi-hazard, vulnerability, and exposure models
│   ├── optimizer/                 # Portfolio optimization engine (exact + PuLP)
│   ├── utils/                     # Shared helpers, narrative generation, map view
│   ├── data_loader.py             # Active runtime data loader
│   ├── optimizer.py               # Active runtime optimizer
│   ├── explanations.py            # Active runtime explanation generator
│   └── map_view.py                # Active runtime spatial map and fallback
│
├── components/                    # Reusable Streamlit UI components
├── tests/                         # Pytest validation and integration test suite
├── exports/                       # Optimization result exports and comparison CSVs
├── docs/                          # Additional technical documentation and guides
└── assets/                        # Visual assets, logos, and icons
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ (Recommended: Anaconda / virtual environment)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Running Tests
```bash
pytest
```

### 4. Running the Application
```bash
streamlit run app.py
```

---

## Provenance & Disclaimer

All data values are explicitly labeled with their provenance status (`verified`, `derived`, or `simulated`). The application functions as an advisory decision-support tool; real-world allocation decisions require localized on-ground geotechnical and socio-economic validation.
