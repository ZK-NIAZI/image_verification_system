# face_detector.py
# AI Image Verification System
# Uses: MediaPipe Tasks API (works on mediapipe 0.10+)
# Model: blaze_face_short_range.tflite

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core import base_options as base_opts


# ── Error Codes
SUCCESS         = "SUCCESS"
NO_FACE         = "NO_FACE"
MULTIPLE_FACES  = "MULTIPLE_FACES"
INVALID_IMAGE   = "INVALID_IMAGE"
MODEL_NOT_FOUND = "MODEL_NOT_FOUND"


# ── Model Path — update this if your file is in a different location
MODEL_PATH = "models/blaze_face_short_range.tflite"


# ── Load MediaPipe Tasks Face Detector once
def _load_detector():
    import os
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found at '{MODEL_PATH}'. "
            "Download it from: https://storage.googleapis.com/mediapipe-models/"
            "face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
            " and place it inside a 'models/' folder in your project root."
        )

    options = vision.FaceDetectorOptions(
        base_options=base_opts.BaseOptions(
            model_asset_path=MODEL_PATH
        ),
        min_detection_confidence=0.6   # 60% confidence minimum to count as a face
    )
    return vision.FaceDetector.create_from_options(options)


# Load detector at startup
try:
    _detector = _load_detector()
    _model_ready = True
except FileNotFoundError as e:
    print(f"[WARNING] {e}")
    _detector    = None
    _model_ready = False


# ── Main Function
def detect_face(image):
    """
    Takes an image (numpy array from cv2.imread) and checks
    if exactly one face is present.

    Returns a dictionary:
    {
        "status"     : "SUCCESS" / "NO_FACE" / "MULTIPLE_FACES" /
                       "INVALID_IMAGE" / "MODEL_NOT_FOUND",
        "face_count" : number of faces found (int),
        "message"    : plain English explanation (str)
    }
    """

    # Step 1 — Check if model loaded correctly
    if not _model_ready:
        return _result(MODEL_NOT_FOUND, 0,
                       f"Model file missing at '{MODEL_PATH}'. "
                       "Please download blaze_face_short_range.tflite "
                       "and place it in the models/ folder.")

    # Step 2 — Check if image is valid
    if image is None:
        return _result(INVALID_IMAGE, 0,
                       "Image could not be loaded. Check the file path.")

    # Step 3 — Convert BGR (OpenCV) → RGB (MediaPipe needs RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Step 4 — Wrap into MediaPipe Image format
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=image_rgb
    )

    # Step 5 — Run face detection
    detection_result = _detector.detect(mp_image)

    # Step 6 — Count faces found
    face_count = len(detection_result.detections)

    # Step 7 — Validate and return result
    if face_count == 0:
        return _result(NO_FACE, 0,
                       "No face detected. Please upload a clear photo of your face.")

    elif face_count == 1:
        return _result(SUCCESS, 1,
                       "Face verified. Exactly one face detected.")

    else:
        return _result(MULTIPLE_FACES, face_count,
                       f"Multiple faces detected ({face_count}). "
                       "Please upload a photo with only one person.")


# ── Build result dictionary
def _result(status, face_count, message):
    return {
        "status"     : status,
        "face_count" : face_count,
        "message"    : message
    }