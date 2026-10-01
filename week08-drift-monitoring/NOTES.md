# NOTES.md — Week 8: Drift and Observability Monitoring

**Student ID used with `generate_for_student.py`:**
student id : 142301003
seed: 2279155017
Wrote 40 images across 2 camera profiles -> D:\DS5619-MLOPS\week08-drift-monitoring\data\fixtures
Wrote 168 annotations -> D:\DS5619-MLOPS\week08-drift-monitoring\data\fixtures/_annotations.coco.json
Sanity-checked PSI (using the mock detector, not your drift_monitor.py): 0.1154

---

## Drift level vs. expectation

The report showed **PSI = 0.1154 → "moderate"** drift. This is expected — the two cameras have deliberately different visual profiles (daylight vs low-light), so their confidence-score distributions differ. Camera A had more spread (std=0.029, min=0.722) while Camera B scores were tightly clustered near 0.98 (std=0.016, min=0.835).

---

## What confidence-score-only monitoring misses

Confidence scores catch **covariate drift** (input distribution shift) but miss **concept drift** (the input-to-label relationship changes). A model can stay confidently wrong — e.g., misclassifying a new vehicle type it was never trained on with high confidence.

With ground-truth labels available a day later, I would monitor:
1. **Actual accuracy** (mAP, precision, recall)
2. **Label distribution shift** (new or changing class frequencies)
3. **Per-class confusion matrix** (systematic misclassifications)
4. **Calibration error** (does confidence match actual correctness?)

