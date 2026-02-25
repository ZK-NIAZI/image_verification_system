# ─────────────────────────────────────────────────────────────
# benchmarks/profile_pipeline.py
# Inference-Time Profiler for the Image Verification Pipeline
#
# Runs verify() N times on test assets and reports per-stage
# and total latency statistics (min, p50, p95, max).
#
# Usage:
#   python benchmarks/profile_pipeline.py
#   python benchmarks/profile_pipeline.py --runs 50
# ─────────────────────────────────────────────────────────────

import argparse
import os
import sys
import time
import statistics

# ── Ensure project root is on sys.path ────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import cv2
from verifier import verify, verify_from_bytes


ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# Images that pass all checks (so every stage is exercised)
TEST_IMAGES = [
    "one_face.jpg",
    "normal_lighting.jpg",
]


def profile_verify(image_path):
    """Run verify() and extract its built-in stage timings."""
    t0 = time.perf_counter()
    result = verify(image_path)
    total = (time.perf_counter() - t0) * 1000  # ms

    stage_times = result.get("stage_times_ms", {})
    timings = {
        "load": stage_times.get("load", 0),
        "preprocess": stage_times.get("preprocess", 0),
        "lighting": stage_times.get("lighting", 0),
        "clarity": stage_times.get("clarity", 0),
        "face_detection": stage_times.get("face_detection", 0),
        "total": total,
    }
    pipeline_result = None
    if result.get("details"):
        pipeline_result = {}
        for key in ("lighting", "clarity", "face"):
            if key in result["details"]:
                pipeline_result[key] = result["details"][key].get("status", "N/A")

    return timings, pipeline_result


def profile_verify_from_bytes(image_path):
    """Run verify_from_bytes() and extract its built-in stage timings."""
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    t0 = time.perf_counter()
    result = verify_from_bytes(image_bytes)
    total = (time.perf_counter() - t0) * 1000  # ms

    stage_times = result.get("stage_times_ms", {})
    timings = {
        "load": stage_times.get("load", 0),
        "preprocess": stage_times.get("preprocess", 0),
        "lighting": stage_times.get("lighting", 0),
        "clarity": stage_times.get("clarity", 0),
        "face_detection": stage_times.get("face_detection", 0),
        "total": total,
    }
    pipeline_result = None
    if result.get("details"):
        pipeline_result = {}
        for key in ("lighting", "clarity", "face"):
            if key in result["details"]:
                pipeline_result[key] = result["details"][key].get("status", "N/A")

    return timings, pipeline_result


def percentile(data, p):
    """Return the p-th percentile of data."""
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[f]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def run_benchmark(runs=30, label="BASELINE"):
    """Run the full benchmark suite and print a formatted report."""

    print(f"\n{'=' * 70}")
    print(f"  INFERENCE BENCHMARK -- {label}")
    print(f"  Runs per image: {runs}")
    print(f"{'=' * 70}\n")

    available_images = [
        img for img in TEST_IMAGES
        if os.path.exists(os.path.join(ASSETS_DIR, img))
    ]

    if not available_images:
        print("  ERROR: No test images found in assets/ directory.")
        print("  Expected: one_face.jpg, normal_lighting.jpg")
        return

    all_totals = []

    for img_name in available_images:
        img_path = os.path.join(ASSETS_DIR, img_name)
        file_size = os.path.getsize(img_path) / 1024  # KB
        image = cv2.imread(img_path)
        h, w = image.shape[:2] if image is not None else (0, 0)

        print(f"  Image: {img_name}")
        print(f"  Size:  {file_size:.0f} KB | Resolution: {w}x{h}")
        print(f"  {'-' * 60}")

        stage_timings = {
            "load": [], "preprocess": [], "lighting": [], "clarity": [],
            "face_detection": [], "total": [],
        }

        # Warm-up run (excluded from stats)
        profile_verify(img_path)

        for _ in range(runs):
            timings, result = profile_verify(img_path)
            for stage, val in timings.items():
                stage_timings[stage].append(val)  # already in ms

        # Print per-stage table
        print(f"  {'Stage':<18} {'Min':>8} {'p50':>8} {'p95':>8} {'Max':>8}")
        print(f"  {'-' * 52}")

        for stage in ["load", "preprocess", "lighting", "clarity", "face_detection", "total"]:
            data = stage_timings[stage]
            if not data:
                continue
            mn = min(data)
            p50 = percentile(data, 50)
            p95 = percentile(data, 95)
            mx = max(data)
            marker = " [!]" if stage == "total" and p95 > 500 else ""
            print(
                f"  {stage:<18} {mn:>7.1f}ms {p50:>7.1f}ms "
                f"{p95:>7.1f}ms {mx:>7.1f}ms{marker}"
            )

        all_totals.extend(stage_timings["total"])

        if result:
            print(f"\n  Pipeline result: {result}")
        print()

    # Summary
    if all_totals:
        p50 = percentile(all_totals, 50)
        p95 = percentile(all_totals, 95)
        target_met = "YES" if p95 < 500 else "NO"

        print(f"{'=' * 70}")
        print(f"  SUMMARY ({label})")
        print(f"  {'-' * 60}")
        print(f"  Overall p50:  {p50:>7.1f} ms")
        print(f"  Overall p95:  {p95:>7.1f} ms")
        print(f"  Target <500ms: {target_met}")
        print(f"{'=' * 70}\n")

    return all_totals


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile the verification pipeline")
    parser.add_argument("--runs", type=int, default=30, help="Runs per image (default: 30)")
    parser.add_argument("--label", type=str, default="BASELINE", help="Label for the report")
    args = parser.parse_args()

    run_benchmark(runs=args.runs, label=args.label)
