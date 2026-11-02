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
├── CONTEXT.md             # Authoritative project specification and data contracts
├── TASKS.md               # Implementation roadmap and task tracking
├── README.md              # Project overview and setup instructions
├── requirements.txt       # Project dependencies
├── data/
│   ├── zones.csv          # 6 illustrative planning zones in Pune
│   ├── projects.csv       # 12 adaptation intervention packages
│   └── sources.md         # Data provenance and methodology notes
├── src/
│   ├── __init__.py
│   ├── data_loader.py     # Schema validation and data ingestion
│   ├── optimizer.py       # Multi-criteria portfolio optimization
│   ├── explanations.py    # Deterministic narrative and trade-off generation
│   └── map_view.py        # Spatial mapping and visualization fallbacks
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   └── test_optimizer.py
└── app.py                 # Streamlit interactive application entry point
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
