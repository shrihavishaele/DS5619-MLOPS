# NOTES.md — Week 10: Fairness and Robustness Audit

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
142301003


## Which classes got flagged?

<!-- Which classes got flagged, and does that match what you'd expect given
     how generate_for_student.py built the fixtures? -->
Hatchback (83.3%), Two-wheeler (84.6%), Other (87.0%), and Bicycle (87.5%) fell below the 0.90 threshold.
Yes, this aligns with expectations: Bicycle and Two-wheeler have smaller size multipliers (0.35 and 0.45), making them structurally harder to detect. Hatchback and Other dipping below 90% is sampling variance from small sample sizes (~18–23 boxes) and low-light noise.


## If the grouping variable were a protected attribute

<!-- Tying back to the framing note: what would change about this audit's
     stakes and your obligations as an engineer if the grouping variable
     were a protected demographic attribute instead of a vehicle class? -->
* **Higher Stakes:** Disparities across protected demographics (e.g., race, gender) risk civil rights violations, legal liability (Title VII, EU AI Act), and systemic discrimination (e.g., biased arrests or hiring rejections) rather than just technical detection errors.
* **Engineering Obligations:** Engineers must enforce hard deployment gates (no shipping with >10% disparity), conduct mandatory bias mitigations (e.g., equalized odds constraints via Fairlearn), and maintain continuous production audit logs with avenues for user appeal.


## Which attack could corrupt this audit?

<!-- Name one lifecycle stage and attack from the lecture (data poisoning,
     model theft, or adversarial examples) that could silently corrupt THIS
     audit's result, and one control from the lecture that would reduce the
     risk. -->
* **Attack:** Data Poisoning (Evaluation / Pre-deployment Stage) — an insider or compromised feed shifts ground-truth bounding boxes or inflates box sizes in the test set to artificially boost recall above 90%, concealing real model bias.
* **Control:** Cryptographic dataset verification (tracking SHA-256 hashes of test annotations via immutable storage like DVC/LakeFS) along with automated schema validation on bounding box sizes.


## Would SHAP or LIME explain a missed detection?

<!-- Pick one missed ground-truth box in a flagged class. An auditor asks
     you to explain WHY the detector missed it, not just that it did. Would
     SHAP or LIME actually help you answer that for a bounding-box detector
     — and if not, what's different about this detector's inputs/outputs
     that breaks the assumption both tools make? -->
No.
* **Output Cardinality:** Standard SHAP/LIME assume a fixed scalar score for a predefined class. A missed vehicle produces zero candidate detections, leaving no output score to attribute feature importance to.
* **Step-Function Mechanics:** The detector relies on rigid thresholds (pixel redness and `len(pts) >= 20`). Masking image superpixels causes detections to abruptly vanish or shift rather than smoothly varying, violating LIME's local linearity assumption.


## What did your attack show?

<!-- Using fairness_report.json["adversarial"]: at what eps does each flagged
     class fall further? Which class is most fragile, and is it the same
     class the clean audit flagged? Compare the drop ranking
     (most_fragile) with lowest_recall_under_attack — do they agree, and
     which is the better measure of who is hurt? What does that say about who bears the
     cost of an attack (or of an unmonitored failure)? Then: what would
     adversarial training or input validation look like for this detector,
     and why does a rule this simple break so much more easily than a CNN
     (or does it)? -->

* **Eps Degradation:** **Bicycle** falls steeply at $\epsilon=10$ ($0.8750 \rightarrow 0.6250$) and collapses to $0.1875$ at $\epsilon=40$; **Two-wheeler** drops $0.8462 \rightarrow 0.5385$ ($\epsilon=20$) and reaches $0.3846$ ($\epsilon=40$); **Hatchback** drops $0.8333 \rightarrow 0.6667$ ($\epsilon=20$) and $0.3889$ ($\epsilon=40$); **Other** drops to $0.7826$ ($\epsilon=20$) and $0.5217$ ($\epsilon=40$).
* **Fragility:** At $\epsilon=20$, **Bicycle** suffers the largest drop (0.4375), followed by **Sedan** (0.3182) and **Van** (0.3125). Bicycle matches the class flagged in the clean audit.
* **Drop vs. Absolute Recall:** The rankings diverge (`most_fragile` = Bicycle, Sedan, Van vs. `lowest_recall_under_attack` = Bicycle, Two-wheeler, Van). **Lowest absolute recall** is the superior safety metric because operational risk depends on whether a vehicle is detected on the road, not how much recall it lost relative to a high baseline.
* **Cost of Failure:** Vulnerable road users (cyclists and two-wheelers) absorb the safety hazard, as their already low baseline detection rates collapse completely under perturbation.
* **Rule vs. CNN Brittleness:** Hardcoded static rules ($R > 120$, $R - G > 40$, $R - B > 40$) break catastrophically because an $\epsilon=20$ shift narrows the color gap by 40 points, eliminating pixel blobs. CNNs are more robust to uniform channel shifts because they extract hierarchical spatial features, edges, and silhouettes.
* **Mitigations:** Input validation via channel balance checks ($\bar{R} - \bar{G}$) and spatial median filtering; adversarial training by augmenting the model with $\pm\epsilon$ perturbed samples to learn shape invariants instead of relying purely on color thresholds.
