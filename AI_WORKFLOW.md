# Multi-AI Collaboration Protocol & Governance Workflow (`AI_WORKFLOW.md`)

**Project:** AI-Assisted Climate Adaptation Investment Prioritization  
**Target Geography:** Pune, Maharashtra, India  
**Scope:** PCCOE International Grand Challenge 2026 (AI for Climate Change)  
**Status:** Authoritative Operational Protocol

---

## 1. Overview & Objectives

This document establishes the collaboration protocol, division of responsibilities, and handoff standards across **ChatGPT**, **Gemini**, **Antigravity**, and the **Human Team**.

To avoid drift, conflicting implementations, or ungrounded generative hallucinations, every development cycle follows strict single-responsibility boundaries, deterministic mathematical constraints, and explicit handoff documentation.

---

## 2. Agent Roles & Authority Matrix

| Collaborator | Operational Role | Primary Focus & Domain | Explicit Constraints & Boundaries |
|---|---|---|---|
| **ChatGPT** | **Project Architect & Technical Supervisor** | • Owns project context, architecture, roadmap, specifications, and technical reviews.<br>• Reviews Gemini's mathematical recommendations.<br>• Reviews Antigravity's implementation reports.<br>• Determines the recommended next task and responsible agent. | • **Does not silently approve scope changes.**<br>• Must verify adherence to frozen MVP scope (6 Pune zones, 12 interventions, 4 presets, ₹ Cr budget). |
| **Gemini** | **Mathematical Engineering Lead** | • Reviews mathematical formulations and optimization logic.<br>• Audits assumptions, scoring systems, constraints, and validation.<br>• Documents mathematical recommendations and proposed changes.<br>• Designs composite risk formulas and Pareto trade-off analyses. | • **Does not independently change approved architecture.**<br>• Must ground all recommendations in the existing project documentation without introducing unapproved complexity. |
| **Antigravity** | **Primary Implementation Agent** | • Implements approved specifications and refactoring plans.<br>• Maintains the codebase, executes test suites, and fixes bugs.<br>• Reports changed files, test results, and outstanding issues.<br>• Manages Git hygiene, pull requests, and workspace layout. | • **Does not silently change approved interfaces or mathematical assumptions.**<br>• Requires human approval before making architectural refactors or file removals. |
| **Human Team** | **Executive Authority & Final QA** | • Approves major architectural, mathematical, and scope decisions.<br>• Conducts civic data verification and functional quality assurance.<br>• Approves Git merges and feature releases. | • Final decision-making authority on municipal policy alignment and presentation readiness. |

---

## 3. Operational Cycle & Handoff Standard

Every task follows a strict linear sequence:

```
[ChatGPT / Human]              [Gemini]                 [Antigravity]              [Human Team]
Task Specification  ──>  Mathematical Review  ──>  Code Implementation  ──>  Merge & Approval
        │                         │                           │                      │
Updates NEXT_ACTION.md    AI HANDOFFS/Gemini/         AI HANDOFFS/Antigravity/   Reviews PR & Closes
```

### Protocol Rules:
1. **Always Check `NEXT_ACTION.md` First:** Before starting any work, every collaborator must read [`NEXT_ACTION.md`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/NEXT_ACTION.md) to confirm who is currently assigned.
2. **Never Overwrite Historical Handoffs:** All handoffs must be saved with dated filenames under `AI HANDOFFS/<Agent>/` following the convention `YYYY-MM-DD_<agent>_<slug>.md`.
3. **Mandatory Handoff Headers:** Every handoff document must include:
   - Date
   - Authoring agent
   - Task ID (from `PROJECT DOCS/TASKS.md`)
   - Status
   - Relevant file paths
   - Deliverables
   - Next recommended action
4. **Update `NEXT_ACTION.md` Upon Completion:** When an assigned collaborator finishes their task, they must update `NEXT_ACTION.md` with the outcome and the recommended next agent.
5. **No Self-Approvals for Major Decisions:** No AI agent may unilaterally approve its own major architectural or mathematical revisions.

---

## 4. Branch & Release Management

- **`main` Branch:** Protected, stable, deployable code. All tests must pass (100% pass rate).
- **`dev` Branch:** Active multi-agent integration branch.
- **`feature/*` Branches:** Individual feature or experimental tasks.
- **Change Management Workflow:**
  $$\text{Task Definition} \longrightarrow \text{Implementation} \longrightarrow \text{Automated Tests} \longrightarrow \text{Commit \& Push} \longrightarrow \text{Pull Request} \longrightarrow \text{Review} \longrightarrow \text{Merge}$$

---

## 5. Non-Negotiable Project Guardrails

1. **MVP Boundary:** 6 illustrative Pune planning areas (`Z01`–`Z06`), 12 adaptation packages (`P01`–`P12`, 2 mutually exclusive per zone), 4 objective presets, and ₹ Crore budget.
2. **Data Provenance Discipline:** Mandatory 3-tier classification (`verified`, `derived`, `simulated`). Never invent data sources.
3. **Deterministic Optimization:** Exact combinatorial / PuLP solver with deterministic two-tier tie-breaking (cost minimization, then lexicographical order).
4. **Transparent Explanations:** Deterministic, hallucination-free rationale and one-click CSV export.
5. **Advisory Posture:** All recommendations are advisory decision-support tools, not automated executive mandates.
