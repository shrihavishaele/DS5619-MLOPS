# NOTES.md — Week 6: Containerize and Serve a Detector

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student_id: 142301003
seed: 2399502667
Wrote 6 images across 2 camera profiles -> D:\DS5619-MLOPS\week06-containerize-serve\data\fixtures
Wrote 19 annotations -> D:\DS5619-MLOPS\week06-containerize-serve\data\fixtures/_annotations.coco.json

## Built image size

<!-- What image size did `docker images` report for week6-detector? -->

```
$ docker images week6-detector
IMAGE                   ID             DISK USAGE   CONTENT SIZE
week6-detector:latest   e93f12d7cb52        234MB         57.5MB
```

The `week6-detector` image is **234 MB** on disk (57.5 MB compressed content size).

## Swapping in a real checkpoint

<!-- What's the single biggest thing you'd change about this Dockerfile if
     src/mock_detector.py were swapped for a real torch-based checkpoint?
     (Think about what that does to build time and image size.) -->

The most important change is using a **multi-stage build**. Real models like YOLOv12 (with PyTorch and CUDA) increase the image size from ~234 MB to 5-8+ GB.

A multi-stage Dockerfile separates the build stage (installing dependencies and weights) from the runtime stage (running the server). This keeps the final image small by removing build tools and caches. For GPU support, you should also switch to an NVIDIA CUDA runtime base image and install the specific PyTorch wheel for that CUDA version.
