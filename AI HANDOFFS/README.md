# AI Collaboration & Handoff Archive (`AI HANDOFFS/`)

This directory serves as the persistent communication and audit trail across AI agents (ChatGPT, Gemini, Antigravity) and human team members collaborating on the **AI-Assisted Climate Adaptation Investment Prioritization** project.

---

## 1. Collaboration Roles & Responsibilities

| Agent / Model | Primary Role | Directory | Key Deliverables |
|---|---|---|---|
| **ChatGPT** | System Architecture & Product Governance | `AI HANDOFFS/ChatGPT/` | Feature specifications, product requirements, UX reviews, policy documents |
| **Gemini** | Mathematical Modeling & Scientific Validation | `AI HANDOFFS/Gemini/` | Multi-criteria optimization formulations, objective weighting proposals, risk model reviews |
| **Antigravity** | Primary Implementation & Engineering Lead | `AI HANDOFFS/Antigravity/` | Code implementation reports, test execution logs, refactoring plans, debug reports |

---

## 2. Directory Structure

```text
AI HANDOFFS/
├── README.md                          # Collaboration guidelines and protocols
│
├── ChatGPT/
│   ├── Specifications/               # Product requirements and feature design briefs
│   └── Reviews/                      # Architecture and documentation reviews
│
├── Gemini/
│   ├── Mathematical Proposals/       # Knapsack, Pareto, and multi-criteria mathematical specs
│   └── Reviews/                      # Scientific and algorithmic reviews
│
└── Antigravity/
    ├── Implementation Reports/       # Engineering progress, code structure, and test reports
    └── Debug Reports/                # Root-cause analysis, bug fixes, and regression reports
```

---

## 3. Handoff Protocol & File Naming Standard

1. **Format:** Markdown (`.md`).
2. **File Naming Convention:** `YYYY-MM-DD_<agent>_<topic_slug>.md`
   - Example: `2026-11-05_antigravity_workspace_organization.md`
   - Example: `2026-11-06_gemini_pulp_vs_exact_evaluation.md`
   - Example: `2026-11-06_chatgpt_scenario_comparison_spec.md`
3. **Mandatory Header Fields in Every Handoff Document:**
   ```markdown
   # Handoff: [Title]
   - **Author:** [ChatGPT | Gemini | Antigravity | Human]
   - **Recipient:** [All | Specific Agent]
   - **Date:** YYYY-MM-DD
   - **Context / Task:** [Brief summary]
   - **Status:** [Draft | Proposed | Approved | Implemented]
   ```
4. **Preservation Rule:** Never delete or overwrite previous handoff documents; always append new reports or link to previous iterations to maintain the audit trail.
