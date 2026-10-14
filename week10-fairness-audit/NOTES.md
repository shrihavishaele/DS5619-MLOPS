# NOTES.md — Week 10: Fairness and Robustness Audit

**Student ID used with `generate_for_student.py`:**
`142301003`

Deterministic generation log:
- **Student ID**: `142301003`
- **Sub-seed**: `410824825`
- **Fixtures written**: 60 images across 2 camera profiles (`camera_A_daylight`, `camera_B_lowlight`) to `data/fixtures/`
- **Annotations written**: 243 ground-truth bounding boxes across 14 BMD-45 categories to `data/fixtures/_annotations.coco.json`

---

## Which classes got flagged?

Running the clean fairness audit (`python src/run_pipeline.py`) flagged **4 categories** falling below the 90.0% recall threshold (sorted worst-first):
1. **Hatchback**: 15 / 18 detected = **83.33%** recall
2. **Two-wheeler**: 11 / 13 detected = **84.62%** recall
3. **Other**: 20 / 23 detected = **86.96%** recall
4. **Bicycle**: 14 / 16 detected = **87.50%** recall

All remaining 10 classes met or exceeded the 90.0% bar: Tempo-traveller (90.91%), Mini-bus (92.31%), Three-wheeler (92.86%), Van (93.75%), and MUV, LCV, Bus, Sedan, SUV, Truck (all 100.0%).

### Does this match what is expected from `generate_for_student.py`?
**Yes, exactly.** 
- `generate_for_student.py` models the empirical finding from the BMD-45 benchmark: small vehicle classes are structurally harder to detect. It enforces small bounding box dimensions via `CLASS_SIZE_MULTIPLIER`: `Bicycle: 0.35` and `Two-wheeler: 0.45`, whereas large vehicles receive multipliers between `1.3` and `2.2` (`Bus: 2.2`, `Truck: 2.0`, `Tempo-traveller: 1.9`, `Mini-bus: 1.8`, `Van: 1.3`).
- The generator's retry loop explicitly guarantees that **Bicycle** and **Two-wheeler** both finish below 90% recall while no large class does.
- The appearance of **Hatchback** (83.33%) and **Other** (86.96%) below the threshold represents expected **sampling noise** rather than a structural flaw:
  - Each class in the 60-image fixture set contains only 13 to 23 total ground-truth annotations.
  - In `camera_B_lowlight`, boxes are scaled down by 0.7 and high noise (±22) is applied to pixels.
  - For small sample counts ($N \approx 18$), missing just 3 boxes drops recall by 16.7% ($15/18 \approx 83.3\%$). Missing 3 boxes of "Other" drops recall by 13.0% ($20/23 \approx 87.0\%$).
  - As noted in `README.pdf`, mid-sized classes hovering between 80% and 90% due to sample variance is fully expected. In contrast, the deficit for Bicycles and Two-wheelers is a systematic size disparity.

---

## If the grouping variable were a protected attribute

If the grouping variable in this audit were a protected demographic attribute (such as race, ethnicity, gender, age, or disability status under Title VII, the Equal Credit Opportunity Act, or the EU AI Act) instead of vehicle categories:

1. **Ethical Stakes & Human Consequences**:
   - In vehicle detection, an unequal recall between Bicycles and Sedans poses serious traffic safety and autonomous navigation hazards, but it remains an engineering challenge of object localization.
   - For protected demographic groups (e.g., in facial recognition, automated hiring screening, credit risk scoring, or healthcare diagnostic algorithms), a performance disparity means **allocative or quality-of-service harms**: wrongful arrests, systemic denial of employment or loans, or disparate misdiagnosis rates resulting in preventable mortality. The stakes shift from technical performance to civil rights, fundamental liberties, and human dignity.

2. **Legal and Regulatory Obligations**:
   - Disparity cannot be dismissed as "acceptable physical variation" or "sampling noise." Legal frameworks (e.g., the EEOC 4/5ths rule, Title VII disparate impact doctrine, EU AI Act High-Risk AI conformity assessments) mandate continuous algorithmic auditing and statistical justification.
   - Engineers bear affirmative legal liability to perform formal Algorithmic Impact Assessments (AIA) and document audit trails.

3. **Engineering Workflow & Deployment Constraints**:
   - A disparity of 10–15% across demographic groups is a **blocking deployment gate**. An engineer cannot deploy the model until fairness interventions are executed (e.g., Fairlearn equalized odds post-processing, adversarial debiasing, cost-sensitive reweighting, or targeted resampling).
   - Engineers have a strict obligation to establish continuous production monitoring for demographic parity and equal opportunity metrics, provide transparent model cards, and implement clear human-in-the-loop appeal mechanisms for individuals adversely affected.

---

## Which attack could corrupt this audit?

- **Lifecycle Stage**: Data Preparation & Evaluation Dataset Curation (pre-deployment testing).
- **Attack**: **Evaluation Data Poisoning / Clean-Label Backdoor Poisoning**.
  - *Mechanism*: An insider or an attacker who compromises the storage repository where evaluation fixtures are staged (`data/fixtures/` or `_annotations.coco.json`) can subtly modify the test set. For example:
    - Slightly shrinking or shifting the ground-truth bounding boxes for small vehicles (Bicycles and Two-wheelers) so that the calculated IoU with real detections drops below 0.3, artificially suppressing recall to sabotage audit compliance.
    - Conversely, inserting an imperceptible backdoor trigger pattern into images and generating enlarged duplicate annotations for underperforming classes so that candidate detections artificially achieve >90% recall. This would falsely certify a biased, unsafe model as "fair" prior to production release.
- **Control from Lecture**:
  - **Cryptographic Provenance & Immutable Data Versioning**: Golden evaluation datasets must be version-controlled with cryptographic signing (e.g., SHA-256 manifest hashing in DVC, LakeFS, or signed Git LFS tags) and stored in append-only, tamper-evident object storage with strict Role-Based Access Control (RBAC).
  - **Automated Data Validation & Schema Integrity**: Automated pipeline gates (e.g., Great Expectations, CI integrity checks) that check distribution properties—such as bounding box aspect ratio distributions, spatial coordinate bounds, label frequencies, and image noise levels—against historical baselines to flag anomalous alterations before the audit pipeline executes.

---

## Would SHAP or LIME explain a missed detection?

### Picked Missed Ground-Truth Box:
- **Image**: `camera_B_lowlight/021.jpg`
- **Category**: `Bicycle`
- **Annotation ID**: 84 (bbox: `[176, 88, 6, 7]`, area: 42 pixels)
- **Why the detector missed it**: 
  The mock detector requires a connected component of reddish pixels (`r > 120 and r - g > 40 and r - b > 40`) to have at least 20 contiguous pixels (`len(pts) >= 20`). In `camera_B_lowlight`, the base lighting is dark (`bg: (60, 62, 70)`) and severe random pixel noise ($\pm 22$) is added. For a tiny $6 \times 7$ bounding box (total area 42), the noise pushes several border pixels below the redness criteria, leaving fewer than 20 pixels in the flood-fill stack. The detector discards the blob entirely and emits zero detections for that object.

### Would SHAP or LIME explain this missed detection?
**No, standard SHAP and LIME cannot explain this missed detection.**

### What breaks their core assumptions:
1. **The Fixed-Output Assumption vs. Variable-Cardinality Outputs**:
   - Both SHAP (KernelSHAP) and LIME assume the model is a function $f(x) \in \mathbb{R}^K$ producing a fixed scalar probability or score for fixed classes (e.g., $P(\text{class}=c)$).
   - An object detector produces a variable-length list of bounding boxes $[\text{bbox}_i, \text{score}_i, \text{class}_i]$. When image regions or superpixels are masked or perturbed, existing detections shift position, merge, split, or disappear entirely. There is no consistent output slot to correlate across perturbations.
2. **The "Null Output" Problem on False Negatives**:
   - In a missed detection, the detector produced **no candidate bounding box whatsoever** in that region.
   - Because $f(x) = \emptyset$, there is no confidence score, no bounding box coordinate, and no logit from which to compute gradients (SHAP) or fit a local linear regression surrogate (LIME). You cannot attribute importance weights to input features when there is no scalar output to explain.
3. **Severe Local Discontinuity & Step-Function Thresholds**:
   - The detector relies on a hard step-function threshold (`len(pts) >= 20` and Boolean color inequalities).
   - LIME assumes local smoothness (that small input perturbations produce smooth, approximately linear changes in output). A single pixel crossing the threshold flips the output from "detected box with score 0.8" to "no box at all", completely violating the local linearity assumption.

---

## What did your attack show?

Using `fairness_report.json["adversarial"]`:

### Recall Progression Across Budgets ($\epsilon \in [0, 10, 20, 30, 40]$):
| Category | $\epsilon=0$ (Clean) | $\epsilon=10$ | $\epsilon=20$ | $\epsilon=30$ | $\epsilon=40$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Bicycle** | 87.5% | 62.5% | **43.8%** | 25.0% | 18.8% |
| **Two-wheeler** | 84.6% | 76.9% | **53.8%** | 46.2% | 38.5% |
| **Hatchback** | 83.3% | 77.8% | **66.7%** | 61.1% | 38.9% |
| **Other** | 87.0% | 87.0% | **78.3%** | 69.6% | 52.2% |
| **Van** | 93.8% | 87.5% | **62.5%** | 43.8% | 43.8% |
| **Sedan** | 100.0% | 77.3% | **68.2%** | 40.9% | 31.8% |
| **Three-wheeler** | 92.9% | 78.6% | **71.4%** | 64.3% | 35.7% |
| **Truck** | 100.0% | 88.9% | **72.2%** | 50.0% | 33.3% |
| **SUV** | 100.0% | 88.9% | **72.2%** | 66.7% | 50.0% |
| **Tempo-traveller** | 90.9% | 81.8% | **72.7%** | 63.6% | 50.0% |
| **Mini-bus** | 92.3% | 92.3% | **76.9%** | 76.9% | 46.2% |
| **Bus** | 100.0% | 86.7% | **80.0%** | 60.0% | 46.7% |
| **LCV** | 100.0% | 100.0% | **80.0%** | 80.0% | 66.7% |
| **MUV** | 100.0% | 95.0% | **90.0%** | 85.0% | 65.0% |

### At what $\epsilon$ does each flagged class fall further?
- **Bicycle** falls catastrophically immediately at $\epsilon=10$ (dropping 25.0 percentage points to 62.5%), and plummets to 43.8% at $\epsilon=20$, collapsing to 18.8% at $\epsilon=40$.
- **Two-wheeler** degrades steadily from 84.6% to 76.9% at $\epsilon=10$, drops sharply to 53.8% at $\epsilon=20$, and reaches 38.5% at $\epsilon=40$.
- **Hatchback** drops to 77.8% at $\epsilon=10$, 66.7% at $\epsilon=20$, and collapses to 38.9% at $\epsilon=40$.
- **Other** is resilient at $\epsilon=10$ (87.0%), then degrades to 78.3% at $\epsilon=20$ and 52.2% at $\epsilon=40$.

### Which class is most fragile at $\epsilon=20$?
- The top-3 most fragile classes by recall drop at $\epsilon=20$ are:
  1. **Bicycle**: recall drop of **43.75%** ($0.8750 \to 0.4375$)
  2. **Sedan**: recall drop of **31.82%** ($1.0000 \to 0.6818$)
  3. **Van**: recall drop of **31.25%** ($0.9375 \to 0.6250$)
- **Is it the same class the clean audit flagged?**
  Yes. **Bicycle** was already flagged in the clean audit (87.5%), and it exhibits the largest absolute drop under attack (-43.75%), proving that the most vulnerable category under clean conditions is also the most fragile under adversarial stress.

### Drop Ranking vs. Lowest-Recall Ranking:
- **Most fragile (largest drop)**: `Bicycle` (-43.8%), `Sedan` (-31.8%), `Van` (-31.2%).
- **Lowest absolute recall under attack**: `Bicycle` (43.8%), `Two-wheeler` (53.8%), `Van` (62.5%).
- **Why they differ**:
  - `Sedan` started with perfect recall (100.0%) and fell to 68.2%, yielding a large drop ($\Delta = 31.8\%$). However, its absolute recall (68.2%) is still substantially higher than `Two-wheeler` (53.8%).
  - `Two-wheeler` started with low clean recall (84.6%) and dropped to 53.8% ($\Delta = 30.8\%$). Because its drop was slightly smaller than Sedan's, it was omitted from the "top 3 drop" list despite having the second-worst operational recall in the entire dataset.
- **Which is the better measure of who is hurt?**
  **Lowest absolute recall under attack** is the far better measure of operational harm and safety risk. On an urban roadway, an autonomous or traffic monitoring system that detects two-wheelers only 53.8% of the time creates an extreme hazard. Focusing exclusively on percentage drop ($\Delta$) obscures the severe baseline disadvantage of already marginalized or under-detected groups.

### Who bears the cost?
Vulnerable road users (bicycles, two-wheelers) bear the compound burden: they suffer the lowest baseline detection rate in benign conditions, and under adversarial perturbation or environmental degradation, their detection rate collapses to near-zero (18.8% for bicycles at $\epsilon=40$). The gap between protected large vehicles (buses/trucks) and vulnerable small vehicles widens under attack.

### Adversarial Training and Input Validation for this Detector:
- **Input Validation**:
  - *Channel Distribution Check*: Compute image-wide color statistics (e.g., $\Delta_{rg} = \bar{R} - \bar{G}$, $\Delta_{rb} = \bar{R} - \bar{B}$). If the red channel is systematically suppressed relative to green and blue compared to the camera's calibrated baseline profile, trigger an adversarial tampering alert.
  - *Spatial Denoising / Pre-filtering*: Apply median filtering or Gaussian smoothing before feeding the image to the detector. Uniform single-pixel channel nudges ($\epsilon \le 20$) are smoothed out by neighborhood averaging, preserving core reddish blob centroids.
- **Adversarial Training**:
  - In a deep CNN/Transformer detector (e.g. YOLO/RT-DETR), adversarial training involves generating multi-step FGSM/PGD perturbations during mini-batch training and computing the loss over perturbed inputs. This forces the network to learn invariant shape, silhouette, and contextual cues rather than relying on high-frequency color shortcuts.
  - For this rule-based detector, "adversarial training" would mean parameter calibration: replacing fixed, rigid thresholds ($R > 120, R - G > 40$) with adaptive thresholds conditioned on local background luminance, or training a soft logistic/linear classifier over perturbed samples to expand the decision boundary margin.

### Why does a simple rule break more easily than a CNN?
- The mock detector is a **discontinuous, non-differentiable step function** evaluated directly on raw RGB channels without spatial hierarchy or feature invariance. Shifting $R$ down by $\epsilon$ and $G, B$ up by $\epsilon$ changes the margin $(R - G)$ by $2\epsilon$. At $\epsilon=20$, the difference drops by 40 points—instantly pushing marginal pixels below the threshold, destroying connected components, and dropping the blob size below 20 pixels.
- A **CNN**, by contrast, builds distributed hierarchical representations across multiple convolutional layers. Neurons in deeper layers respond to edges, gradients, textures, aspect ratios, and spatial relationships across many receptive fields. A uniform low-frequency color shift changes the DC component of an image but leaves gradient orientations and edge contrasts largely intact. While CNNs remain vulnerable to subtle high-frequency gradient-based perturbations aligned with network loss gradients, they are vastly more robust against naive, uniform color perturbations than a brittle single-pixel threshold rule.
