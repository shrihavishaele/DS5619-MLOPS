# NOTES.md — Week 5: Model Registry Governance

**Student ID used with `generate_for_student.py`:**
student_id: 142301003
seed: 563063486
candidate_a: f1=0.516 (below 0.70 bar)
candidate_b: f1=0.833 (clears 0.70 bar)

## Which candidate reached Production, and why?

**Candidate B** — `promote_model` requires (1) a completed model card and (2) F1 ≥ 0.70. Candidate A (F1 = 0.516) was rejected with `GovernanceError` despite having a valid card. Candidate B (F1 = 0.833) met both conditions and was promoted.

## Gating stale feature data

Add a third check in `promote_model`'s Production gate: require a `feature_data_timestamp` field in the manifest, compare it to `now`, and raise `GovernanceError` if the gap exceeds 30 days. The upstream pipeline (feature store / training job) must emit this timestamp at training time so `register_model` can persist it.

## Scaling to 40 candidates

No code changes needed. `register_model` auto-increments version IDs (v1 … v40) and stores each independently. `promote_model` evaluates governance per-version (card + F1 check). Archiving scans sibling versions to find/archive the current Production model — works the same at 2 or 40. At thousands of versions, a `production_pointer.json` index would improve efficiency, but at 40 it's fine as-is.

