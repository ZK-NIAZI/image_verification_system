# Day 1 Research — AI Image Verification System

**Project:** AI Powered Image Verification System
**Day:** 1 — Core Logic & Face Detection
**Date:** 2026-02-16

---

## What Are We Building?

A system that looks at an uploaded image and checks three things:

1. Is there a **face** in the image?
2. Is the image **clear** (not blurry)?
3. Is the **lighting** good (not too dark or too bright)?

If all three pass → image is verified. If any one fails → image is rejected.

---

## Part 1 — Which Tool to Use for Face Detection?

We compared two tools: **MediaPipe** and **MTCNN**

### MediaPipe
- Made by Google
- Very fast — detects face in under 5ms
- Works on a normal laptop (no GPU needed)
- Easy to install: `pip install mediapipe`
- Small and lightweight

### MTCNN
- Deep learning based model
- Slower — takes 30 to 80ms per image
- Needs TensorFlow (very heavy to install)
- Requires a GPU to run fast
- Not suitable for lightweight systems

### Decision — We chose MediaPipe

**Why?** Our system needs to be fast and easy to run on any machine. MediaPipe does the job well without needing heavy libraries or a GPU. MTCNN is more accurate but too heavy for this project.

---

## Part 2 — How to Check if Image is Blurry?

We use a method called **Laplacian Variance**.

**Simple explanation:**
- A sharp image has clear edges between objects
- A blurry image has soft/unclear edges
- OpenCV checks these edges and gives a number called **variance**
- High number = sharp image, Low number = blurry image

**Code used:**
```python
import cv2
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
variance = cv2.Laplacian(gray, cv2.CV_64F).var()
```

**Our threshold:**

| Variance Score | Meaning | Result |
|---|---|---|
| 0 – 50 | Very blurry | Reject |
| 50 – 100 | Borderline | Soft Reject |
| Above 100 | Clear image | Accept |

**Rule: variance must be above 100 to pass.**

---

## Part 3 — How to Check Lighting?

We use **Mean Pixel Intensity** (average brightness of the image).

**Simple explanation:**
- Every pixel in a grayscale image has a value from 0 (black) to 255 (white)
- We take the average of all pixel values
- Too low = image is too dark, Too high = image is too bright

**Code used:**
```python
import cv2, numpy as np
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
mean_intensity = np.mean(gray)
```

**Our threshold:**

| Mean Value | Meaning | Result |
|---|---|---|
| 0 – 40 | Too dark | Reject |
| 40 – 200 | Good lighting | Accept |
| 200 – 255 | Too bright | Reject |

**Rule: mean pixel value must be between 40 and 200 to pass.**

---

## Part 4 — Project Folder Structure

```
image_verification_system/
│
├── src/
│   ├── face_detector.py       # face detection using MediaPipe
│   ├── clarity_check.py       # blur check using Laplacian
│   ├── lighting_check.py      # lighting check using pixel intensity
│   └── __init__.py
│
├── tests/
│   └── test.py           # basic tests
│
├── assets/
│       # for test image
│
├── docs/
│   └── day1_research.md       # this file
│
├── requirements.txt
└── main.py                    # runs the full verification
```

---

## Summary — All Decisions in One Place

| What | Decision | Why |
|---|---|---|
| Face detection tool | MediaPipe | Fast, lightweight, no GPU needed |
| Blur detection | Laplacian Variance | Simple and works well with OpenCV |
| Blur threshold | variance > 100 | Standard value for image verification |
| Lighting detection | Mean Pixel Intensity | Fast and reliable |
| Lighting range | 40 to 200 | Covers normal indoor and outdoor lighting |

---