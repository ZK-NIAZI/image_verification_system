# ─────────────────────────────────────────────────────────────
# app.py
# AI Image Verification System — FastAPI Application
#
# REST API that wraps the CV verification pipeline.
# Endpoints:
#   POST /verify  — Upload an image for verification
#   GET  /health  — Health check
#
# Run:
#   uvicorn app:app --reload --port 8000
# ─────────────────────────────────────────────────────────────

import os
import tempfile
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from verifier import verify


# ── Constants ─────────────────────────────────────────────────
API_VERSION = "1.0.0"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


# ── FastAPI App ───────────────────────────────────────────────
app = FastAPI(
    title="AI Image Verification API",
    description=(
        "Upload a photo and verify it meets quality standards: "
        "good lighting, clarity, and exactly one face detected."
    ),
    version=API_VERSION,
)


# ── POST /verify ──────────────────────────────────────────────
@app.post("/verify")
async def verify_image(file: UploadFile = File(...)):
    """
    Upload an image file for verification.

    The pipeline checks (in order, short-circuits on first failure):
      1. Lighting (too dark / too bright)
      2. Clarity  (too blurry)
      3. Face detection (no face / multiple faces)

    Returns a structured JSON response with the verification result.
    """

    # ── Step 1: Validate file extension ───────────────────────
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": (
                        f"File type '{ext or 'unknown'}' is not supported. "
                        "Only JPEG and PNG image files are accepted."
                    ),
                },
            },
        )

    # ── Step 2: Validate content type ─────────────────────────
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": (
                        f"Content type '{file.content_type}' is not supported. "
                        "Only JPEG and PNG image files are accepted."
                    ),
                },
            },
        )

    # ── Step 3: Read file and check size ──────────────────────
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=413,
            content={
                "success": False,
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": (
                        f"File size ({len(contents) / (1024*1024):.1f} MB) exceeds "
                        f"the maximum allowed size of {MAX_FILE_SIZE // (1024*1024)} MB."
                    ),
                },
            },
        )

    if len(contents) == 0:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": "EMPTY_FILE",
                    "message": "The uploaded file is empty.",
                },
            },
        )

    # ── Step 4: Save to temp file and run verification ────────
    tmp_path = None
    try:
        # Write to a temp file so the verifier can read it with cv2.imread
        suffix = ext if ext else ".jpg"
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        os.close(tmp_fd)

        with open(tmp_path, "wb") as f:
            f.write(contents)

        # Run the verification pipeline
        result = verify(tmp_path)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"An unexpected error occurred: {str(e)}",
                },
            },
        )

    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


# ── GET /health ───────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns the API status and whether the face detection model is loaded.
    """
    # Check model readiness by importing the detector state
    try:
        from src.face_detector import _model_ready
        model_loaded = _model_ready
    except ImportError:
        model_loaded = False

    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "version": API_VERSION,
    }


# ── Run directly with: python app.py ─────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
