# Handoff: Mathematical Model Audit — Climate Adaptation Investment Prioritization

- **Author:** Antigravity (Implementation Agent on behalf of Human Team)
- **Recipient:** Gemini (Mathematical Modeling Lead)
- **Date:** 2026-11-05
- **Task Reference:** Task M3-T4 (`PROJECT DOCS/TASKS.md`)
- **Status:** Requested Review / Proposed Action Item

---

## 1. Purpose & Scope of Audit

As part of Milestone 3 of the **PCCOE International Grand Challenge: 2026 (AI for Climate Change)**, this document formally requests an independent mathematical audit and peer review from Gemini on the portfolio optimization model, multi-criteria objective formulation, constraints, and proposed composite risk calculations for Pune's climate adaptation decision-support platform.

The existing implementation in `src/optimizer.py` is operational and passes all 9 unit tests in `tests/test_optimizer.py`. However, to ensure rigorous mathematical defensibility before jury presentation, Gemini's review is requested across five key dimensions.

---

## 2. Baseline Model Specification (As Implemented)

### 2.1 Multi-Criteria Scoring Function
For any candidate intervention package $p \in P$, the resilience score under policy preset $\theta \in \{\text{flood}, \text{heat}, \text{balanced}, \text{equity}\}$ is computed additively:
$$\text{score}(p, \theta) = \sum_{k \in K} w_k(\theta) \cdot S_k(p)$$
where:
- Criteria $K = \{\text{flood}, \text{heat}, \text{equity}, \text{infrastructure}, \text{urgency}\}$
- $S_k(p) \in [0, 100]$ are relative benefit points from `data/reference/projects.csv`
- $\sum_{k \in K} w_k(\theta) = 1.00$

### 2.2 Normalized Objective Presets
Weights are currently configured as:

| Preset $\theta$ | $w_{flood}$ | $w_{heat}$ | $w_{equity}$ | $w_{infra}$ | $w_{urgency}$ | $\sum w$ |
|---|---|---|---|---|---|---|
| **Flood Priority** | 0.60 | 0.10 | 0.15 | 0.10 | 0.05 | 1.00 |
| **Heat Priority** | 0.10 | 0.60 | 0.15 | 0.10 | 0.05 | 1.00 |
| **Balanced Resilience** | 0.35 | 0.35 | 0.15 | 0.10 | 0.05 | 1.00 |
| **Social & Climate Equity**| 0.15 | 0.15 | 0.50 | 0.15 | 0.05 | 1.00 |

### 2.3 Optimization Formulation (Multiple-Choice 0-1 Knapsack with GUB)
Find binary decisions $x_p \in \{0, 1\}$ to:
$$\max_{x} \sum_{p \in P} x_p \cdot \text{score}(p, \theta)$$
Subject to:
1. **Capital Budget Constraint:**
   $$\sum_{p \in P} x_p \cdot c_p \le B$$
   where $c_p > 0$ is capital cost in ₹ Crore, and $B$ is the user budget in ₹ Crore.
2. **Mutual Exclusivity per Zone (Generalized Upper Bound):**
   $$\sum_{p \in P_z} x_p \le 1 \quad \forall z \in Z$$
   where $P_z$ denotes the candidate projects in zone $z$ ($|P_z| = 2$ for MVP; decision is Project A, Project B, or No Project).
3. **Implementation Feasibility:**
   $$x_p = 0 \quad \forall p \text{ where } \text{feasible}(p) = \text{False}$$

### 2.4 Deterministic Two-Tier Tie-Breaking
When two candidate portfolios $X_1, X_2$ achieve identical total resilience score:
1. **Cost Minimization:** $\arg\min \sum_{p \in X} c_p$ (selects the portfolio with higher cost efficiency).
2. **Lexicographical Tie-Breaker:** If costs are also identical, sort selected `project_id` strings alphanumerically and choose the lexicographically smaller tuple.

### 2.5 Search Space
For the 6 illustrative Pune zones with 2 projects each ($|Z| = 6, |P| = 12$):
$$\text{Total Combinations} = \prod_{z \in Z} (|P_z| + 1) = 3^6 = 729 \text{ candidate portfolios}$$
Solved via exhaustive combinatorial enumeration and verified against PuLP ILP formulation.

---

## 3. Specific Audit Questions for Gemini

Gemini is requested to review and provide recommendations on:

1. **Multi-Criteria Scoring Linearity:**
   - Does the linear additive weighting $\sum w_i S_i$ adequately capture multi-hazard resilience?
   - Should diminishing marginal returns, submodularity, or non-linear saturation effects be documented as limitations or future extensions?
2. **Preset Weight Sensitivity & Differentiation:**
   - Are the four preset weight vectors sufficiently differentiated to demonstrate clear municipal policy trade-offs across realistic budget levels (e.g., ₹5 Cr, ₹10 Cr, ₹15 Cr)?
3. **Knapsack Slack & Multi-Objective Trade-Offs:**
   - In cases where residual budget remains (e.g. ₹0.3 Cr left that cannot fund any package), does the formulation appropriately communicate capital efficiency vs. absolute score?
   - Is Pareto-frontier analysis recommended for the scenario comparison module?
4. **Proposed Composite Risk Index for `src/risk_model/`:**
   - In `data/reference/zones.csv`, each zone has: `flood_risk_index`, `heat_risk_index`, `exposure_index`, `vulnerability_index`, and `critical_infrastructure_index`.
   - What is the mathematically sound, defensible formula for computing an overall baseline **Composite Risk Index** $R_z \in [0, 100]$ prior to intervention? (e.g. Geometric mean, weighted arithmetic sum, or IPCC hazard $\times$ exposure $\times$ vulnerability formulation?)
5. **Scalability Beyond MVP ($n > 6$):**
   - For Pune's complete municipal jurisdiction (e.g., 40+ wards or 100+ projects), $3^{40} \approx 1.2 \times 10^{19}$ combinations makes exhaustive enumeration infeasible.
   - Please review the branch-and-cut / integer linear programming formulation using PuLP/CBC to ensure mathematical parity with the exact MVP solver.

---

## 4. Reference Documents & Code Locations

- **Specification:** [`PROJECT DOCS/CONTEXT.md`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/PROJECT%20DOCS/CONTEXT.md) (Sections 4.1–4.4)
- **Data Policy & Guardrails:** [`PROJECT DOCS/DATA POLICY.md`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/PROJECT%20DOCS/DATA%20POLICY.md) (Rules 1, 2, 3, 4, 8, 9)
- **Architectural Decisions:** [`PROJECT DOCS/DECISIONS.md`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/PROJECT%20DOCS/DECISIONS.md) (ADR-002, ADR-004, ADR-005, ADR-009)
- **Optimizer Code:** [`src/optimizer.py`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/src/optimizer.py)
- **Unit Test Suite:** [`tests/test_optimizer.py`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/tests/test_optimizer.py)

---

## 5. Output Instructions for Gemini

Please submit your mathematical audit report as a markdown document in:
`AI HANDOFFS/Gemini/Mathematical Proposals/YYYY-MM-DD_gemini_model_audit_response.md` (or in `AI HANDOFFS/Gemini/Reviews/`).
