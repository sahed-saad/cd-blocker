"""
backend/backend.py

Core backend logic for AI CD Blocker / Unprying Eyes.
Handles:
- Image decoding (from base64 to OpenCV)
- YOLOv8 detection pipeline
- Optional text analysis / credit card pattern detection
- Output formatting for the Flask app
"""

import base64
import cv2
import numpy as np
import re
from ultralytics import YOLO

# ✅ Load YOLOv8 model globally (fast startup time)
# Use 'yolov8n.pt' for speed or replace with custom-trained model
model = YOLO("yolov8n.pt")


# -------------------------------
# 🔎 1. Decode base64 image to OpenCV frame
# -------------------------------
def decode_base64_image(base64_string: str):
    """Convert base64-encoded image to OpenCV frame."""
    try:
        image_data = base64.b64decode(base64_string)
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print("❌ Image decoding failed:", e)
        return None


# -------------------------------
# 🧠 2. Run YOLOv8 object detection
# -------------------------------
def detect_credit_card_regions(frame, conf_threshold=0.3):
    """
    Runs YOLOv8 to find regions likely to contain credit card information.
    Returns bounding boxes with confidence scores.
    """
    results = model(frame, conf=conf_threshold)
    detections = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]

            # Heuristic: Look for regions that *might* contain cards
            if class_name in ["cell phone", "book", "tv", "laptop", "remote"]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])

                detections.append({
                    "class": class_name,
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(conf, 2)
                })

    return detections


# -------------------------------
# 💳 3. Credit card number detection (basic pattern)
# -------------------------------
def detect_credit_card_numbers(text: str):
    """
    Detect potential credit card numbers using regex + Luhn validation.
    Returns a list of detected card numbers.
    """
    # Common credit card regex: 13-19 digits
    potential_cards = re.findall(r"\b(?:\d[ -]*?){13,19}\b", text)
    valid_cards = [card for card in potential_cards if luhn_check(card)]
    return valid_cards


# -------------------------------
# ✅ 4. Luhn algorithm check
# -------------------------------
def luhn_check(card_number: str) -> bool:
    """Validate a credit card number using the Luhn algorithm."""
    digits = [int(d) for d in card_number if d.isdigit()]
    checksum = 0
    double = False

    for d in reversed(digits):
        if double:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
        double = not double

    return checksum % 10 == 0


# -------------------------------
# 🔁 5. Full processing pipeline
# -------------------------------
def process_frame(base64_image: str):
    """
    Main entry point for the backend.
    - Decodes the image
    - Runs YOLOv8 detection
    - Returns structured results (bounding boxes, confidence)
    """
    frame = decode_base64_image(base64_image)
    if frame is None:
        return {"error": "Invalid image data"}

    detections = detect_credit_card_regions(frame)
    return {
        "status": "ok",
        "detections": detections,
        "total_detections": len(detections)
    }
