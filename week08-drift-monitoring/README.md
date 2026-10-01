# Week 8 — Drift and Observability Monitoring

**DS5619 Machine Learning Systems Operations · Track B (BMD-45 Vehicle Detection)**


This lab applies **ML Observability and Drift Detection** from the Week 8 lecture to a vehicle detection pipeline. We use the **Population Stability Index (PSI)** to compare detector confidence-score distributions between a "reference" camera feed (training-time conditions) and a "live" camera feed (deployment-time conditions), flagging when the distribution has drifted enough to warrant investigation.


## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python generate_for_student.py --student-id <your roll number or institute email>
```

## What Was Implemented

Four functions in [`src/drift_monitor.py`](src/drift_monitor.py):

| Function | Purpose |
|---|---|
| `extract_confidence_scores(camera_dir)` | Runs the mock detector over all `.jpg` images in a camera directory and collects every detection's confidence score |
| `compute_psi(reference_scores, live_scores, n_bins)` | Computes the Population Stability Index between two score distributions using equal-width binning |
| `classify_drift(psi)` | Maps a PSI value to `"none"` / `"moderate"` / `"significant"` using standard thresholds (0.10, 0.25) |
| `summarize_scores(scores)` | Returns count, mean, std, min, max for a list of scores |

## Running

```bash
# Generate the drift report
python src/run_pipeline.py

# Self-check tests
python -m pytest tests/ -q
```
