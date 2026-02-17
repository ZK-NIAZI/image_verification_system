# main.py
# AI Image Verification System — Entry Point
# HOW TO RUN:
#   python main.py assets/one_face.jpg

import sys
import cv2
from src.face_detector import detect_face


def verify_image(image_path):
    print(f"\n  Verifying: {image_path}")
    print("  " + "─" * 40)

    # Load the image
    image = cv2.imread(image_path)

    # Run face detection
    result = detect_face(image)

    # Print result
    status = result["status"]
    if status == "SUCCESS":
        print(f"  ✓  Status  : {result['status']}")
    else:
        print(f"  ✗  Status  : {result['status']}")

    print(f"     Faces   : {result['face_count']}")
    print(f"     Message : {result['message']}")
    print("  " + "─" * 40 + "\n")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n  Usage: python main.py <image_path>")
        print("  Example: python main.py assets/one_face.jpg\n")
        sys.exit(1)

    verify_image(sys.argv[1])