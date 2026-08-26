# NOTES.md — Week 4: Versioning, Feature Store & Lineage

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student_id: 142301003
seed: 1773144849
Wrote 500 v1 records -> /home2/mlops/Documents/DS5619-MLOPS/week04-versioning-feature-store/data/v1/transactions.csv
Wrote 125 v2 records -> /home2/mlops/Documents/DS5619-MLOPS/week04-versioning-feature-store/data/v2/transactions.csv

## v1 vs. v2 manifest comparison

The v1 and v2 feature-group manifests have the same feature-group name,
feature schema, and transform version. Both contain the derived fields
`card_id`, `txn_count`, `avg_amount`, `max_amount`, `pct_card_present`, and
`event_time`.

The important differences are that they have different
`feature_group_version_id` values and different `source_raw_version_id`
values. The v1 feature group points to raw version v1, while the v2 feature
group points to raw version v2. Their `row_count` and `created_at` values can
also differ because they were built from separate data revisions. This keeps
the v1 history intact instead of overwriting it after the schema change.


## Why treat amount_minor_units differently from amount?

In v1, `amount` is already expressed in major currency units, such as
`100.00`. In v2, `amount_minor_units` is an integer number of cents, such as
`10000`. `build_features` divides the v2 value by 100 before calculating the
average and maximum. Without this conversion, v2 amounts would be 100 times
larger and the aggregates could not be compared fairly with the v1 features.
