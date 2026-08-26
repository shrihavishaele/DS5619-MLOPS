# Week 4: Versioning, Feature Store, and Lineage

This folder contains the Week 4 lab for DS5619 Machine Learning Systems
Operations. The lab builds a small, local feature store for a fraud-detection
transaction feed. It uses only Python and JSON files, so the ideas can be
examined without setting up an external service such as Feast or Hopsworks.

## What This Lab Demonstrates

The lab follows a transaction dataset through four steps:

1. **Raw data versioning**: each input file is identified by its SHA-256
	content hash. Running the same snapshot again returns the existing version
	instead of creating a duplicate.
2. **Feature engineering**: transactions are grouped by `card_id` to produce
	transaction count, average amount, maximum amount, card-present percentage,
	and the latest event time.
3. **Feature-group versioning**: every registered feature group receives a new
	version, so a later schema change never overwrites earlier features.
4. **Lineage**: each feature-group manifest records which raw data version and
	transformation produced it.

## The v1 to v2 Schema Change

The `data/` directory contains two revisions of the same upstream feed:

| Revision | Amount field | Country field | Additional field |
| --- | --- | --- | --- |
| v1 | `amount` in major units | `country` | None |
| v2 | `amount_minor_units` in cents | `country_code` | `device_fingerprint` |

This is a breaking upstream change. The feature builder detects the schema
from the row fields and converts v2 amounts from cents by dividing by 100.
That conversion keeps v1 and v2 aggregate features comparable.

## Folder Contents

- `src/mini_feature_store.py`: implementation of raw snapshots, feature
  construction, feature-group registration, and lineage lookup.
- `src/run_pipeline.py`: complete driver that processes v1 and v2 in order.
- `data/v1/transactions.csv`: first transaction schema revision.
- `data/v2/transactions.csv`: breaking second schema revision.
- `tests/test_smoke.py`: self-checks for the four functions and full pipeline.
- `generate_for_student.py`: deterministically regenerates the data for a
  student ID.
- `.feature_store/`: JSON manifests and feature rows created by the pipeline.
- `lineage_report.json`: combined lineage report for the registered versions.
- `NOTES.md`: student ID and observations about the v1/v2 manifests.

## Setup

From this folder, create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Regenerate the student-specific input data and record the same ID in `NOTES.md`:

```bash
python generate_for_student.py --student-id <your-roll-number-or-email>
```

## Run the Pipeline

Run this command from the `week04-versioning-feature-store` directory:

```bash
python src/run_pipeline.py
```

The driver will:

1. Snapshot the v1 CSV and build the v1 feature group.
2. Snapshot the v2 CSV and build a separate feature-group version.
3. Verify that snapshotting the unchanged v1 CSV is idempotent.
4. Write lineage information to `lineage_report.json`.

On a clean registry, the first run creates raw versions `v1` and `v2`, and
feature-group versions `v1` and `v2`. Running the pipeline again should keep
the raw IDs for identical files but create new feature-group versions because
feature-group registration is intentionally append-only.

## Run the Tests

```bash
pytest tests/ -q
```

The tests cover content-hash idempotency, changed-file detection, both input
schemas, feature-group non-overwrite behavior, lineage lookup, and the full
pipeline.

## Submission Checklist

Before submitting, confirm that:

- `NOTES.md` contains the student ID used to generate the data.
- The committed CSV files match that student ID.
- `.feature_store/` contains the generated JSON registry artifacts.
- `lineage_report.json` is present.
- `python src/run_pipeline.py` completes successfully.
- `pytest tests/ -q` passes.

The implementation is intentionally small, but the design mirrors production
principles: immutable data versions, explicit schema handling, reproducible
feature transformations, and traceable lineage.
