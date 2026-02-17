# Tests all 3 face detection scenarios:
#   1. No face in image      → expect NO_FACE
#   2. Exactly one face      → expect SUCCESS
#   3. Two or more faces     → expect MULTIPLE_FACES
#
# HOW TO RUN:
#   python tests/test.py

import sys
import os

# Allow imports from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from src.face_detector import detect_face, SUCCESS, NO_FACE, MULTIPLE_FACES


# ── Colours for terminal output
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


# ── Print test result
def print_result(test_name, result, expected_status):
    passed = result["status"] == expected_status
    icon   = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"  {icon}  {test_name}")
    print(f"         Status     : {result['status']}")
    print(f"         Face Count : {result['face_count']}")
    print(f"         Message    : {result['message']}")
    print(f"         Expected   : {expected_status}")
    print()
    return passed


# ── Load image safely
def load_image(path):
    if not os.path.exists(path):
        print(f"  {YELLOW}⚠  Image not found: {path}{RESET}")
        print(f"     Place a test image at this path and re-run.\n")
        return None
    return cv2.imread(path)


# ── Test 1: No Face
def test_no_face():
    print(f"{BOLD}Test 1 — No face in image{RESET}")
    image = load_image("assets/no_face.jpg")
    if image is None:
        return None
    result = detect_face(image)
    return print_result("no_face.jpg", result, NO_FACE)


# ── Test 2: Exactly One Face
def test_one_face():
    print(f"{BOLD}Test 2 — Exactly one face{RESET}")
    image = load_image("assets/one_face.jpg")
    if image is None:
        return None
    result = detect_face(image)
    return print_result("one_face.jpg", result, SUCCESS)


# ── Test 3: Multiple Faces
def test_multiple_faces():
    print(f"{BOLD}Test 3 — Multiple faces{RESET}")
    image = load_image("assets/two_faces.jpg")
    if image is None:
        return None
    result = detect_face(image)
    return print_result("two_faces.jpg", result, MULTIPLE_FACES)


# ── Test 4: Invalid / Missing Image
def test_invalid_image():
    print(f"{BOLD}Test 4 — Invalid image (None){RESET}")
    result = detect_face(None)
    return print_result("None input", result, "INVALID_IMAGE")


# ── Run All Tests
if __name__ == "__main__":
    print()
    print(f"{BOLD}{'─'*52}{RESET}")
    print(f"{BOLD}  AI Image Verification — Face Detection Tests{RESET}")
    print(f"{BOLD}{'─'*52}{RESET}\n")

    results = [
        test_no_face(),
        test_one_face(),
        test_multiple_faces(),
        test_invalid_image(),
    ]

    # Filter out skipped tests
    ran      = [r for r in results if r is not None]
    passed   = sum(ran)
    total    = len(ran)
    skipped  = len(results) - total

    print(f"{BOLD}{'─'*52}{RESET}")
    print(f"  Results: {GREEN}{passed} passed{RESET} / "
          f"{RED}{total - passed} failed{RESET} / "
          f"{YELLOW}{skipped} skipped{RESET}")
    print(f"{BOLD}{'─'*52}{RESET}\n")

    if skipped > 0:
        print(f"  {YELLOW}Tip: Add images to assets/ folder to run skipped tests.{RESET}")
        print(f"  {YELLOW}  → assets/no_face.jpg   (any image with no people){RESET}")
        print(f"  {YELLOW}  → assets/one_face.jpg  (selfie or solo portrait){RESET}")
        print(f"  {YELLOW}  → assets/two_faces.jpg (photo with 2+ people){RESET}\n")