# ─────────────────────────────────────────────────────────────
# verifier.py
# AI Image Verification System
#
# Unified verification pipeline that combines all validation checks:
#   1. Lighting check (fastest)
#   2. Clarity/blur check (medium)
#   3. Face detection (slowest)
#
# Short-circuits on first failure to save processing time.
#
# Performance optimizations:
#   - Image resize cap (MAX_IMAGE_DIMENSION) before any checks
#   - Shared grayscale conversion for lighting + clarity
#   - verify_from_bytes() for in-memory decode (skips disk I/O)
#   - Per-stage timing instrumentation via time.perf_counter()
# ─────────────────────────────────────────────────────────────

import cv2
import sys
import os
import time
import numpy as np

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if os.path.exists(src_dir):
    sys.path.insert(0, current_dir)
    from src.lighting_check import check_lighting, GOOD_LIGHTING
    from src.clarity_check import check_clarity, CLEAR
    from src.face_detector import detect_face, SUCCESS
else:
    # Fallback for when running from outputs directory in testing
    try:
        from src.lighting_check import check_lighting, GOOD_LIGHTING
        from src.clarity_check import check_clarity, CLEAR
        from src.face_detector import detect_face, SUCCESS
    except ImportError:
        print("Error: Cannot find required modules.")
        print("Make sure verifier.py is in the project root with src/ folder.")
        sys.exit(1)

from config import MAX_IMAGE_DIMENSION, PERF_LOGGING_ENABLED


# ── Error Codes ───────────────────────────────────────────────
# All possible validation results
ERROR_CODES = {
    "SUCCESS": "All validation checks passed. Image verified.",
    "INVALID_IMAGE": "Image file not found or could not be loaded.",
    "TOO_DARK": "Image is too dark/underexposed. Please upload a well-lit photo.",
    "TOO_BRIGHT": "Image is too bright/overexposed. Please reduce lighting.",
    "TOO_BLURRY": "Image is blurry or out of focus. Please upload a sharp photo.",
    "NO_FACE": "No face detected. Please upload a photo with your face visible.",
    "MULTIPLE_FACES": "Multiple faces detected. Please upload a photo with only one person.",
    "MODEL_NOT_FOUND": "Face detection model file is missing.",
}


# ── Image Preprocessing ──────────────────────────────────────
def _preprocess_image(image):
    """
    Resize image so the longest side <= MAX_IMAGE_DIMENSION.
    Also pre-compute grayscale (shared by lighting + clarity checks).

    Returns:
        (resized_image, gray_image)
    """
    h, w = image.shape[:2]
    max_dim = max(h, w)

    if max_dim > MAX_IMAGE_DIMENSION:
        scale = MAX_IMAGE_DIMENSION / max_dim
        new_w = int(w * scale)
        new_h = int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image, gray


# ── Main Verification Function ────────────────────────────────
def verify(image_path):
    """
    Unified verification pipeline for image validation.
    
    Runs all checks in sequence with short-circuit logic:
      1. Lighting check (TOO_DARK / TOO_BRIGHT)
      2. Clarity check (TOO_BLURRY)
      3. Face detection (NO_FACE / MULTIPLE_FACES)
    
    Stops at the first failure and returns immediately.
    
    Args:
        image_path (str): Path to the image file to verify
    
    Returns:
        dict: {
            "valid": bool,              # True if all checks pass
            "reason": str,              # Error code
            "message": str,             # Human-readable explanation
            "details": dict,            # Detailed results from each check
            "inference_time_ms": float, # Total inference time in milliseconds
            "stage_times_ms": dict      # Per-stage timing breakdown
        }
    """
    stage_times = {}
    t_start = time.perf_counter()
    
    # Step 1: Load image
    t0 = time.perf_counter()
    image = cv2.imread(image_path)
    stage_times["load"] = _elapsed_ms(t0)
    
    if image is None:
        return _build_result(False, "INVALID_IMAGE",
                             stage_times=stage_times, t_start=t_start)
    
    # Step 2: Preprocess (resize + grayscale)
    t0 = time.perf_counter()
    image, gray = _preprocess_image(image)
    stage_times["preprocess"] = _elapsed_ms(t0)
    
    # Step 3: Check lighting (pass pre-computed grayscale)
    t0 = time.perf_counter()
    lighting_result = check_lighting(image, gray=gray)
    stage_times["lighting"] = _elapsed_ms(t0)
    
    if lighting_result["status"] != GOOD_LIGHTING:
        return _build_result(False, lighting_result["status"], {
            "lighting": lighting_result
        }, stage_times=stage_times, t_start=t_start)
    
    # Step 4: Check clarity/blur (pass pre-computed grayscale)
    t0 = time.perf_counter()
    clarity_result = check_clarity(image, gray=gray)
    stage_times["clarity"] = _elapsed_ms(t0)
    
    if clarity_result["status"] != CLEAR:
        return _build_result(False, clarity_result["status"], {
            "lighting": lighting_result,
            "clarity": clarity_result
        }, stage_times=stage_times, t_start=t_start)
    
    # Step 5: Check face detection (on resized image)
    t0 = time.perf_counter()
    face_result = detect_face(image)
    stage_times["face_detection"] = _elapsed_ms(t0)
    
    if face_result["status"] != SUCCESS:
        return _build_result(False, face_result["status"], {
            "lighting": lighting_result,
            "clarity": clarity_result,
            "face": face_result
        }, stage_times=stage_times, t_start=t_start)
    
    # All checks passed - image is valid
    return _build_result(True, "SUCCESS", {
        "lighting": lighting_result,
        "clarity": clarity_result,
        "face": face_result
    }, stage_times=stage_times, t_start=t_start)


# ── In-memory verification (no disk I/O) ─────────────────────
def verify_from_bytes(image_bytes):
    """
    Verify an image from raw bytes (e.g. from an upload).
    Decodes in-memory — no temp file needed.
    
    Args:
        image_bytes (bytes): Raw image file bytes (JPEG/PNG)
    
    Returns:
        Same dict as verify()
    """
    stage_times = {}
    t_start = time.perf_counter()
    
    # Step 1: Decode from memory
    t0 = time.perf_counter()
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    stage_times["load"] = _elapsed_ms(t0)
    
    if image is None:
        return _build_result(False, "INVALID_IMAGE",
                             stage_times=stage_times, t_start=t_start)
    
    # Step 2: Preprocess (resize + grayscale)
    t0 = time.perf_counter()
    image, gray = _preprocess_image(image)
    stage_times["preprocess"] = _elapsed_ms(t0)
    
    # Step 3: Check lighting
    t0 = time.perf_counter()
    lighting_result = check_lighting(image, gray=gray)
    stage_times["lighting"] = _elapsed_ms(t0)
    
    if lighting_result["status"] != GOOD_LIGHTING:
        return _build_result(False, lighting_result["status"], {
            "lighting": lighting_result
        }, stage_times=stage_times, t_start=t_start)
    
    # Step 4: Check clarity/blur
    t0 = time.perf_counter()
    clarity_result = check_clarity(image, gray=gray)
    stage_times["clarity"] = _elapsed_ms(t0)
    
    if clarity_result["status"] != CLEAR:
        return _build_result(False, clarity_result["status"], {
            "lighting": lighting_result,
            "clarity": clarity_result
        }, stage_times=stage_times, t_start=t_start)
    
    # Step 5: Check face detection
    t0 = time.perf_counter()
    face_result = detect_face(image)
    stage_times["face_detection"] = _elapsed_ms(t0)
    
    if face_result["status"] != SUCCESS:
        return _build_result(False, face_result["status"], {
            "lighting": lighting_result,
            "clarity": clarity_result,
            "face": face_result
        }, stage_times=stage_times, t_start=t_start)
    
    return _build_result(True, "SUCCESS", {
        "lighting": lighting_result,
        "clarity": clarity_result,
        "face": face_result
    }, stage_times=stage_times, t_start=t_start)


# ── Timing helper ────────────────────────────────────────────
def _elapsed_ms(t0):
    """Return milliseconds elapsed since t0."""
    return round((time.perf_counter() - t0) * 1000, 2)


# ── Helper: Build result dictionary ──────────────────────────
def _build_result(valid, reason, details=None, stage_times=None, t_start=None):
    """Build standardized result dictionary with optional timing data."""
    total_ms = round((time.perf_counter() - t_start) * 1000, 2) if t_start else 0
    result = {
        "valid": valid,
        "reason": reason,
        "message": ERROR_CODES.get(reason, "Unknown error"),
        "details": details or {},
    }
    if PERF_LOGGING_ENABLED:
        result["inference_time_ms"] = total_ms
        result["stage_times_ms"] = stage_times or {}
    return result


# ── Utility: Batch verification ──────────────────────────────
def verify_batch(image_paths):
    """
    Verify multiple images at once.
    
    Args:
        image_paths (list): List of image file paths
    
    Returns:
        list: List of verification results, one per image
    
    Example:
        paths = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
        results = verify_batch(paths)
        for i, result in enumerate(results):
            print(f"Image {i+1}: {result['reason']}")
    """
    return [verify(path) for path in image_paths]


# ── Command Line Interface ────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n  Usage: python verifier.py <image_path>")
        print("  Example: python verifier.py assets/photo.jpg\n")
        sys.exit(1)
    
    image_path = sys.argv[1]
    result = verify(image_path)
    
    print("\n" + "-" * 50)
    print(f"  Image Verification Result")
    print("-" * 50)
    print(f"  File   : {image_path}")
    print(f"  Valid  : {result['valid']}")
    print(f"  Reason : {result['reason']}")
    print(f"  Message: {result['message']}")
    if PERF_LOGGING_ENABLED:
        print(f"  Time   : {result.get('inference_time_ms', 'N/A')} ms")
        stage_times = result.get('stage_times_ms', {})
        if stage_times:
            print(f"  Stages : {stage_times}")
    print("-" * 50 + "\n")
    
    # Exit with appropriate code (0 = success, 1 = failure)
    sys.exit(0 if result["valid"] else 1)