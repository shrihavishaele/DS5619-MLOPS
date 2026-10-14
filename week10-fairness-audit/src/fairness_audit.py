"""
Class-based performance disparity audit for the vehicle detector — this
week's lecture content ("Per-Group Fairness Metrics Must Be Monitored
Continuously") applied concretely.

A NOTE ON FRAMING: real fairness audits (Fairlearn, demographic parity,
equalized odds) measure disparity across PROTECTED DEMOGRAPHIC GROUPS.
BMD-45 is a vehicle-detection dataset with no demographic attributes, so
this lab applies the same underlying methodology — measure a quality metric
independently per group, then flag groups that fall below the rest — to
vehicle CLASSES instead. The statistics and the code are identical to a
real fairness audit; only the grouping variable differs. Don't walk away
thinking "vehicle class" and "protected group" are the same thing — the
audit technique generalizes, the ethical stakes of what you're auditing do
not.

The metric here is per-class RECALL: of all the ground-truth vehicles of a
given class, what fraction did the detector find at all (regardless of
what class label it guessed)? Small-vehicle classes (bicycles,
two-wheelers) are the ones a real detector — and this mock one — tend to
miss more; that's the disparity this audit should surface.

In the lecture's terms, per-class recall is the equal-opportunity check
(true-positive rate per group), not demographic parity (selection rate per
group). Each class has only ~5-30 ground-truth boxes, so a small recall gap
can be sampling noise; other mid-sized classes may also fall below the
threshold for some student IDs.

Fill in the four functions marked # TODO. (adversarial.py adds three more
for the robustness half of this lab.)
"""
import glob
import json
import os
import sys
from collections import defaultdict

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mock_detector as det


# ---------------------------------------------------------------------------
# Part 1 — Intersection over Union between two [x, y, w, h] boxes
# ---------------------------------------------------------------------------

def compute_iou(box_a, box_b):
    """box_a and box_b are [x, y, w, h]. Return the Intersection-over-Union
    (a float in [0.0, 1.0]) between them.

    Steps:
      1. Convert each box to (x1, y1, x2, y2) corners.
      2. Compute the intersection rectangle's width/height (clamp to >= 0 —
         non-overlapping boxes have zero intersection, not negative).
      3. intersection_area = inter_w * inter_h
      4. union_area = area(box_a) + area(box_b) - intersection_area
      5. Return intersection_area / union_area, or 0.0 if union_area is 0.
    """
    # 1. Convert [x, y, w, h] to (x1, y1, x2, y2) corners
    ax1, ay1 = box_a[0], box_a[1]
    ax2, ay2 = ax1 + box_a[2], ay1 + box_a[3]

    bx1, by1 = box_b[0], box_b[1]
    bx2, by2 = bx1 + box_b[2], by1 + box_b[3]

    # 2. Intersection rectangle (clamp to >= 0)
    inter_w = max(0, min(ax2, bx2) - max(ax1, bx1))
    inter_h = max(0, min(ay2, by2) - max(ay1, by1))

    # 3. Intersection area
    intersection_area = inter_w * inter_h

    # 4. Union area
    area_a = box_a[2] * box_a[3]
    area_b = box_b[2] * box_b[3]
    union_area = area_a + area_b - intersection_area

    # 5. IoU
    if union_area == 0:
        return 0.0
    return intersection_area / union_area


# ---------------------------------------------------------------------------
# Part 2 — Was each ground-truth box found by ANY detection?
# ---------------------------------------------------------------------------

def match_ground_truth(gt_boxes, detections, iou_threshold=0.3):
    """`gt_boxes` is a list of [x, y, w, h]. `detections` is a list of
    mock_detector.Detection objects (each has a .bbox attribute, also
    [x, y, w, h]).

    Return a list of booleans, same length and order as gt_boxes: True if
    that ground-truth box has IoU >= iou_threshold with AT LEAST ONE
    detection (use compute_iou), False otherwise.

    Note: this is a recall check, not one-to-one matching — the same
    detection CAN count as a match for more than one ground-truth box if it
    happens to overlap both (rare with real data, fine for this audit).
    """
    results = []
    for gt_box in gt_boxes:
        matched = False
        for d in detections:
            if compute_iou(gt_box, d.bbox) >= iou_threshold:
                matched = True
                break
        results.append(matched)
    return results


# ---------------------------------------------------------------------------
# Part 3 — Run the audit across every image and every class
# ---------------------------------------------------------------------------

def audit_by_category(coco_path, fixtures_dir, iou_threshold=0.3, transform=None):
    """Load the COCO annotation file at `coco_path` (has "images",
    "annotations", "categories" keys — see data/fixtures/_annotations.coco.json
    for the exact shape). For every image, run the detector once, then use
    match_ground_truth to check every ground-truth box in that image.

    Accumulate, per category NAME (not id — look up the name from
    "categories"): total ground-truth boxes seen, and how many were
    detected. Return a dict:

      {category_name: {"total": int, "detected": int, "recall": float}}

    "recall" = detected / total, rounded to 4 decimal places. Skip (don't
    include in the result) any category with zero ground-truth boxes in
    this dataset — division by zero isn't meaningful there.

    `transform` is an optional function PIL Image -> PIL Image. If it is not
    None, apply it to each image (converted to RGB) right before running
    the detector — Part 6 (adversarial.py) uses this to audit perturbed
    images. Ground-truth boxes are never transformed.

    Hint: build a lookup from image_id -> list of its annotations, and a
    lookup from category_id -> category name, before the main loop. Image
    file paths are `os.path.join(fixtures_dir, image["file_name"])`.
    """
    with open(coco_path) as f:
        coco = json.load(f)

    # Build lookup: category_id -> category name
    cat_id_to_name = {cat["id"]: cat["name"] for cat in coco["categories"]}

    # Build lookup: image_id -> list of annotations
    img_id_to_anns = defaultdict(list)
    for ann in coco["annotations"]:
        img_id_to_anns[ann["image_id"]].append(ann)

    # Accumulate per-category totals
    cat_total = defaultdict(int)
    cat_detected = defaultdict(int)

    for image in coco["images"]:
        img_path = os.path.join(fixtures_dir, image["file_name"])
        img = Image.open(img_path).convert("RGB")

        # Apply transform if provided (for adversarial perturbation)
        if transform is not None:
            img = transform(img)

        # Run detector on (possibly transformed) image
        detections = det.detect(img)

        # Get ground-truth annotations for this image
        anns = img_id_to_anns[image["id"]]

        # Group annotations by category
        anns_by_cat = defaultdict(list)
        for ann in anns:
            anns_by_cat[ann["category_id"]].append(ann["bbox"])

        # Match ground-truth boxes against detections, per category
        for cat_id, gt_boxes in anns_by_cat.items():
            cat_name = cat_id_to_name[cat_id]
            matched = match_ground_truth(gt_boxes, detections, iou_threshold)
            cat_total[cat_name] += len(gt_boxes)
            cat_detected[cat_name] += sum(matched)

    # Build result dict, skipping categories with zero total
    result = {}
    for cat_name in cat_total:
        total = cat_total[cat_name]
        if total == 0:
            continue
        detected = cat_detected[cat_name]
        recall = round(detected / total, 4)
        result[cat_name] = {"total": total, "detected": detected, "recall": recall}

    return result


# ---------------------------------------------------------------------------
# Part 4 — Surface the categories that fall below the bar
# ---------------------------------------------------------------------------

def find_underperforming_categories(category_stats, recall_threshold=0.90):
    """`category_stats` is the dict returned by audit_by_category.

    Return a list of (category_name, recall) tuples for every category
    whose recall is BELOW recall_threshold, sorted worst-first (lowest
    recall first).
    """
    underperforming = [
        (name, stats["recall"])
        for name, stats in category_stats.items()
        if stats["recall"] < recall_threshold
    ]
    # Sort worst-first (lowest recall first)
    underperforming.sort(key=lambda x: x[1])
    return underperforming
