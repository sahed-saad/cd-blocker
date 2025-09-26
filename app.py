"""
🛡️ AI CD Blocker - Main Application
Real-time credit card detection and blurring for live streamers

This is the main entry point that orchestrates:
1. Web interface for streamers
2. Real-time video processing pipeline
3. Google Gemini AI integration for enhanced detection
4. Backend processing for YOLOv8 + OCR + validation
"""

import os
import sys
import time
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, Response
import google.generativeai as genai
from backend.backend import process_frame, detect_credit_card_numbers, luhn_check
import threading
import queue
from typing import Dict, List, Tuple, Optional

# =============================================================================
# 🚀 FLASK APP INITIALIZATION
# =============================================================================

app = Flask(__name__)

# =============================================================================
# 🔧 CONFIGURATION & GEMINI AI SETUP
# =============================================================================

# Google Gemini API configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables")
    print("   Set it with: export GEMINI_API_KEY='your_api_key_here'")
    print("   Or create a .env file with: GEMINI_API_KEY=your_api_key_here")

# Initialize Gemini AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Google Gemini AI initialized successfully")
else:
    gemini_model = None
    print("❌ Google Gemini AI not available - using fallback detection only")

# Processing configuration
PROCESSING_CONFIG = {
    'blur_intensity': 15,  # Gaussian blur kernel size
    'confidence_threshold': 0.3,  # YOLOv8 detection confidence
    'max_processing_time': 0.3,  # 300ms latency target
    'enable_gemini_analysis': True,  # Use Gemini for text analysis
}

# =============================================================================
# 🧠 GOOGLE GEMINI AI INTEGRATION
# =============================================================================

def analyze_text_with_gemini(text: str) -> Dict:
    """
    Use Google Gemini AI to analyze text for credit card information.
    
    Args:
        text: Text extracted from detected regions
        
    Returns:
        Dict containing analysis results and confidence scores
    """
    if not gemini_model:
        return {"error": "Gemini AI not available"}
    
    try:
        prompt = f"""
        Analyze this text for credit card information. Look for:
        1. Credit card numbers (13-19 digits)
        2. Expiry dates (MM/YY or MM/YYYY format)
        3. CVV codes (3-4 digits)
        4. Cardholder names
        5. Any other sensitive financial information
        
        Text to analyze: "{text}"
        
        Respond in JSON format:
        {{
            "has_credit_card": true/false,
            "confidence": 0.0-1.0,
            "detected_elements": {{
                "card_numbers": ["1234-5678-9012-3456"],
                "expiry_dates": ["12/25"],
                "cvv_codes": ["123"],
                "cardholder_names": ["John Doe"]
            }},
            "risk_level": "low/medium/high",
            "recommendation": "blur_region/allow/manual_review"
        }}
        """
        
        response = gemini_model.generate_content(prompt)
        
        # Parse JSON response (basic implementation)
        # In production, use proper JSON parsing with error handling
        result = {
            "has_credit_card": "true" in response.text.lower(),
            "confidence": 0.8,  # Placeholder - extract from actual response
            "detected_elements": {
                "card_numbers": [],
                "expiry_dates": [],
                "cvv_codes": [],
                "cardholder_names": []
            },
            "risk_level": "medium",
            "recommendation": "blur_region"
        }
        
        return result
        
    except Exception as e:
        print(f"❌ Gemini AI analysis failed: {e}")
        return {"error": f"Analysis failed: {str(e)}"}

def extract_text_from_region(frame: np.ndarray, bbox: List[int]) -> str:
    """
    Extract text from a specific region using OCR.
    This is a simplified implementation - in production, use Tesseract or similar.
    
    Args:
        frame: OpenCV image frame
        bbox: Bounding box [x1, y1, x2, y2]
        
    Returns:
        Extracted text string
    """
    x1, y1, x2, y2 = bbox
    
    # Crop the region
    roi = frame[y1:y2, x1:x2]
    
    # Convert to grayscale for better OCR
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to get better text contrast
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # For demo purposes, return placeholder text
    # In production, integrate with Tesseract OCR:
    # import pytesseract
    # text = pytesseract.image_to_string(thresh)
    
    return "Sample extracted text for demo purposes"

# =============================================================================
# 🎯 CREDIT CARD DETECTION & BLURRING
# =============================================================================

def apply_blur_to_regions(frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
    """
    Apply Gaussian blur to detected credit card regions.
    
    Args:
        frame: Original OpenCV frame
        detections: List of detection results with bounding boxes
        
    Returns:
        Frame with blurred regions
    """
    blurred_frame = frame.copy()
    
    for detection in detections:
        bbox = detection['bbox']
        x1, y1, x2, y2 = bbox
        
        # Extract the region
        roi = blurred_frame[y1:y2, x1:x1+(x2-x1)]
        
        # Apply Gaussian blur
        kernel_size = PROCESSING_CONFIG['blur_intensity']
        if kernel_size % 2 == 0:
            kernel_size += 1  # Ensure odd kernel size
        
        blurred_roi = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)
        
        # Replace the region in the frame
        blurred_frame[y1:y2, x1:x2] = blurred_roi
    
    return blurred_frame

def process_video_frame(frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
    """
    Process a single video frame for credit card detection and blurring.
    
    Args:
        frame: OpenCV video frame
        
    Returns:
        Tuple of (processed_frame, detection_info)
    """
    start_time = time.time()
    
    # Convert frame to base64 for backend processing
    _, buffer = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Process with backend (YOLOv8 detection)
    backend_result = process_frame(frame_base64)
    
    if backend_result.get('error'):
        return frame, {"error": backend_result['error']}
    
    detections = backend_result.get('detections', [])
    processed_frame = frame.copy()
    
    # Enhanced analysis with Gemini AI for each detection
    enhanced_detections = []
    
    for detection in detections:
        bbox = detection['bbox']
        
        # Extract text from the region
        extracted_text = extract_text_from_region(frame, bbox)
        
        # Use Gemini AI for enhanced analysis
        if PROCESSING_CONFIG['enable_gemini_analysis'] and gemini_model:
            gemini_analysis = analyze_text_with_gemini(extracted_text)
            
            # Only blur if Gemini confirms it's a credit card
            if gemini_analysis.get('has_credit_card', False):
                enhanced_detection = detection.copy()
                enhanced_detection['gemini_analysis'] = gemini_analysis
                enhanced_detections.append(enhanced_detection)
        else:
            # Fallback: use traditional pattern matching
            card_numbers = detect_credit_card_numbers(extracted_text)
            if card_numbers:
                enhanced_detection = detection.copy()
                enhanced_detection['detected_cards'] = card_numbers
                enhanced_detections.append(enhanced_detection)
    
    # Apply blur to confirmed credit card regions
    if enhanced_detections:
        processed_frame = apply_blur_to_regions(processed_frame, enhanced_detections)
    
    processing_time = time.time() - start_time
    
    return processed_frame, {
        "detections": enhanced_detections,
        "processing_time": round(processing_time, 3),
        "total_detections": len(enhanced_detections),
        "meets_latency_target": processing_time < PROCESSING_CONFIG['max_processing_time']
    }

# =============================================================================
# 🌐 FLASK ROUTES
# =============================================================================

@app.route('/')
def index():
    """Main dashboard page for streamers."""
    return render_template('index.html', 
                         gemini_available=gemini_model is not None,
                         config=PROCESSING_CONFIG)

@app.route('/api/process_frame', methods=['POST'])
def api_process_frame():
    """
    API endpoint for processing individual frames.
    Accepts base64-encoded images and returns processed results.
    """
    try:
        data = request.get_json()
        base64_image = data.get('image')
        
        if not base64_image:
            return jsonify({"error": "No image data provided"}), 400
        
        # Decode base64 to OpenCV frame
        image_data = base64.b64decode(base64_image)
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid image data"}), 400
        
        # Process the frame
        processed_frame, detection_info = process_video_frame(frame)
        
        # Encode processed frame back to base64
        _, buffer = cv2.imencode('.jpg', processed_frame)
        processed_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "status": "success",
            "processed_image": processed_base64,
            "detection_info": detection_info
        })
        
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API endpoint for managing processing configuration."""
    if request.method == 'GET':
        return jsonify(PROCESSING_CONFIG)
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Update configuration
        for key, value in data.items():
            if key in PROCESSING_CONFIG:
                PROCESSING_CONFIG[key] = value
        
        return jsonify({"status": "success", "config": PROCESSING_CONFIG})

@app.route('/api/health')
def api_health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "gemini_available": gemini_model is not None,
        "backend_loaded": True,
        "timestamp": time.time()
    })

# =============================================================================
# 🎥 VIDEO STREAMING (Optional - for real-time processing)
# =============================================================================

def generate_frames():
    """
    Generator function for video streaming.
    This would integrate with your camera/streaming setup.
    """
    # Placeholder for camera integration
    # In production, connect to your camera source
    cap = cv2.VideoCapture(0)  # Use webcam for demo
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Process frame
        processed_frame, _ = process_video_frame(frame)
        
        # Encode frame for streaming
        _, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route for real-time processing."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# =============================================================================
# 🚀 MAIN APPLICATION ENTRY POINT
# =============================================================================

def main() -> int:
    """
    Main application entry point.
    Initializes the Flask app and starts the server.
    """
    print("🛡️  AI CD Blocker - Starting up...")
    print("=" * 50)
    
    # Check dependencies
    if not GEMINI_API_KEY:
        print("⚠️  Running without Google Gemini AI (fallback mode)")
    else:
        print("✅ Google Gemini AI configured")
    
    print("✅ Backend modules loaded")
    print("✅ Flask app initialized")
    print("=" * 50)
    print("🌐 Starting web server...")
    print("📱 Dashboard: http://localhost:5000")
    print("🔧 API Health: http://localhost:5000/api/health")
    print("🎥 Video Feed: http://localhost:5000/video_feed")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    
    try:
        # Start Flask development server
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())