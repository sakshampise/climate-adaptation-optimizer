---
name: Bug Report / Defect
about: Report a defect, test failure, regression, or calculation discrepancy
title: '[BUG]: '
labels: bug
assignees: ''
---

## Description
[Clear description of the unexpected behavior or failure.]

## Environment & Steps to Reproduce
1. Command / Step: `...`
2. Arguments / Inputs: `...`
3. Error Output / Stack Trace:

```text
[Paste stack trace here]
```

## Expected Behavior
[What should have happened according to CONTEXT.md and test specifications.]

## Affected Components
- [ ] `src/data_processing/` / `src/data_loader.py`
- [ ] `src/optimizer/` / `src/optimizer.py`
- [ ] `src/utils/` / `src/explanations.py` / `src/map_view.py`
- [ ] `app.py` / `components/`
- [ ] Data fixtures (`data/reference/`)

## Impact on Mathematical or Data Integrity
- Does this bug produce incorrect scores or violate budget constraints? [Yes / No]
- Does this bug cause unhandled exceptions in the Streamlit UI? [Yes / No]
