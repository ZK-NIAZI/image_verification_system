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
from datetime import datetime, timezone

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from verifier import verify, verify_from_bytes


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
async def verify_image(
    request: Request,
    file: UploadFile = File(...),
    verbose: bool = Query(False, description="Include full details, timing, and stage breakdowns"),
):
    """
    Upload an image file for verification.

    The pipeline checks (in order, short-circuits on first failure):
      1. Lighting (too dark / too bright)
      2. Clarity  (too blurry)
      3. Face detection (no face / multiple faces)

    By default returns a minimal response (success, valid, reason, message).
    Pass ?verbose=true or header X-Verbose: true for full details.
    """

    # Check header as alternative to query param
    if not verbose:
        verbose = request.headers.get("X-Verbose", "").lower() in ("true", "1", "yes")

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

    # ── Step 4: Run verification directly from bytes ──────────
    try:
        result = verify_from_bytes(contents)

        # ── Build response based on verbosity ─────────────────
        if verbose:
            # Full response: everything the pipeline returns
            response_content = {
                "success": True,
                "result": result,
                "inference_time_ms": result.get("inference_time_ms"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            # Minimal response: just the essentials
            response_content = {
                "success": True,
                "valid": result["valid"],
                "reason": result["reason"],
                "message": result["message"],
            }

        return JSONResponse(
            status_code=200,
            content=response_content,
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
