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

## Day 2 — Face Detection Implementation

**Focus:** Implement exactly one face validation using MediaPipe Tasks API

---

### What Was Built

A `face_detector.py` module inside `src/` that takes any image and checks if exactly one human face is present.

---

### Issue Found & Fixed

During implementation, `mp.solutions.face_detection` threw an attribute error on MediaPipe `0.10+` because Google removed the `solutions` API in newer versions.

**Fix applied:** Switched to the new **MediaPipe Tasks API** which works on all versions `0.10+`. This required downloading the `blaze_face_short_range.tflite` model file and placing it in the `models/` folder.

```
models/
└── blaze_face_short_range.tflite   ← downloaded separately
```

---

### How the Detection Works

1. Check model file is loaded
2. Check image is valid and not None
3. Convert image from BGR (OpenCV) → RGB (MediaPipe requirement)
4. Wrap image in `mp.Image()` format
5. Run `_detector.detect()` — MediaPipe scans for face patterns
6. Count faces in `detection_result.detections` list
7. Return result based on count

---

### Validation Rules

| Face Count | Status Code | Message |
|---|---|---|
| 0 | `NO_FACE` | No face detected |
| 1 | `SUCCESS` | Face verified |
| 2 or more | `MULTIPLE_FACES` | Multiple faces detected |
| Image is None | `INVALID_IMAGE` | Image could not be loaded |
| Model missing | `MODEL_NOT_FOUND` | Model file not found |

---

### Confidence Threshold

MediaPipe is set to `min_detection_confidence=0.6` — meaning it only counts a face if it is at least **60% confident** it found one. This prevents false detections from posters, photos on walls, or unclear shapes.

---

### Result Dictionary Format

Every call to `detect_face()` always returns this structure:

```python
{
    "status"     : "SUCCESS",         # error code for your logic
    "face_count" : 1,                 # exact number of faces found
    "message"    : "Face verified."   # human readable text for user
}
```

---

### Files Added on Day 2

| File | Purpose |
|---|---|
| `src/face_detector.py` | Main face detection logic |
| `tests/test_day2.py` | Tests for all 3 scenarios |
| `models/blaze_face_short_range.tflite` | MediaPipe model file |

---

### Test Results

| Test Image | Expected | Result |
|---|---|---|
| `assets/no_face.jpg` | `NO_FACE` | ✅ Pass |
| `assets/one_face.jpg` | `SUCCESS` | ✅ Pass |
| `assets/two_faces.jpg` | `MULTIPLE_FACES` | ✅ Pass |
| `None` input | `INVALID_IMAGE` | ✅ Pass |

---

*Status: Day 2 Complete — Face Detection Working*


## Day 3 — Blur Detection Implementation

**Focus:** Implement clarity check using Laplacian variance

---

### What Was Built

A `clarity_check.py` module inside `src/` that detects if an image is too blurry or acceptably clear for verification purposes.

---

### How Blur Detection Works

Uses **Laplacian variance** method:

1. Convert image to grayscale
2. Apply Laplacian operator (edge detection filter)
3. Calculate variance of the result
4. Compare against threshold

**High variance = many sharp edges = clear image**  
**Low variance = few/soft edges = blurry image**

---

### Code Implementation

```python
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
laplacian = cv2.Laplacian(gray, cv2.CV_64F)
variance = laplacian.var()

if variance < BLUR_THRESHOLD:
    return TOO_BLURRY
else:
    return CLEAR
```

---

### Critical Discovery — Content Type Matters

During testing, discovered that **variance depends on image content**, not just blur:

| Content Type | Typical Variance Range |
|---|---|
| Face photos (smooth skin) | 30-80 |
| Landscape/objects (textures) | 80-200+ |
| Blurry face photos | 10-30 |

**Key Learning:** Since this is a face verification system, the threshold must be tuned specifically for face photos, not general images.

---

### Threshold Calibration Process

**Initial attempt:** `BLUR_THRESHOLD = 100` (from general research)  
**Problem:** Too strict — rejected clear face photos with variance 45-85

**Solution:** Test with actual face photos and adjust threshold based on results.

**Test Results with Face Photos:**
- Clear face selfie: variance = 45
- Blurry face selfie: variance = 18
- **Optimal threshold: 30** (sits between blurry and clear)

---

### Final Threshold Value

```python
BLUR_THRESHOLD = 30  # Tuned for face verification
```

**Rationale:** 
- Accepts clear face photos (variance 40-80)
- Rejects blurry face photos (variance under 30)
- Specific to face verification use case

---

### Validation Rules

| Variance | Status | Action |
|---|---|---|
| Under 30 | `TOO_BLURRY` | Reject |
| 30 and above | `CLEAR` | Accept |
| Image is None | `INVALID_IMAGE` | Reject |

---

### Result Dictionary Format

Every call to `check_clarity()` returns:

```python
{
    "status"    : "CLEAR",           # or TOO_BLURRY / INVALID_IMAGE
    "variance"  : 45.23,             # actual calculated variance
    "threshold" : 30,                # threshold used for comparison
    "message"   : "Image is clear"   # human readable explanation
}
```

---

### Files Added on Day 3

| File | Purpose |
|---|---|
| `src/clarity_check.py` | Blur detection logic using Laplacian variance |
| `config.py` | Centralized configuration with BLUR_THRESHOLD |
| `tests/test_day3.py` | Tests with variance table for threshold tuning |

---

### Configuration Structure

Created `config.py` at project root to store all thresholds in one place:

```python
BLUR_THRESHOLD = 30              # Clarity check
FACE_DETECTION_CONFIDENCE = 0.6  # Face detection
LIGHTING_MIN = 40                # Lighting check (Day 4)
LIGHTING_MAX = 200               # Lighting check (Day 4)
```

**Benefits:**
- Easy to adjust thresholds without changing code
- Single source of truth for all settings
- Well-documented with comments explaining each value

---

### Test Results

| Test Image | Variance | Expected | Result |
|---|---|---|---|
| `blurry_image.jpg` | 3.83 | `TOO_BLURRY` | ✅ Pass |
| `clear_image.jpg` | 186.62 | `CLEAR` | ✅ Pass |
| `one_face.jpg` | 45.39 | `CLEAR` | ✅ Pass |
| `two_face.jpg` | 41.67 | `CLEAR` | ✅ Pass |
| `None` input | 0 | `INVALID_IMAGE` | ✅ Pass |

---

### Lessons Learned

1. **Generic thresholds don't work** — must calibrate for your specific use case
2. **Content type affects variance** — faces have lower variance than landscapes
3. **Test with representative images** — use actual face photos, not random images
4. **Variance is not blur alone** — it measures edge density in the image
5. **Threshold tuning is essential** — always test with your own images and adjust

---

*Status: Day 3 Complete — Blur Detection Working with Optimized Threshold*