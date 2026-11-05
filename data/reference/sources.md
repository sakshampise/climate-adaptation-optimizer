# Data Sources & Provenance Documentation

This document describes the provenance, methodology, and limitations of the datasets in `data/zones.csv` and `data/projects.csv`.

---

## 1. Geographic Boundaries & Coordinates

- **Target City:** Pune, Maharashtra, India.
- **Coordinate Reference System:** WGS84 (EPSG:4326).
- **Zone Selection Methodology:**
  Six representative zones were chosen to embody distinct urban typologies across Pune:
  1. **Z01 (Sangamwadi Confluence):** River confluence zone prone to monsoon backwater swelling.
  2. **Z02 (Shivajinagar Urban Core):** High-density administrative and transit node with high thermal inertia.
  3. **Z03 (Hadapsar Corridor):** Mixed industrial, logistics, and blue-collar residential hub.
  4. **Z04 (Katraj Lake Catchment):** High-gradient catchment basin at southern ghat foothills subject to flash runoff.
  5. **Z05 (Yerawada Riverfront Settlements):** High-density informal communities with high socioeconomic vulnerability to both heat and waterlogging.
  6. **Z06 (Hinjawadi Tech Corridor):** Peri-urban economic engine with high impervious surface cover and critical tech infrastructure.
- **Coordinates Status:** The centroid coordinates correspond to real geographic locations in Pune, but are utilized for illustrative demonstration purposes (`simulated` data status).

---

## 2. Hazard & Vulnerability Indices (0–100)

- **Nature of Scores:** Relative planning points, not absolute physical measurements or return-period probabilities.
- **Provenance:** Simulated based on public domain Pune climate risk literature (e.g., Pune Municipal Corporation Environment Status Reports, heat island research, and Mula-Mutha flood mapping).
- **Conservative Provenance Tag:** All index rows are categorized as `simulated` to maintain data provenance discipline.

---

## 3. Intervention Packages & Costing

- **Cost Scale:** Sized in ₹ Crore (Cr) corresponding to realistic municipal pilot capital expenditure scales (ranging from ₹1.4 Cr to ₹4.8 Cr).
- **Mutual Exclusivity:** For each zone, two alternative packages are defined:
  - Typically contrasting nature-based solutions (NBS) / passive cooling against engineered grey infrastructure or targeted localized retrofits.
- **Benefit Dimensions:**
  - `flood_benefit_score`: Relative reduction in waterlogging depth/duration.
  - `heat_benefit_score`: Relative reduction in surface heat load and thermal exposure.
  - `equity_benefit_score`: Prioritization of low-income, informal, and vulnerable populations.
  - `infrastructure_benefit_score`: Protection of critical roads, bridges, and utilities.
  - `urgency_score`: Near-term risk severity and policy alignment.
