# Week 8: Drift and Observability Monitoring

In this lab, we built a drift detection pipeline to monitor a vehicle detection model in production. The pipeline uses the **Population Stability Index (PSI)** to compare confidence-score distributions between a reference camera feed and a live camera feed, flagging when conditions have shifted enough to warrant investigation.

Key components:
1. **Score Extraction**: Runs the mock detector over all images in a camera directory and collects every detection's confidence score.
2. **PSI Computation**: Computes the Population Stability Index between reference and live distributions using equal-width binning.
3. **Drift Classification**: Maps PSI values to `"none"` / `"moderate"` / `"significant"` using standard thresholds (0.10, 0.25).

By monitoring drift, we can detect when a deployed model's input distribution changes — before it silently degrades in production!
