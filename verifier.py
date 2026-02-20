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
# ─────────────────────────────────────────────────────────────

import cv2
import sys
import os

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
            "valid": bool,        # True if all checks pass, False otherwise
            "reason": str,        # Error code (SUCCESS or failure reason)
            "message": str,       # Human-readable explanation
            "details": dict       # Detailed results from each check (optional)
        }
    
    Example:
        result = verify("photo.jpg")
        if result["valid"]:
            print("Image verified successfully!")
        else:
            print(f"Verification failed: {result['message']}")
    """
    
    # Step 1: Load image
    image = cv2.imread(image_path)
    if image is None:
        return _build_result(False, "INVALID_IMAGE")
    
    # Step 2: Check lighting 
    lighting_result = check_lighting(image)
    if lighting_result["status"] != GOOD_LIGHTING:
        return _build_result(False, lighting_result["status"], {
            "lighting": lighting_result
        })
    
    # Step 3: Check clarity/blur 
    clarity_result = check_clarity(image)
    if clarity_result["status"] != CLEAR:
        return _build_result(False, clarity_result["status"], {
            "lighting": lighting_result,
            "clarity": clarity_result
        })
    
    # Step 4: Check face detection 
    face_result = detect_face(image)
    if face_result["status"] != SUCCESS:
        return _build_result(False, face_result["status"], {
            "lighting": lighting_result,
            "clarity": clarity_result,
            "face": face_result
        })
    
    # All checks passed - image is valid
    return _build_result(True, "SUCCESS", {
        "lighting": lighting_result,
        "clarity": clarity_result,
        "face": face_result
    })


# ── Helper: Build result dictionary ──────────────────────────
def _build_result(valid, reason, details=None):
    """Build standardized result dictionary"""
    return {
        "valid": valid,
        "reason": reason,
        "message": ERROR_CODES.get(reason, "Unknown error"),
        "details": details or {}
    }


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
    
    print("\n" + "─" * 50)
    print(f"  Image Verification Result")
    print("─" * 50)
    print(f"  File   : {image_path}")
    print(f"  Valid  : {result['valid']}")
    print(f"  Reason : {result['reason']}")
    print(f"  Message: {result['message']}")
    print("─" * 50 + "\n")
    
    # Exit with appropriate code (0 = success, 1 = failure)
    sys.exit(0 if result["valid"] else 1)