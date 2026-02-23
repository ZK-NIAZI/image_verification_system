# ─────────────────────────────────────────────────────────────
# tests/test_edge_cases.py
# AI Image Verification System — Day 6
#
# Edge case testing to identify false positives/negatives
# and stress test the verification pipeline.
#
# HOW TO RUN:
#   python tests/test_edge_cases.py
# ─────────────────────────────────────────────────────────────

import sys
import os
import json
from datetime import datetime

# Allow imports from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verifier import verify


# ── Colours for terminal output ───────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
MAGENTA = "\033[95m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


# ── Edge Case Test Configuration ──────────────────────────────
EDGE_CASES = {
    "side_profiles": {
        "description": "Side/profile views - should detect NO_FACE",
        "path": "assets/edge_cases/side_profile",
        "expected": ["NO_FACE", "MULTIPLE_FACES"],  # Either is acceptable
        "should_pass": False
    },
    "accessories": {
        "description": "Glasses, masks, hats - should mostly PASS",
        "path": "assets/edge_cases/accessories",
        "expected": ["SUCCESS"],
        "should_pass": True,
        "notes": "Sunglasses/masks might fail - this is acceptable"
    },
    "backgrounds": {
        "description": "Complex/cluttered backgrounds - should PASS if one clear face",
        "path": "assets/edge_cases/backgrounds",
        "expected": ["SUCCESS"],
        "should_pass": True,
        "notes": "May detect MULTIPLE_FACES if posters/photos in background"
    },
    "occlusion": {
        "description": "Partially hidden faces - mixed results expected",
        "path": "assets/edge_cases/occlusion",
        "expected": ["NO_FACE", "SUCCESS"],  # Depends on occlusion amount
        "should_pass": None,  # No clear expectation
        "notes": "Results vary based on how much face is visible"
    },
    "lighting_edge": {
        "description": "Extreme lighting conditions - should catch with lighting check",
        "path": "assets/edge_cases/lighting",
        "expected": ["TOO_DARK", "TOO_BRIGHT", "SUCCESS"],
        "should_pass": None,
        "notes": "Half-shadow might pass or fail depending on overall brightness"
    }
}


# ── Results Storage ───────────────────────────────────────────
test_results = {
    "timestamp": datetime.now().isoformat(),
    "categories": {},
    "summary": {
        "total_images": 0,
        "correct": 0,
        "false_positives": 0,
        "false_negatives": 0,
        "skipped": 0
    }
}


# ── Helper: Check if directory exists ─────────────────────────
def check_directory(path):
    """Check if directory exists and has images"""
    if not os.path.exists(path):
        return False, 0
    
    image_files = [f for f in os.listdir(path) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return True, len(image_files)


# ── Helper: Determine if result is correct ────────────────────
def is_correct_result(result, expected_codes, should_pass):
    """
    Determine if the verification result is correct.
    
    Returns: (is_correct, issue_type)
        is_correct: True/False
        issue_type: None / 'false_positive' / 'false_negative'
    """
    actual_code = result["reason"]
    actual_valid = result["valid"]
    
    # If no clear expectation (mixed results category)
    if should_pass is None:
        return True, None
    
    # If should pass (valid image)
    if should_pass:
        if actual_valid:
            return True, None
        else:
            return False, "false_negative"  # Should pass but didn't
    
    # If should fail (invalid image)
    else:
        if not actual_valid:
            # Check if failure reason is expected
            if actual_code in expected_codes:
                return True, None
            else:
                # Failed but with unexpected reason
                return False, "unexpected_failure"
        else:
            return False, "false_positive"  # Should fail but passed


# ── Helper: Print category header ─────────────────────────────
def print_category_header(category_name, description):
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}  {category_name.upper().replace('_', ' ')}{RESET}")
    print(f"  {description}")
    print(f"{BOLD}{'='*80}{RESET}\n")


# ── Helper: Print test result ─────────────────────────────────
def print_test_result(filename, result, is_correct, issue_type, expected_codes):
    """Print formatted test result"""
    
    valid_text = f"{GREEN}VALID{RESET}" if result["valid"] else f"{RED}INVALID{RESET}"
    reason = result["reason"]
    
    # Determine icon
    if is_correct:
        icon = f"{GREEN}✓{RESET}"
        status = "CORRECT"
    elif issue_type == "false_positive":
        icon = f"{RED}✗ FP{RESET}"  # False Positive
        status = f"{RED}FALSE POSITIVE{RESET}"
    elif issue_type == "false_negative":
        icon = f"{RED}✗ FN{RESET}"  # False Negative
        status = f"{RED}FALSE NEGATIVE{RESET}"
    elif issue_type == "unexpected_failure":
        icon = f"{YELLOW}⚠{RESET}"
        status = f"{YELLOW}UNEXPECTED{RESET}"
    else:
        icon = f"{CYAN}?{RESET}"
        status = "UNKNOWN"
    
    expected_text = "/".join(expected_codes) if len(expected_codes) > 1 else expected_codes[0]
    
    print(f"  {icon}  {filename:<35} {valid_text:<20} {reason:<20} {status}")
    if not is_correct:
        print(f"       {YELLOW}Expected: {expected_text}{RESET}")
    
    return is_correct, issue_type


# ── Test Single Category ──────────────────────────────────────
def test_category(category_key, config):
    """Test all images in a category"""
    
    print_category_header(category_key, config["description"])
    
    path = config["path"]
    expected_codes = config["expected"]
    should_pass = config["should_pass"]
    
    # Check if directory exists
    exists, image_count = check_directory(path)
    
    if not exists:
        print(f"  {YELLOW}⚠  Directory not found: {path}{RESET}")
        print(f"     Create this directory and add test images.\n")
        return None
    
    if image_count == 0:
        print(f"  {YELLOW}⚠  No images found in: {path}{RESET}")
        print(f"     Add test images to this directory.\n")
        return None
    
    # Get all images
    image_files = sorted([f for f in os.listdir(path) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    # Test each image
    results = []
    correct_count = 0
    false_positive_count = 0
    false_negative_count = 0
    
    for img_file in image_files:
        img_path = os.path.join(path, img_file)
        result = verify(img_path)
        
        is_correct, issue_type = is_correct_result(result, expected_codes, should_pass)
        print_test_result(img_file, result, is_correct, issue_type, expected_codes)
        
        # Track statistics
        if is_correct:
            correct_count += 1
        elif issue_type == "false_positive":
            false_positive_count += 1
        elif issue_type == "false_negative":
            false_negative_count += 1
        
        # Store detailed result
        results.append({
            "filename": img_file,
            "path": img_path,
            "result": result,
            "is_correct": is_correct,
            "issue_type": issue_type
        })
    
    # Display category summary
    total = len(results)
    incorrect = total - correct_count
    
    print(f"\n  {BOLD}Category Summary:{RESET}")
    print(f"    Total: {total}")
    print(f"    {GREEN}Correct: {correct_count}{RESET}")
    print(f"    {RED}Incorrect: {incorrect}{RESET}")
    if false_positive_count > 0:
        print(f"      • False Positives: {false_positive_count}")
    if false_negative_count > 0:
        print(f"      • False Negatives: {false_negative_count}")
    
    if "notes" in config:
        print(f"\n  {CYAN}Note: {config['notes']}{RESET}")
    
    # Store results
    category_stats = {
        "description": config["description"],
        "total": total,
        "correct": correct_count,
        "false_positives": false_positive_count,
        "false_negatives": false_negative_count,
        "results": results
    }
    
    return category_stats


# ── Generate Report ───────────────────────────────────────────
def generate_report():
    """Generate edge_case_report.json with all results"""
    
    report_path = "docs/edge_case_results.json"
    
    # Create docs directory if it doesn't exist
    os.makedirs("docs", exist_ok=True)
    
    # Write JSON report
    with open(report_path, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n{CYAN}Detailed results saved to: {report_path}{RESET}")


# ── Main Test Runner ──────────────────────────────────────────
if __name__ == "__main__":
    print()
    print(f"{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}  AI Image Verification — Day 6 Edge Case Testing{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")
    
    # Test each category
    for category_key, config in EDGE_CASES.items():
        stats = test_category(category_key, config)
        
        if stats:
            test_results["categories"][category_key] = stats
            
            # Update summary
            test_results["summary"]["total_images"] += stats["total"]
            test_results["summary"]["correct"] += stats["correct"]
            test_results["summary"]["false_positives"] += stats["false_positives"]
            test_results["summary"]["false_negatives"] += stats["false_negatives"]
        else:
            test_results["summary"]["skipped"] += 1
    
    # Display overall summary
    summary = test_results["summary"]
    
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}  Overall Summary{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    if summary["total_images"] > 0:
        accuracy = (summary["correct"] / summary["total_images"]) * 100
        
        print(f"  Total Images Tested: {summary['total_images']}")
        print(f"  {GREEN}Correct: {summary['correct']}{RESET}")
        print(f"  {RED}Incorrect: {summary['false_positives'] + summary['false_negatives']}{RESET}")
        print(f"    • False Positives: {summary['false_positives']}")
        print(f"    • False Negatives: {summary['false_negatives']}")
        print(f"  {CYAN}Accuracy: {accuracy:.1f}%{RESET}")
        
        if summary["skipped"] > 0:
            print(f"  {YELLOW}Categories Skipped: {summary['skipped']}{RESET}")
        
        # Generate detailed report
        generate_report()
        
        # Recommendations
        print(f"\n{BOLD}Recommendations:{RESET}")
        
        if summary["false_negatives"] > 0:
            print(f"  {YELLOW}• False negatives detected - consider lowering thresholds:{RESET}")
            print(f"    - BLUR_THRESHOLD (if clear images rejected as blurry)")
            print(f"    - FACE_DETECTION_CONFIDENCE (if faces not detected)")
            print(f"    - LIGHTING_MIN (if well-lit images rejected as dark)")
        
        if summary["false_positives"] > 0:
            print(f"  {YELLOW}• False positives detected - consider raising thresholds:{RESET}")
            print(f"    - BLUR_THRESHOLD (if blurry images pass)")
            print(f"    - LIGHTING_MAX/MIN (if poorly lit images pass)")
        
        if accuracy >= 90:
            print(f"\n  {GREEN}✓ System performing well on edge cases!{RESET}")
        elif accuracy >= 75:
            print(f"\n  {YELLOW}⚠ System needs some threshold adjustments.{RESET}")
        else:
            print(f"\n  {RED}✗ System struggles with edge cases. Review config.py settings.{RESET}")
    
    else:
        print(f"  {YELLOW}No test images found.{RESET}")
        print(f"\n{CYAN}Setup Instructions:{RESET}")
        print(f"  Create edge case test folders:")
        print(f"    • assets/edge_cases/side_profile/")
        print(f"    • assets/edge_cases/accessories/")
        print(f"    • assets/edge_cases/backgrounds/")
        print(f"    • assets/edge_cases/occlusion/")
        print(f"    • assets/edge_cases/lighting/")
        print(f"\n  Add 3-5 test images to each folder.")
    
    print()