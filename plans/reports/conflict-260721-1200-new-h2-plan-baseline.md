---
date: 2026-07-21
scope: Conflict baseline before creating the H2 completion plan
old_branch: feature/task/Tri
target: main at 697f5b2
new_branch: feat/h2-provincial-completion
---

# Conflict baseline — old Tri branch vs main

## Verdict

`feature/task/Tri` remains reference-only. It diverged from `main` at `34b0bae`; do not merge, rebase or cherry-pick commit `90da9f9`.

## Confirmed overlap

- Conflict: `app/pages/provincial.py`.
- Changed on both branches: `app/pages/ai_assistant.py`.
- Diverged contract/implementation: `app/ai/api_logs.py`.
- Broad overlap: H2, report, tests and requirements.

## Rule for this plan

The new branch starts from `main` and ports behavior manually into the current `src/analysis/provincial.py` + `app/pages/provincial.py` contract. AI/log changes from the old branch are excluded. Report changes are re-authored only after H2 output is reproduced.

## Open question

None. The approved design requires map click-to-drill with a selectbox fallback.
