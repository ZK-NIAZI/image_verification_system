# ─────────────────────────────────────────────────────────────
# tests/test_day3.py
# AI Image Verification System — Day 3 Tests
#
# Tests clarity check with blurry and clear images
#
# HOW TO RUN:
#   python tests/test_day3.py
# ─────────────────────────────────────────────────────────────

import sys
import os

# Allow imports from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from src.clarity_check import check_clarity, CLEAR, TOO_BLURRY, INVALID_IMAGE


# ── Colours for terminal output ───────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


# ── Helper: Print test result ─────────────────────────────────
def print_result(test_name, result, expected_status):
    passed = result["status"] == expected_status
    icon   = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    
    print(f"  {icon}  {test_name}")
    print(f"         Status    : {result['status']}")
    print(f"         Variance  : {result['variance']}")
    print(f"         Threshold : {result['threshold']}")
    print(f"         Expected  : {expected_status}")
    print(f"         Message   : {result['message']}")
    print()
    return passed


# ── Helper: Load image safely ─────────────────────────────────
def load_image(path):
    if not os.path.exists(path):
        print(f"  {YELLOW}⚠  Image not found: {path}{RESET}")
        print(f"     Place a test image at this path and re-run.\n")
        return None
    return cv2.imread(path)


# ── Test 1: Blurry Image ──────────────────────────────────────
def test_blurry_image():
    print(f"{BOLD}Test 1 — Blurry / Out-of-focus image{RESET}")
    image = load_image("assets/blurry_image.jpg")
    if image is None:
        return None
    result = check_clarity(image)
    return print_result("blurry_image.jpg", result, TOO_BLURRY)


# ── Test 2: Clear Image ───────────────────────────────────────
def test_clear_image():
    print(f"{BOLD}Test 2 — Clear and sharp image{RESET}")
    image = load_image("assets/clear_image.jpg")
    if image is None:
        return None
    result = check_clarity(image)
    return print_result("clear_image.jpg", result, CLEAR)


# ── Test 3: Invalid Image ─────────────────────────────────────
def test_invalid_image():
    print(f"{BOLD}Test 3 — Invalid image (None){RESET}")
    result = check_clarity(None)
    return print_result("None input", result, INVALID_IMAGE)


# ── Bonus: Calculate variance for all images in assets/ ───────
def show_all_variances():
    print(f"{BOLD}{'─'*52}{RESET}")
    print(f"{BOLD}  Variance Values for All Test Images{RESET}")
    print(f"{BOLD}{'─'*52}{RESET}\n")
    
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        print(f"  {YELLOW}No assets/ folder found{RESET}\n")
        return
    
    image_files = [f for f in os.listdir(assets_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print(f"  {YELLOW}No images found in assets/{RESET}\n")
        return
    
    print(f"  {'Image':<30} {'Variance':<12} {'Status':<15}")
    print(f"  {'-'*30} {'-'*12} {'-'*15}")
    
    for img_file in sorted(image_files):
        img_path = os.path.join(assets_dir, img_file)
        img = cv2.imread(img_path)
        if img is not None:
            result = check_clarity(img)
            variance = result["variance"]
            status = result["status"]
            
            color = GREEN if status == CLEAR else RED
            print(f"  {img_file:<30} {variance:<12.2f} {color}{status}{RESET}")
    
    print()


# ── Run All Tests ─────────────────────────────────────────────
if __name__ == "__main__":
    print()
    print(f"{BOLD}{'─'*52}{RESET}")
    print(f"{BOLD}  AI Image Verification — Day 3 Clarity Check Tests{RESET}")
    print(f"{BOLD}{'─'*52}{RESET}\n")

    results = [
        test_blurry_image(),
        test_clear_image(),
        test_invalid_image(),
    ]

    # Filter out skipped tests (None = image not found)
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
        print(f"  {YELLOW}  → assets/blurry_image.jpg  (out of focus / motion blur){RESET}")
        print(f"  {YELLOW}  → assets/clear_image.jpg   (sharp, in-focus photo){RESET}\n")
    
    # Show variance values for all images
    show_all_variances()
    
    print(f"  {CYAN}Tip: Use these variance values to fine-tune BLUR_THRESHOLD in config.py{RESET}")
    print(f"  {CYAN}     Current threshold: 30 (adjust if needed based on your images){RESET}\n")