# Two-Agent Collaboration Protocol & Governance Workflow (`AI_WORKFLOW.md`)

**Project:** Pune Climate Optimizer — AI-Assisted Climate Adaptation Investment Prioritization  
**Target Geography:** Pune, Maharashtra, India  
**Scope:** PCCOE International Grand Challenge 2026 (AI for Climate Change)  
**Status:** Authoritative Operational Protocol (Two-Agent Governance Model)  
**Effective Date:** November 5, 2026

---

## 1. Overview & Organizational Architecture

This document establishes the official collaboration protocol, division of responsibilities, and change-management standards across **ChatGPT**, **Antigravity**, and the **Human Project Lead**.

Following the November 5, 2026 governance transition, Gemini has been retired from active operational assignments. All existing Gemini reports are preserved permanently under `AI HANDOFFS/Gemini/` as historical audit records. Active project development is governed strictly under a streamlined **Two-Agent Model** with Human Executive Oversight.

---

## 2. Agent Roles & Authority Matrix

| Collaborator | Operational Role | Primary Focus & Domain | Explicit Constraints & Boundaries |
|---|---|---|---|
| **ChatGPT** | **Project Architect & Technical Supervisor** | • Owns project context, architecture, roadmap, technical specifications, and acceptance criteria.<br>• Formulates mathematical modeling and optimization design.<br>• Reviews technical proposals, code changes, and Antigravity implementation reports.<br>• Coordinates tasks, maintains project context, and determines next assignments.<br>• Recommends approval or rejection of pull requests. | • **Does not silently approve scope changes.**<br>• Must verify adherence to frozen MVP scope (6 Pune zones, 12 interventions, 4 presets, ₹ Cr budget).<br>• Does not write direct repository code commits. |
| **Antigravity** | **Primary Implementation Agent** | • Executes actual repository and application development.<br>• Implements approved specifications from ChatGPT.<br>• Debugs and maintains the application and data pipelines.<br>• Runs unit, integration, and regression test suites.<br>• Maintains documentation, Git hygiene, branches, commits, and pull requests.<br>• Produces complete Markdown handoff reports after each task. | • **Does not silently change approved interfaces or mathematical assumptions.**<br>• Requires human approval before making architectural refactors or schema alterations.<br>• Does not self-approve implementation work. |
| **Human Project Lead** | **Executive Authority & Final QA** | • Approves material scope, architecture, and mathematical changes.<br>• Conducts civic data verification and functional quality assurance.<br>• Approves Git merges, pull requests, and releases.<br>• Serves as the ultimate decision-maker for all project conflicts. | • Final decision-making authority on municipal policy alignment and presentation readiness. |

*Note on Historical Records:* Gemini is retired from active operations. No active tasks will be dispatched to Gemini, but historical files in `AI HANDOFFS/Gemini/` remain immutable audit artifacts.

---

## 3. Operational Cycle & Handoff Standard

Every task follows a strict linear sequence:

```
[ChatGPT / Human Lead]              [Antigravity]                 [ChatGPT]               [Human Team]
Task & Approved Spec   ──>  Implementation & Tests  ──>  Technical Review  ──>  Functional QA & Merge
        │                           │                           │                       │
Updates NEXT_ACTION.md      AI HANDOFFS/Antigravity/       Reviews Code & PR       Approves PR & Releases
```

### Protocol Rules:
1. **Always Check `NEXT_ACTION.md` First:** Before starting any work, every collaborator must read [`NEXT_ACTION.md`](file:///c:/Users/saksh/OneDrive/Documents/Desktop/pccoe%20indradhanu/NEXT_ACTION.md) to confirm the active task, prerequisites, and expected deliverables.
2. **Standardized Implementation Reports:** For every completed task, Antigravity produces one dated Markdown report in `AI HANDOFFS/Antigravity/Reports/` using the 12-section template.
3. **Never Claim Tests Passed Without Running:** All test results documented in handoffs must reflect actual terminal execution logs with exact passing counts and runtime.
4. **Never Claim Pushed State Without Verification:** Only mark commits as pushed after verifying local and remote Git tracking status.
5. **Update `NEXT_ACTION.md` Upon Completion:** When completing an assigned task, Antigravity updates `NEXT_ACTION.md` with results and hands off to ChatGPT for review.
6. **No Self-Approvals for Major Decisions:** No agent may unilaterally approve its own major architectural, mathematical, or scope changes.

---

## 4. Branch & Release Management

- **`main` Branch:** Protected, stable, deployable code. All tests must pass (100% pass rate). Never push unreviewed changes directly to `main`.
- **`dev` Branch:** Active multi-agent integration branch.
- **`feature/*` or `docs/*` Branches:** Individual feature, bugfix, or documentation work.
- **Change Management Workflow:**
  $$\text{Task Specification (ChatGPT)} \longrightarrow \text{Branch Checkout} \longrightarrow \text{Implementation (Antigravity)} \longrightarrow \text{Pytest Validation} \longrightarrow \text{Handoff Report} \longrightarrow \text{Commit \& Push} \longrightarrow \text{Pull Request} \longrightarrow \text{Review (ChatGPT)} \longrightarrow \text{QA \& Merge (Human Lead)}$$

---

## 5. Non-Negotiable Project Guardrails (Frozen MVP)

1. **MVP Boundary:** Six illustrative Pune planning areas (`Z01`–`Z06`), twelve adaptation packages (`P01`–`P12`, 2 mutually exclusive per area), four objective presets (*Flood Priority*, *Heat Priority*, *Balanced Resilience*, *Social & Climate Equity*), and user-defined capital budget in ₹ Crore.
2. **Scoring Model:** Additive multi-criteria scoring model with 5 benefit dimensions (Flood, Heat, Equity, Infrastructure, Urgency). Multiplicative hazard-vulnerability coupling is explicitly excluded from the frozen MVP.
3. **Data Provenance Discipline:** Mandatory 3-tier classification (`verified`, `derived`, `simulated`). Never invent data sources or present simulated values as verified measurements.
4. **Deterministic Optimization:** Exact combinatorial / PuLP solver over 729 combinations with deterministic two-tier tie-breaking (cost minimization, then lexicographical ID).
5. **Transparent Explanations & Export:** Deterministic, hallucination-free narrative explanations and one-click CSV export.
6. **Advisory Posture:** All recommendations are advisory decision-support tools, not automated executive mandates. No claims of validated lives saved or physical casualty reduction.
