# ─────────────────────────────────────────────────────────────
# tests/test_day5.py
# AI Image Verification System — Day 5 Tests
#
# End-to-end testing of the complete verification pipeline.
# Tests all scenarios: good images and various failure types.
#
# HOW TO RUN:
#   python tests/test_day5.py
# ─────────────────────────────────────────────────────────────

import sys
import os

# Allow imports from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verifier import verify, ERROR_CODES


# ── Colours for terminal output ───────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


# ── Test Batch Configuration ──────────────────────────────────
TEST_BATCH = {
    # Good images - should all pass
    "good": [
        "assets/test_batch/good_1.jpg",
        "assets/test_batch/good_2.jpg",
        "assets/test_batch/good_3.jpg",
        "assets/test_batch/good_4.jpg",
        "assets/test_batch/good_5.jpg",
    ],
    
    # Bad images - should fail with specific reasons
    "bad": {
        "assets/test_batch/bad_dark.jpg": "TOO_DARK",
        "assets/test_batch/bad_bright.jpg": "TOO_BRIGHT",
        "assets/test_batch/bad_blurry.jpg": "TOO_BLURRY",
        "assets/test_batch/bad_no_face.jpg": "NO_FACE",
        "assets/test_batch/bad_two_faces.jpg": "MULTIPLE_FACES",
    }
}


# ── Helper: Print test result ─────────────────────────────────
def print_test_result(image_path, result, expected_valid, expected_reason=None):
    """Print formatted test result with pass/fail indicator"""
    
    filename = os.path.basename(image_path)
    valid = result["valid"]
    reason = result["reason"]
    
    # Check if test passed
    if expected_valid:
        # Should be valid
        passed = valid is True and reason == "SUCCESS"
    else:
        # Should be invalid with specific reason
        passed = valid is False and (expected_reason is None or reason == expected_reason)
    
    # Format output
    icon = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
    valid_text = f"{GREEN}VALID{RESET}" if valid else f"{RED}INVALID{RESET}"
    
    print(f"  {icon}  {filename:<30} {valid_text:<20} {reason}")
    
    return passed


# ── Helper: Check if file exists ──────────────────────────────
def file_exists(path):
    """Check if file exists, return True/False"""
    return os.path.exists(path)


# ── Test 1: Good Images (Should All Pass) ────────────────────
def test_good_images():
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  Test 1 — Good Images (Expected: All VALID){RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    results = []
    skipped = 0
    
    for image_path in TEST_BATCH["good"]:
        if not file_exists(image_path):
            print(f"  {YELLOW}⚠{RESET}  {os.path.basename(image_path):<30} {YELLOW}SKIPPED (file not found){RESET}")
            skipped += 1
            continue
        
        result = verify(image_path)
        passed = print_test_result(image_path, result, expected_valid=True)
        results.append(passed)
    
    return results, skipped


# ── Test 2: Bad Images (Should All Fail) ──────────────────────
def test_bad_images():
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  Test 2 — Bad Images (Expected: All INVALID with specific reasons){RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    results = []
    skipped = 0
    
    for image_path, expected_reason in TEST_BATCH["bad"].items():
        if not file_exists(image_path):
            print(f"  {YELLOW}⚠{RESET}  {os.path.basename(image_path):<30} {YELLOW}SKIPPED (file not found){RESET}")
            skipped += 1
            continue
        
        result = verify(image_path)
        passed = print_test_result(image_path, result, expected_valid=False, expected_reason=expected_reason)
        results.append(passed)
    
    return results, skipped


# ── Test 3: Invalid Image Path ───────────────────────────────
def test_invalid_path():
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  Test 3 — Invalid Image Path{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    result = verify("nonexistent_file.jpg")
    passed = print_test_result("nonexistent_file.jpg", result, expected_valid=False, expected_reason="INVALID_IMAGE")
    
    return [passed], 0


# ── Display Error Codes Reference ─────────────────────────────
def show_error_codes():
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  Error Codes Reference{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    print(f"  {'Code':<20} {'Meaning'}")
    print(f"  {'-'*20} {'-'*45}")
    
    for code, description in ERROR_CODES.items():
        if code == "SUCCESS":
            color = GREEN
        else:
            color = RED
        print(f"  {color}{code:<20}{RESET} {description}")
    
    print()


# ── Display Setup Instructions ────────────────────────────────
def show_setup_instructions():
    print(f"\n{CYAN}{'─'*70}{RESET}")
    print(f"{CYAN}  Setup Instructions{RESET}")
    print(f"{CYAN}{'─'*70}{RESET}\n")
    print(f"  To run complete tests, create a test batch folder:")
    print(f"  {YELLOW}assets/test_batch/{RESET}\n")
    print(f"  Add these images:\n")
    print(f"  {GREEN}Good images (5):{RESET}")
    print(f"    • good_1.jpg to good_5.jpg  (well-lit, clear, one face each)")
    print()
    print(f"  {RED}Bad images (5):{RESET}")
    print(f"    • bad_dark.jpg       (very dark / underexposed)")
    print(f"    • bad_bright.jpg     (overexposed / washed out)")
    print(f"    • bad_blurry.jpg     (out of focus / motion blur)")
    print(f"    • bad_no_face.jpg    (no person in photo)")
    print(f"    • bad_two_faces.jpg  (2 or more people)")
    print()


# ── Main Test Runner ──────────────────────────────────────────
if __name__ == "__main__":
    print()
    print(f"{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  AI Image Verification — Day 5 End-to-End Pipeline Tests{RESET}")
    print(f"{BOLD}{'='*70}{RESET}")
    
    # Run all tests
    good_results, good_skipped = test_good_images()
    bad_results, bad_skipped = test_bad_images()
    invalid_results, invalid_skipped = test_invalid_path()
    
    # Combine results
    all_results = good_results + bad_results + invalid_results
    total_skipped = good_skipped + bad_skipped + invalid_skipped
    
    # Calculate stats
    total_ran = len(all_results)
    total_passed = sum(all_results)
    total_failed = total_ran - total_passed
    
    # Display summary
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  Test Summary{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")
    print(f"  {GREEN}✓ Passed:{RESET}  {total_passed}")
    print(f"  {RED}✗ Failed:{RESET}  {total_failed}")
    print(f"  {YELLOW}⚠ Skipped:{RESET} {total_skipped}")
    print(f"  {BLUE}Total:{RESET}    {total_ran + total_skipped}")
    print()
    
    # Show error codes reference
    show_error_codes()
    
    # Show setup instructions if images are missing
    if total_skipped > 0:
        show_setup_instructions()
    
    # Final status
    if total_failed == 0 and total_skipped == 0:
        print(f"  {GREEN}{BOLD}✓ ALL TESTS PASSED{RESET}")
        print(f"  {GREEN}The verification pipeline is working correctly!{RESET}\n")
    elif total_failed == 0 and total_skipped > 0:
        print(f"  {YELLOW}{BOLD}⚠ TESTS PASSED (but some skipped){RESET}")
        print(f"  {YELLOW}Add missing test images to run complete test suite.{RESET}\n")
    else:
        print(f"  {RED}{BOLD}✗ SOME TESTS FAILED{RESET}")
        print(f"  {RED}Review the failures above and adjust thresholds if needed.{RESET}\n")