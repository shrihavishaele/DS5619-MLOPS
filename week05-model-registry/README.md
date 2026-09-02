# Week 5 — Model Registry Governance

> **Course:** DS5619 Machine Learning Systems Operations 



This project implements a **minimal local model registry** in pure Python that demonstrates three core governance ideas:

| Concept | What it does | Function |
|---|---|---|
| **Artifact Store** | Versions each trained model with immutable manifests | `register_model` |
| **Model Card** | Requires a genuinely filled-in governance record (no TODOs allowed) | `generate_model_card` |
| **Promotion Gate** | Blocks Production deployment unless the model has a card **and** F1 ≥ 0.70 | `promote_model` |
| **Production Lookup** | Returns whichever version is currently live | `get_production_model` |

When a new model is promoted to Production, the previously live version is automatically **archived** — so there is always exactly one answer to *"what's in production right now?"*

## How it works

Two pre-trained fraud-detection candidates (`candidate_a` and `candidate_b`) are provided. Each is a simple amount-threshold model with its own `metrics.json`. The pipeline:

1. **Registers** both candidates → versioned directories under `.model_registry/`
2. **Attempts promotion without a model card** → blocked by governance gate (`GovernanceError`)
3. **Generates model cards** for both candidates
4. **Attempts promotion of the low-F1 candidate** → blocked (F1 < 0.70)
5. **Promotes the passing candidate** → reaches Production, writes `registry_summary.json`

## Project Structure

```
week05-model-registry/
├── src/
│   ├── mini_model_registry.py   # Core registry: register, card, promote, lookup
│   └── run_pipeline.py          # Driver script — runs the full demo
├── data/
│   ├── candidate_a/             # Model + metrics (fails F1 bar)
│   └── candidate_b/             # Model + metrics (passes F1 bar)
├── tests/                       # Self-check test suite
├── .model_registry/             # Generated registry artifacts (manifests, cards)
├── model_card_fields.json       # Model card content (must be filled in)
├── registry_summary.json        # Output: production model summary
├── generate_for_student.py      # Generates student-specific candidate data
├── requirements.txt
├── NOTES.md                     # Analysis and reflections
└── README.md
```

## Setup & Run

```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate student-specific candidate data
python generate_for_student.py --student-id <your roll number or institute email>

# Run the full pipeline
python src/run_pipeline.py

# Run self-check tests
pytest tests/ -q
```

> **Note:** `generate_for_student.py` overwrites `data/candidate_a/` and `data/candidate_b/` with deterministic values derived from your student ID. Record your `--student-id` in `NOTES.md` — the grader re-generates and diffs against your committed output.

## Key Design Decisions

- **Governance as code, not policy** — promotion rules are enforced programmatically in `promote_model`, not by convention or review checklists.
- **Immutable versioning** — `register_model` auto-increments version IDs (`v1`, `v2`, …) and never overwrites a prior version.
- **Card completeness validation** — `generate_model_card` rejects any card with missing fields, blank values, or leftover `TODO` placeholders.
- **Single Production invariant** — promoting a new version to Production auto-archives the previous one, maintaining exactly one live version at all times.

## Deliverables

- `src/mini_model_registry.py` — completed implementation
- `model_card_fields.json` — filled in with real content (no `TODO` left)
- `.model_registry/` — generated registry artifacts
- `registry_summary.json` — production model summary
- `NOTES.md` — student ID, analysis, and reflections
