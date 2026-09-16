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

The single biggest change would be to use a **multi-stage build**. Swapping in a real torch-based checkpoint (e.g. YOLOv12 via `ultralytics`) would add PyTorch (~2 GB), CUDA runtime libraries, and the model weights themselves, easily ballooning the image from ~234 MB to 5–8+ GB and build times from seconds to many minutes.

A multi-stage Dockerfile separates the *build* stage (where you install torch, compile any C extensions, and download model weights) from the *runtime* stage (where you copy in only the installed packages and weights the server actually needs). This avoids shipping pip caches, build tools, compiler toolchains, and intermediate build artifacts in the final image. You'd also switch the base image from `python:3.12-slim` to an NVIDIA CUDA runtime image (e.g. `nvidia/cuda:12.x-runtime-ubuntu22.04`) if GPU inference is needed, and pin the exact PyTorch wheel URL for the target CUDA version to avoid pulling unnecessary CPU/GPU variants.
