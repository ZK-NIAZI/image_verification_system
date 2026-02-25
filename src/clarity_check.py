# ─────────────────────────────────────────────────────────────
# clarity_check.py
# AI Image Verification System — Day 3
#
# Detects if an image is blurry or clear using Laplacian variance.
# Blurry images are rejected for verification.
# ─────────────────────────────────────────────────────────────

import cv2
import sys
import os

# Add project root to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BLUR_THRESHOLD


# ── Error Codes
CLEAR          = "CLEAR"
TOO_BLURRY     = "TOO_BLURRY"
INVALID_IMAGE  = "INVALID_IMAGE"


# ── Main Function
def check_clarity(image, gray=None):
    """
    Checks if an image is clear or blurry using Laplacian variance.

    How it works:
    1. Convert image to grayscale (or use pre-computed grayscale)
    2. Apply Laplacian operator (detects edges)
    3. Calculate variance (measures edge sharpness)
    4. Compare against threshold

    Args:
        image: BGR numpy array from cv2.imread
        gray:  Optional pre-computed grayscale image (avoids re-conversion)

    Returns a dictionary:
    {
        "status"   : "CLEAR" / "TOO_BLURRY" / "INVALID_IMAGE",
        "variance" : calculated Laplacian variance (float),
        "threshold": the threshold used for comparison (int),
        "message"  : plain English explanation (str)
    }
    """

    # Step 1 — Check if image is valid
    if image is None:
        return _result(INVALID_IMAGE, 0.0, BLUR_THRESHOLD,
                       "Image could not be loaded. Check the file path.")

    # Step 2 — Convert to grayscale (or reuse pre-computed)
    if gray is None:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 3 — Apply Laplacian filter and calculate variance
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance  = laplacian.var()

    # Step 4 — Compare against threshold
    if variance < BLUR_THRESHOLD:
        return _result(TOO_BLURRY, variance, BLUR_THRESHOLD,
                       f"Image is too blurry (variance: {variance:.2f}, "
                       f"threshold: {BLUR_THRESHOLD}). Please upload a clear, in-focus photo.")
    else:
        return _result(CLEAR, variance, BLUR_THRESHOLD,
                       f"Image is clear (variance: {variance:.2f}).")


# ── Build result dictionary
def _result(status, variance, threshold, message):
    return {
        "status"    : status,
        "variance"  : round(variance, 2),  # round to 2 decimal places
        "threshold" : threshold,
        "message"   : message
    }


# ── Calculate variance for any image (testing helper)
def calculate_variance(image_path):
    """
    Helper function to quickly check the variance of any image.
    Useful for testing and finding good threshold values.

    Usage:
        from src.clarity_check import calculate_variance
        calculate_variance("assets/my_photo.jpg")
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    print(f"Image: {image_path}")
    print(f"Variance: {variance:.2f}")
    return variance