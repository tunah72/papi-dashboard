# Deferred P4 context — peer review and main-branch validation

**Recorded:** 2026-07-21 12:13 ICT
**Status:** Deferred by user until the current H2 implementation plan is complete.

## Why this is deferred

The current priority is to complete the approved plan in
[`../260721-1203-hon-tt-h2-so-snh-tnh-ca-tr/plan.md`](../260721-1203-hon-tt-h2-so-snh-tnh-ca-tr/plan.md)
on the branch based on `main`. Deferral does **not** waive either completion
gate below.

## P4 gates to resume after the current plan

1. **Cross-page review:** choose one peer page (H1, H3, or H4), review its
   data grain, source/missing-data disclosure, controls, and visual consistency;
   record actionable findings and either fix in scope or explicitly hand off.
2. **Integration validation on `main`:** after H2 receives independent review
   and is merged, switch to the resulting `main`, rerun the relevant test suite
   and Streamlit smoke test, then update the verified project/docs status.

## Preconditions for resuming P4

- Phases 01–05 of the H2 provincial-comparison plan are implemented and their
  stated validations have evidence.
- The H2 change is ready for independent code review; it is not merged merely
  because local implementation appears complete.
- The old `feature/task/Tri` branch remains reference-only. Do not merge or
  rebase it onto `main`; it has known conflicts in `app/pages/provincial.py`.
