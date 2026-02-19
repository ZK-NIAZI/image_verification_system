# ─────────────────────────────────────────────────────────────
# tests/test_day4.py
# AI Image Verification System
#
# Tests lighting check with dark, normal, and bright images
#
# HOW TO RUN:
#   python tests/test_day4.py
# ─────────────────────────────────────────────────────────────

import sys
import os

# Allow imports from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from src.lighting_check import check_lighting, GOOD_LIGHTING, TOO_DARK, TOO_BRIGHT, INVALID_IMAGE


# ── Colours for terminal output ───────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


# ── Print test result ─────────────────────────────────
def print_result(test_name, result, expected_status):
    passed = result["status"] == expected_status
    icon   = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    
    print(f"  {icon}  {test_name}")
    print(f"         Status         : {result['status']}")
    print(f"         Mean Intensity : {result['mean_intensity']}")
    print(f"         Min Threshold  : {result['min_threshold']}")
    print(f"         Max Threshold  : {result['max_threshold']}")
    print(f"         Expected       : {expected_status}")
    print(f"         Message        : {result['message']}")
    print()
    return passed


# ──  Load image safely ─────────────────────────────────
def load_image(path):
    if not os.path.exists(path):
        print(f"  {YELLOW}⚠  Image not found: {path}{RESET}")
        print(f"     Place a test image at this path and re-run.\n")
        return None
    return cv2.imread(path)


# ── Test 1: Dark / Underexposed Image ─────────────────────────
def test_dark_image():
    print(f"{BOLD}Test 1 — Dark / Underexposed image{RESET}")
    image = load_image("assets/dark_image.jpg")
    if image is None:
        return None
    result = check_lighting(image)
    return print_result("dark_image.jpg", result, TOO_DARK)


# ── Test 2: Normal Lighting ───────────────────────────────────
def test_normal_lighting():
    print(f"{BOLD}Test 2 — Normal / Well-lit image{RESET}")
    image = load_image("assets/normal_lighting.jpg")
    if image is None:
        return None
    result = check_lighting(image)
    return print_result("normal_lighting.jpg", result, GOOD_LIGHTING)


# ── Test 3: Bright / Overexposed Image ────────────────────────
def test_bright_image():
    print(f"{BOLD}Test 3 — Bright / Overexposed image{RESET}")
    image = load_image("assets/bright_image.jpg")
    if image is None:
        return None
    result = check_lighting(image)
    return print_result("bright_image.jpg", result, TOO_BRIGHT)


# ── Test 4: Invalid Image ─────────────────────────────────────
def test_invalid_image():
    print(f"{BOLD}Test 4 — Invalid image (None){RESET}")
    result = check_lighting(None)
    return print_result("None input", result, INVALID_IMAGE)


# ── Bonus: Show intensity values for all images ───────────────
def show_all_intensities():
    print(f"{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  Mean Intensity Values for All Test Images{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}\n")
    
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        print(f"  {YELLOW}No assets/ folder found{RESET}\n")
        return
    
    image_files = [f for f in os.listdir(assets_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print(f"  {YELLOW}No images found in assets/{RESET}\n")
        return
    
    print(f"  {'Image':<30} {'Intensity':<12} {'Status':<15}")
    print(f"  {'-'*30} {'-'*12} {'-'*15}")
    
    for img_file in sorted(image_files):
        img_path = os.path.join(assets_dir, img_file)
        img = cv2.imread(img_path)
        if img is not None:
            result = check_lighting(img)
            intensity = result["mean_intensity"]
            status = result["status"]
            
            if status == GOOD_LIGHTING:
                color = GREEN
            elif status == TOO_DARK:
                color = RED
            elif status == TOO_BRIGHT:
                color = YELLOW
            else:
                color = RESET
            
            print(f"  {img_file:<30} {intensity:<12.2f} {color}{status}{RESET}")
    
    print()
    print(f"  {CYAN}Acceptable range: 40 - 200{RESET}")
    print()


# ── Run All Tests ─────────────────────────────────────────────
if __name__ == "__main__":
    print()
    print(f"{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  AI Image Verification — Lighting Check Tests{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}\n")

    results = [
        test_dark_image(),
        test_normal_lighting(),
        test_bright_image(),
        test_invalid_image(),
    ]

    # Filter out skipped tests (None = image not found)
    ran      = [r for r in results if r is not None]
    passed   = sum(ran)
    total    = len(ran)
    skipped  = len(results) - total

    print(f"{BOLD}{'─'*60}{RESET}")
    print(f"  Results: {GREEN}{passed} passed{RESET} / "
          f"{RED}{total - passed} failed{RESET} / "
          f"{YELLOW}{skipped} skipped{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}\n")

    if skipped > 0:
        print(f"  {YELLOW}Tip: Add images to assets/ folder to run skipped tests.{RESET}")
        print(f"  {YELLOW}  → assets/dark_image.jpg       (underexposed / very dark){RESET}")
        print(f"  {YELLOW}  → assets/normal_lighting.jpg  (well-lit photo){RESET}")
        print(f"  {YELLOW}  → assets/bright_image.jpg     (overexposed / washed out){RESET}\n")
    
    # Show intensity values for all images
    show_all_intensities()
    
    print(f"  {CYAN}Tip: If good images are being rejected, adjust LIGHTING_MIN{RESET}")
    print(f"  {CYAN}     and LIGHTING_MAX in config.py based on the values above.{RESET}\n")