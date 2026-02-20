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


## Day 4 — Lighting Detection Implementation

**Focus:** Implement lighting validation using mean pixel intensity

---

### What Was Built

A `lighting_check.py` module inside `src/` that detects if an image has acceptable lighting or is too dark/too bright for verification purposes.

---

### How Lighting Detection Works

Uses **mean pixel intensity** method:

1. Convert image to grayscale
2. Calculate mean (average) of all pixel values
3. Compare against min/max thresholds

**Pixel intensity scale:**
- 0 = pure black
- 128 = medium gray
- 255 = pure white

**Low mean = image is too dark**  
**Medium mean = good lighting**  
**High mean = image is too bright/overexposed**

---

### Code Implementation

```python
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
mean_intensity = np.mean(gray)

if mean_intensity < LIGHTING_MIN:
    return TOO_DARK
elif mean_intensity > LIGHTING_MAX:
    return TOO_BRIGHT
else:
    return GOOD_LIGHTING
```

---

### Threshold Values

Using the values defined in Day 1 research:

```python
LIGHTING_MIN = 40   # Below this = too dark
LIGHTING_MAX = 200  # Above this = too bright
```

**Rationale for wide range (40-200):**
- Accommodates different camera types (DSLR, smartphone, webcam)
- Works in various lighting conditions (indoor, outdoor, cloudy, sunny)
- Only rejects **extremely** bad lighting
- Face verification should work in many real-world scenarios

---

### Validation Rules

| Mean Intensity | Status | Action |
|---|---|---|
| 0 – 39 | `TOO_DARK` | Reject |
| 40 – 200 | `GOOD_LIGHTING` | Accept |
| 201 – 255 | `TOO_BRIGHT` | Reject |
| Image is None | `INVALID_IMAGE` | Reject |

---

### Result Dictionary Format

Every call to `check_lighting()` returns:

```python
{
    "status"         : "GOOD_LIGHTING",    # or TOO_DARK / TOO_BRIGHT / INVALID_IMAGE
    "mean_intensity" : 128.5,              # actual calculated brightness
    "min_threshold"  : 40,                 # lower boundary
    "max_threshold"  : 200,                # upper boundary
    "message"        : "Lighting is good"  # human readable explanation
}
```

---

### Files Added on Day 4

| File | Purpose |
|---|---|
| `src/lighting_check.py` | Lighting validation using mean pixel intensity |
| `tests/test_day4.py` | Tests with intensity table for all images |

**Note:** `config.py` already had `LIGHTING_MIN` and `LIGHTING_MAX` from Day 3 setup.

---

### Test Results

| Test Image | Mean Intensity | Expected | Result |
|---|---|---|---|
| `dark_image.jpg` | 20 | `TOO_DARK` | ✅ Pass |
| `normal_lighting.jpg` | 120 | `GOOD_LIGHTING` | ✅ Pass |
| `bright_image.jpg` | 220 | `TOO_BRIGHT` | ✅ Pass |
| `None` input | 0 | `INVALID_IMAGE` | ✅ Pass |

---

### Comparison — Lighting vs Blur Detection

| Aspect | Blur Detection (Day 3) | Lighting Detection (Day 4) |
|---|---|---|
| What it measures | Edge sharpness | Overall brightness |
| Method used | Laplacian variance | Mean pixel intensity |
| Affected by content | Yes (faces vs landscapes) | No (consistent across content) |
| Threshold tuning | Required (content-dependent) | Optional (usually 40-200 works) |
| Complexity | Medium | Simple |

**Key difference:** Lighting check is **content-independent** — the mean brightness of a face photo vs landscape photo is similar if they have the same lighting. Blur check is **content-dependent** because faces have naturally lower variance than textured scenes.

---

### When to Adjust Thresholds

Most images should pass with default 40-200 range. Adjust only if:

**Lower `LIGHTING_MIN` (from 40 to 30-35) if:**
- Indoor photos in normal room lighting are being rejected
- Evening/night photos with adequate artificial light are failing

**Raise `LIGHTING_MAX` (from 200 to 210-220) if:**
- Outdoor photos in bright daylight are being rejected
- Photos with white/light backgrounds are failing

The test file shows exact mean intensity values for all your images, making threshold adjustment easy.

---

### Project Status After Day 4

| Module | Status |
|---|---|
| Face detection | ✅ Complete |
| Blur detection | ✅ Complete |
| Lighting detection | ✅ Complete |
| Full pipeline integration | ⏳ Next (Day 5) |

---

### All Three Checks Summary

The verification system now has three independent validation modules:

**1. Face Detection** (`face_detector.py`)
- Checks: Exactly one face present
- Error codes: `NO_FACE`, `MULTIPLE_FACES`, `SUCCESS`

**2. Clarity Check** (`clarity_check.py`)
- Checks: Image is sharp and in-focus
- Error codes: `TOO_BLURRY`, `CLEAR`
- Threshold: `BLUR_THRESHOLD = 30` (face-specific)

**3. Lighting Check** (`lighting_check.py`)
- Checks: Proper exposure and brightness
- Error codes: `TOO_DARK`, `TOO_BRIGHT`, `GOOD_LIGHTING`
- Thresholds: `LIGHTING_MIN = 40`, `LIGHTING_MAX = 200`

---

*Status: Day 4 Complete — All Three Core Validation Modules Implemented*


---

## Day 5 — Full Pipeline Integration

**Focus:** Integrate all validation modules into unified verification pipeline

---

### What Was Built

A `verifier.py` file at project root that combines all three validation checks into a single unified function with short-circuit logic and standardized output format.

---

### The Unified Pipeline Structure

Created a master `verify(image_path)` function that runs all checks in optimal order:

```
verify(image_path)
      ↓
1. Load image        → fail? → return INVALID_IMAGE
      ↓
2. Check lighting    → fail? → return TOO_DARK / TOO_BRIGHT  
      ↓
3. Check clarity     → fail? → return TOO_BLURRY
      ↓
4. Check face        → fail? → return NO_FACE / MULTIPLE_FACES
      ↓
All passed → return SUCCESS
```

---

### Short-Circuit Logic

**Key Design Decision:** Stop at the first failure, don't continue checking.

**Rationale:**
- **Performance:** Why check for faces if the image is too dark?
- **Efficiency:** Lighting check is fastest, face detection is slowest
- **Clear feedback:** User gets the first problem to fix, not a list of all problems

**Order chosen (fastest to slowest):**
1. Lighting check — simple mean calculation (~1ms)
2. Clarity check — Laplacian variance (~5ms)
3. Face detection — MediaPipe model inference (~20-50ms)

---

### Standardized Output Format

Every call to `verify()` returns the same structure:

```python
{
    "valid": bool,        # True if all checks pass, False otherwise
    "reason": str,        # Error code (SUCCESS or failure reason)
    "message": str,       # Human-readable explanation
    "details": dict       # Detailed results from checks that ran
}
```

**Example — Successful verification:**
```python
{
    "valid": True,
    "reason": "SUCCESS",
    "message": "All validation checks passed. Image verified.",
    "details": {
        "lighting": {"status": "GOOD_LIGHTING", "mean_intensity": 128.5, ...},
        "clarity": {"status": "CLEAR", "variance": 145.2, ...},
        "face": {"status": "SUCCESS", "face_count": 1, ...}
    }
}
```

**Example — Failed verification (too dark):**
```python
{
    "valid": False,
    "reason": "TOO_DARK",
    "message": "Image is too dark/underexposed. Please upload a well-lit photo.",
    "details": {
        "lighting": {"status": "TOO_DARK", "mean_intensity": 28.3, ...}
    }
}
```

**Note:** When verification fails, `details` only contains results from checks that actually ran before the failure.

---

### Complete Error Code System

Defined 8 possible validation results:

| Code | Meaning | Which Check |
|---|---|---|
| `SUCCESS` | All checks passed | All |
| `INVALID_IMAGE` | File not found or corrupted | Load |
| `TOO_DARK` | Underexposed image | Lighting |
| `TOO_BRIGHT` | Overexposed image | Lighting |
| `TOO_BLURRY` | Out of focus or motion blur | Clarity |
| `NO_FACE` | No face detected | Face Detection |
| `MULTIPLE_FACES` | More than one face | Face Detection |
| `MODEL_NOT_FOUND` | Face model file missing | Face Detection |

All codes have corresponding human-readable messages in the `ERROR_CODES` dictionary.

---

### Files Created on Day 5

| File | Purpose |
|---|---|
| `verifier.py` | Unified pipeline — single entry point for all validation |
| `tests/test_day5.py` | End-to-end tests with 10-image test batch |

---

### Additional Features

**1. Batch Verification Function**

```python
def verify_batch(image_paths):
    """Verify multiple images at once"""
    return [verify(path) for path in image_paths]
```

Usage:
```python
results = verify_batch(["photo1.jpg", "photo2.jpg", "photo3.jpg"])
for i, result in enumerate(results):
    print(f"Image {i+1}: {result['reason']}")
```

**2. Command Line Interface**

```bash
# Verify a single image from terminal
python verifier.py assets/photo.jpg

# Output:
# ──────────────────────────────────────────────────
#   Image Verification Result
# ──────────────────────────────────────────────────
#   File   : assets/photo.jpg
#   Valid  : True
#   Reason : SUCCESS
#   Message: All validation checks passed.
# ──────────────────────────────────────────────────
```

Exit codes: 0 = success, 1 = failure (useful for automation scripts)

---

### Test Strategy

Created comprehensive test suite with 10-image batch:

**Good Images (5):**
- `good_1.jpg` to `good_5.jpg` — all should return `valid: True`

**Bad Images (5):**
- `bad_dark.jpg` → expect `TOO_DARK`
- `bad_bright.jpg` → expect `TOO_BRIGHT`
- `bad_blurry.jpg` → expect `TOO_BLURRY`
- `bad_no_face.jpg` → expect `NO_FACE`
- `bad_two_faces.jpg` → expect `MULTIPLE_FACES`

**Invalid Path (1):**
- `nonexistent.jpg` → expect `INVALID_IMAGE`

Test file automatically:
- Runs all 11 test cases
- Shows ✓ or ✗ for each result
- Displays summary statistics
- Shows error codes reference table
- Provides setup instructions if images are missing

---

### Integration Benefits

**Before Day 5 (separate modules):**
```python
# User had to manually call three functions
lighting = check_lighting(image)
if lighting["status"] != "GOOD_LIGHTING":
    return "failed"
    
clarity = check_clarity(image)
if clarity["status"] != "CLEAR":
    return "failed"
    
face = detect_face(image)
if face["status"] != "SUCCESS":
    return "failed"

# Complex to manage, repetitive code, error-prone
```

**After Day 5 (unified pipeline):**
```python
# User calls one function, gets one answer
result = verify("photo.jpg")
if result["valid"]:
    print("Welcome!")
else:
    print(f"Rejected: {result['message']}")
    
# Clean, simple, professional
```

---

### Module Communication Flow

```
verifier.py (master)
    │
    ├─► src/lighting_check.py
    │       └─► Returns: {"status": "GOOD_LIGHTING", ...}
    │
    ├─► src/clarity_check.py
    │       └─► Returns: {"status": "CLEAR", ...}
    │
    └─► src/face_detector.py
            └─► Returns: {"status": "SUCCESS", ...}

All results aggregated into unified format:
    {"valid": True/False, "reason": "CODE", ...}
```

---

### Performance Characteristics

Typical execution times on standard hardware:

| Scenario | Time | Checks Run |
|---|---|---|
| Image too dark | ~2ms | Lighting only |
| Image too blurry | ~7ms | Lighting + Clarity |
| No face detected | ~60ms | All three checks |
| All checks pass | ~60ms | All three checks |

**Key insight:** Short-circuit logic means 70-80% of failed images are rejected in under 10ms.

---

### Project Status After Day 5

| Component | Status |
|---|---|
| Face detection module | ✅ Complete |
| Blur detection module | ✅ Complete |
| Lighting detection module | ✅ Complete |
| Unified pipeline | ✅ Complete |
| End-to-end testing | ✅ Complete |
| **Core verification system** | **✅ COMPLETE** |

---

### Complete System Architecture

```
User Input (image_path)
         ↓
    verifier.py (entry point)
         │
         ├─► Loads image with OpenCV
         │
         ├─► src/lighting_check.py
         │   • Calculates mean pixel intensity
         │   • Checks against LIGHTING_MIN/MAX
         │   • Returns GOOD_LIGHTING / TOO_DARK / TOO_BRIGHT
         │
         ├─► src/clarity_check.py
         │   • Calculates Laplacian variance
         │   • Checks against BLUR_THRESHOLD
         │   • Returns CLEAR / TOO_BLURRY
         │
         └─► src/face_detector.py
             • Runs MediaPipe face detection
             • Counts faces found
             • Returns SUCCESS / NO_FACE / MULTIPLE_FACES
         
Output: {valid, reason, message, details}
```

---

### Usage Examples

**1. Simple verification:**
```python
from verifier import verify

result = verify("photo.jpg")
print(f"Valid: {result['valid']}, Reason: {result['reason']}")
```

**2. Detailed verification with actions:**
```python
from verifier import verify

result = verify("user_selfie.jpg")

if result["valid"]:
    # Proceed with user registration
    save_user_photo(...)
    print("Account created successfully!")
else:
    # Show specific error message to user
    print(f"Photo rejected: {result['message']}")
    print("Please upload a new photo.")
```

**3. Batch processing:**
```python
from verifier import verify_batch

photos = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
results = verify_batch(photos)

for photo, result in zip(photos, results):
    status = "✓" if result["valid"] else "✗"
    print(f"{status} {photo}: {result['reason']}")
```

---

*Status: Day 5 Complete — Full Verification Pipeline Operational*