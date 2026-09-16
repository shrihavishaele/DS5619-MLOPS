# Docker verification

Fill this in after you build and run your container (see README.md,
"Part 2 — Dockerfile"). This is how we confirm your container actually works, since an
automated grader running in a sandbox may not always have Docker-in-Docker
available.

## Build

Paste the command you ran and its final output line (the one showing the
built image ID/tag):

```
$ docker build -t week6-detector .
 => => naming to docker.io/library/week6-detector:latest                   0.0s 
 => => unpacking to docker.io/library/week6-detector:latest                0.0s 
```

## Run

Paste the command you used to start the container (should map a host port
to the container's 8080):

```
$ docker run --rm -p 8080:8080 week6-detector
 * Serving Flask app 'app'
 * Running on all addresses (0.0.0.0)
 * Running on http://0.0.0.0:8080
```

## Verify

Paste the exact `curl` commands and their JSON output for both endpoints,
run against the running container (not against `python src/app.py` directly
— the point is to prove the *container* works):

```
$ curl http://localhost:8080/health
{"status":"ok"}

$ curl -F "image=@data/fixtures/camera_A_daylight/000.jpg" http://localhost:8080/detect
{"count":5,"detections":[{"bbox":[116,34,23,23],"category_id":11,"id":0,"image_id":0,"score":0.98},{"bbox":[23,80,39,19],"category_id":13,"id":1,"image_id":0,"score":0.98},{"bbox":[218,83,45,27],"category_id":11,"id":2,"image_id":0,"score":0.98},{"bbox":[208,104,44,12],"category_id":10,"id":3,"image_id":0,"score":0.98},{"bbox":[160,132,27,16],"category_id":12,"id":4,"image_id":0,"score":0.98}]}
```
