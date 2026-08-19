# NOTES.md — Week 3: ETL and Data Validation

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student_id: 142301003
seed: 3603207943

## Quarantine count vs. the 7 known injected problems

<!-- How many rows ended up quarantined, and does that match the 7 known
     injected problems? (It won't match exactly — some rows may trip more
     than one expectation. Explain the discrepancy if there is one.) -->

The pipeline quarantined 6 rows, not 7. This is expected because one row can fail multiple checks, so a single bad row is counted once in quarantine even when it triggers several violations.

- expect_column_not_null (amount): 2 violations — rows [88, 298]
- expect_column_not_null (card_id): 1 violation — row [220]
- expect_column_positive (amount): 3 violations — rows [32, 88, 298]
- expect_column_in_set (merchant_category): 1 violation — row [155]
- expect_column_unique (transaction_id): 1 violation — row [342]

Total violations: 8 across 6 unique quarantined rows.