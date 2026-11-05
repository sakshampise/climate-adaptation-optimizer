# Data Directory Manifest (`data/`)

This directory houses all datasets used by the **AI-Assisted Climate Adaptation Investment Prioritization** platform for Pune.

---

## 1. Directory Structure

```text
data/
├── raw/            # Original, unmodified datasets as acquired or ingested
├── processed/      # Cleaned, standardized, and normalized datasets
├── reference/      # Canonical lookup tables and validated baseline fixtures
│   ├── zones.csv   # 6 illustrative Pune planning areas
│   ├── projects.csv# 12 adaptation intervention packages
│   └── sources.md  # Methodology and geographic centroid notes
├── zones.csv       # Active runtime zone dataset
├── projects.csv    # Active runtime projects dataset
├── sources.md      # Active runtime provenance notes
└── README.md       # This manifest file
```

---

## 2. Directory Purposes & Lifecycle Rules

### `raw/`
- **Purpose:** Store raw data dumps, external GeoJSON/Shapefiles, census extracts, or meteorological data in their exact original form.
- **Rule:** Never edit files in `raw/` directly. Always write automated scripts to process them into `processed/`.
- **Status:** Currently initialized for future primary data ingestion.

### `processed/`
- **Purpose:** Cleaned, validated, and normalized data ready for ingestion or modeling.
- **Rule:** Every processed file must document its source file in `raw/` and the transformation script used.

### `reference/`
- **Purpose:** Canonical version-controlled fixtures serving as the ground-truth baseline for the application.
- **Files:**
  - `zones.csv`: Six Pune planning zones with risk, exposure, and vulnerability indices (0–100 scale).
  - `projects.csv`: Twelve intervention packages (2 per zone, mutually exclusive) with capital costs in ₹ Crore and multidimensional benefit scores.
  - `sources.md`: Provenance details, coordinate reference system (WGS84), and literature citations.

---

## 3. Mandatory Data Rules

1. **No Invented Data:** Never synthesize fictitious municipal surveys or attribute simulated values to official sources.
2. **Provenance Field:** Every row must include a `data_status` column strictly restricted to:
   - `verified` (official records)
   - `derived` (mathematically computed from verified base data)
   - `simulated` (illustrative synthetic values grounded in literature)
3. **Auditability:** Every record must include a `source_note` specifying its origin or simulation rationale.
4. **Advisory Guardrail:** Recommendations derived from these datasets are decision-support aids, not validated real-world damage reduction guarantees.
