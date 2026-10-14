# Week 10: Fairness and Robustness Audit

In this lab, we built a fairness and adversarial robustness audit pipeline for a vehicle detection model across 14 vehicle classes (from the BMD-45 benchmark). The pipeline audits per-class recall (equal opportunity) to surface systematic performance disparities on smaller vehicle categories, and evaluates model fragility under white-box FGSM-style adversarial perturbations.

Key components:
1. **Intersection-over-Union (IoU) & Ground-Truth Matching**: Computes bounding box overlap to evaluate whether each ground-truth object is successfully detected, independent of class classification errors.
2. **Per-Category Fairness Audit**: Accumulates detection recall across all images per vehicle category and flags underperforming classes falling below a strict recall threshold (90%).
3. **Adversarial Robustness Evaluation**: Perturbs image channels using an $L_\infty$ budget (lowering red, raising green and blue) across multiple budgets ($\epsilon \in [0, 10, 20, 30, 40]$), measuring recall degradation and ranking the most fragile categories.

By combining per-group fairness audits with adversarial stress testing, we can uncover structural performance gaps across categories and ensure models remain reliable and equitable under adverse real-world conditions!
