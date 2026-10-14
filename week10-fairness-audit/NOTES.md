# NOTES.md — Week 10: Fairness and Robustness Audit

**Student ID used with `generate_for_student.py`:**
student_id: 142301003
seed: 410824825
Wrote 60 images across 2 camera profiles -> D:\DS5619-MLOPS\week10-fairness-audit\data\fixtures
Wrote 243 annotations -> D:\DS5619-MLOPS\week10-fairness-audit\data\fixtures/_annotations.coco.json

---

## Which classes got flagged?

Four categories fell below the 90% recall threshold:
- **Hatchback**: 15 / 18 = **83.3%**
- **Two-wheeler**: 11 / 13 = **84.6%**
- **Other**: 20 / 23 = **87.0%**
- **Bicycle**: 14 / 16 = **87.5%**

**Does this match expectations?**
Yes. `generate_for_student.py` explicitly scales down bounding boxes for small-vehicle classes (`Bicycle: 0.35`, `Two-wheeler: 0.45`) and guarantees both fall below 90% recall. 

`Hatchback` and `Other` falling below 90% is **sampling noise**: each class has only 18–23 total ground-truth boxes, so missing just 3 boxes under Camera B's low light and noise drops recall into the 80s. In contrast, the deficit for Bicycle and Two-wheeler is a structural size disparity.

---

## If the grouping variable were a protected attribute

- **Stakes**: In vehicle detection, disparity is a technical safety issue. If groups were protected demographic attributes (e.g., race, gender in facial recognition, hiring, or healthcare), disparity leads to civil rights violations, legal liability (Title VII, EU AI Act), and severe allocative harms (wrongful arrests, denial of jobs or medical care).
- **Engineering Obligations**:
  - Disparities cannot be dismissed as sampling noise or acceptable physical variation; strict fairness standards (e.g., 4/5ths rule, equalized odds) are legally enforced.
  - Deployment must be blocked until affirmative bias mitigation is applied (e.g., Fairlearn equalized odds constraints, reweighting, adversarial debiasing).
  - Engineers carry a legal and ethical duty to provide audit trails, continuous production fairness monitoring, and appeal mechanisms for affected individuals.

---

## Which attack could corrupt this audit?

- **Lifecycle Stage & Attack**: **Data Poisoning** during the **Evaluation Data Preparation** stage. An adversary alters `_annotations.coco.json` by slightly shifting or enlarging bounding boxes for underperforming classes, artificially inflating measured recall above 90% and hiding a real-world safety disparity.
- **Control**: **Cryptographic Provenance & Schema Validation** — signing evaluation datasets with immutable SHA-256 hashes (e.g., DVC / LakeFS) under strict access controls, coupled with automated schema checks on bounding box coordinate and area distributions.

---

## Would SHAP or LIME explain a missed detection?

- **Missed Box**: `camera_B_lowlight/021.jpg`, Bicycle (bbox `[176, 88, 6, 7]`). Low-light noise reduced reddish pixels below the mock detector's hard threshold (`len(pts) >= 20`), so the detector discarded the component and output nothing.
- **Would SHAP or LIME help?** **No.**
- **Why their assumptions break**:
  1. **Null output on false negatives**: When an object is missed, the detector outputs *no bounding box at all* ($f(x) = \emptyset$). SHAP and LIME require a scalar output score to compute attributions; there is no score to explain.
  2. **Variable-cardinality outputs**: Detectors produce variable numbers of boxes that shift, split, or disappear under perturbation, breaking the fixed-output assumption of standard explainability tools.
  3. **Discontinuous decision boundaries**: The detector uses non-smooth step functions (`len(pts) < 20` and Boolean color checks), violating LIME's core assumption of local linearity.

---

## What did your attack show?

- **Recall degradation**:
  - `Bicycle`: Drops sharply at $\epsilon=10$ (87.5% $\to$ 62.5%), plummets to 43.8% at $\epsilon=20$, and collapses to 18.8% at $\epsilon=40$.
  - `Two-wheeler`: Drops from 84.6% to 76.9% at $\epsilon=10$, and 53.8% at $\epsilon=20$.
  - `Hatchback`: Drops to 77.8% at $\epsilon=10$, 66.7% at $\epsilon=20$.
  - `Other`: Resilient at $\epsilon=10$ (87.0%), then drops to 78.3% at $\epsilon=20$.
- **Most fragile class at $\epsilon=20$**: **Bicycle** has the largest drop (**-43.8%**), followed by Sedan (-31.8%) and Van (-31.2%). This matches the clean audit: the class with structural vulnerability is also the most fragile under attack.
- **Drop ranking vs. Lowest recall ranking**:
  - *Largest drop*: Bicycle (-43.8%), Sedan (-31.8%), Van (-31.2%).
  - *Lowest recall*: Bicycle (43.8%), Two-wheeler (53.8%), Van (62.5%).
  - *Why they differ*: Sedan started at 100% and fell to 68.2% (large drop, moderate recall). Two-wheeler started at 84.6% and fell to 53.8% (smaller delta, but much worse operational recall).
  - *Better measure of harm*: **Lowest absolute recall** is the better measure of real-world safety hazard.
- **Who bears the cost**: Vulnerable road users (cyclists and motorcyclists) who already suffer baseline disadvantages bear the compounded cost under stress.
- **Defenses**:
  - *Input validation*: Monitor channel balance ($\bar{R} - \bar{G}$) to detect red suppression, and apply spatial median filtering to smooth out perturbations.
  - *Adversarial training*: Train on perturbed inputs to force the detector to learn invariant shape and edge features rather than relying on brittle raw color thresholds.
- **Why a simple rule breaks more easily than a CNN**: The rule evaluates raw pixel values with hard Boolean thresholds; shifting channels by $\epsilon=20$ reduces color margins by 40 points, immediately wiping out blobs. A CNN learns hierarchical spatial representations (edges, textures, silhouettes) across many channels, making it far more resilient to uniform color shifts.
