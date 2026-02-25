# ─────────────────────────────────────────────────────────────
# lighting_check.py
# AI Image Verification System — Day 4
#
# Detects if an image has good lighting or is too dark/bright
# using mean pixel intensity analysis.
# ─────────────────────────────────────────────────────────────

import cv2
import numpy as np
import sys
import os

# Add project root to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LIGHTING_MIN, LIGHTING_MAX


# ── Error Codes ───────────────────────────────────────────────
GOOD_LIGHTING  = "GOOD_LIGHTING"
TOO_DARK       = "TOO_DARK"
TOO_BRIGHT     = "TOO_BRIGHT"
INVALID_IMAGE  = "INVALID_IMAGE"


# ── Main Function ─────────────────────────────────────────────
def check_lighting(image, gray=None):
    """
    Checks if an image has acceptable lighting levels.

    How it works:
    1. Convert image to grayscale (or use pre-computed grayscale)
    2. Calculate mean pixel intensity (average brightness)
    3. Compare against min/max thresholds
    4. Reject if too dark or too bright

    Pixel intensity scale:
      0 = pure black
      128 = medium gray
      255 = pure white

    Args:
        image: BGR numpy array from cv2.imread
        gray:  Optional pre-computed grayscale image (avoids re-conversion)

    Returns a dictionary:
    {
        "status"         : "GOOD_LIGHTING" / "TOO_DARK" / "TOO_BRIGHT" / "INVALID_IMAGE",
        "mean_intensity" : average brightness value (float),
        "min_threshold"  : minimum acceptable brightness (int),
        "max_threshold"  : maximum acceptable brightness (int),
        "message"        : plain English explanation (str)
    }
    """

    # Step 1 — Check if image is valid
    if image is None:
        return _result(INVALID_IMAGE, 0.0, LIGHTING_MIN, LIGHTING_MAX,
                       "Image could not be loaded. Check the file path.")

    # Step 2 — Convert to grayscale (or reuse pre-computed)
    if gray is None:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 3 — Calculate mean pixel intensity (average brightness)
    mean_intensity = np.mean(gray)

    # Step 4 — Compare against thresholds
    if mean_intensity < LIGHTING_MIN:
        return _result(TOO_DARK, mean_intensity, LIGHTING_MIN, LIGHTING_MAX,
                       f"Image is too dark (mean: {mean_intensity:.2f}, "
                       f"minimum: {LIGHTING_MIN}). Please upload a well-lit photo.")

    elif mean_intensity > LIGHTING_MAX:
        return _result(TOO_BRIGHT, mean_intensity, LIGHTING_MIN, LIGHTING_MAX,
                       f"Image is too bright/overexposed (mean: {mean_intensity:.2f}, "
                       f"maximum: {LIGHTING_MAX}). Please upload a photo with less light.")

    else:
        return _result(GOOD_LIGHTING, mean_intensity, LIGHTING_MIN, LIGHTING_MAX,
                       f"Lighting is good (mean: {mean_intensity:.2f}).")


# ── Helper: Build result dictionary ──────────────────────────
def _result(status, mean_intensity, min_threshold, max_threshold, message):
    return {
        "status"         : status,
        "mean_intensity" : round(mean_intensity, 2),  # round to 2 decimal places
        "min_threshold"  : min_threshold,
        "max_threshold"  : max_threshold,
        "message"        : message
    }


# ── Utility: Calculate intensity for any image (testing helper) ───
def calculate_intensity(image_path):
    """
    Helper function to quickly check the mean intensity of any image.
    Useful for testing and finding good threshold values.

    Usage:
        from src.lighting_check import calculate_intensity
        calculate_intensity("assets/my_photo.jpg")
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_intensity = np.mean(gray)
    print(f"Image: {image_path}")
    print(f"Mean Intensity: {mean_intensity:.2f}")
    print(f"Thresholds: {LIGHTING_MIN} (min) - {LIGHTING_MAX} (max)")
    return mean_intensity