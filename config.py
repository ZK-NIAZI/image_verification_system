# ─────────────────────────────────────────────────────────────
# config.py
# AI Image Verification System — Configuration
#
# All thresholds and settings in one place for easy adjustment
# ─────────────────────────────────────────────────────────────

# ── Blur / Clarity Detection ──────────────────────────────────
# Laplacian variance threshold for blur detection
#
# CRITICAL: Variance measures EDGES, not just blur.
# Different content types have different "normal" variance:
#   - Face photos (smooth skin): 30-80
#   - Landscape/objects (textures): 80-200+
#   - Blurry face photos: 10-30
#
# Since this is a FACE VERIFICATION system, tune threshold for face photos.
#
# How to find the right threshold FOR FACE PHOTOS:
#   1. Take a BLURRY face selfie (out of focus or motion blur)
#   2. Take a CLEAR face selfie (sharp and in focus)
#   3. Run: python tests/test_day3.py
#   4. Check both variances in the output table
#   5. Set threshold BETWEEN the two values
#
# Example face photo variances:
#   Blurry face selfie: 18
#   Clear face selfie: 45
#   Good threshold: 25-30
#
# IMPORTANT: Do NOT test with landscape/object photos.
# They have naturally higher variance and will give wrong results.
#
# Recommended for face verification systems:
BLUR_THRESHOLD = 25  # Tuned for face photos (adjust based on YOUR test images)


# ── Face Detection ────────────────────────────────────────────
# Minimum confidence for MediaPipe face detection (0.0 to 1.0)
FACE_DETECTION_CONFIDENCE = 0.6


# ── Lighting Check (Coming Later) ────────────────────────────
# Mean pixel intensity range for good lighting
LIGHTING_MIN = 40    # Below this = too dark
LIGHTING_MAX = 200   # Above this = too bright/overexposed


# ── Model Paths ───────────────────────────────────────────────
FACE_DETECTOR_MODEL = "models/blaze_face_short_range.tflite"


# ── Image Preprocessing ──────────────────────────────────────
# Cap the largest image dimension before running any checks.
# Smaller images = faster processing at every stage.
# 640px is a good balance between speed and detection accuracy.
MAX_IMAGE_DIMENSION = 640   # pixels (longest side)


# ── API Server Configuration ──────────────────────────────────
# Host and port for the FastAPI server
# Can be overridden with environment variables:
#   HOST=0.0.0.0 python app.py
#   PORT=9000 python app.py
API_HOST = "0.0.0.0"   # Listen on all interfaces
API_PORT = 8000        # Default port
# Base URL for the API (used in docs and external references)
# Override with BASE_URL environment variable:
#   BASE_URL=https://api.example.com python app.py
BASE_URL = "https://aw4g8kwkg8go0kcokgs8k80w.62.171.148.170.sslip.io"

# ── Performance Logging ───────────────────────────────────────
# When True, verify() returns per-stage timing data and the API
# logs inference latency.
PERF_LOGGING_ENABLED = True