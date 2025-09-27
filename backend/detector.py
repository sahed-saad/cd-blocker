#!/usr/bin/env python3
"""
Simple AI Credit Card Detector
Every 6 seconds: Check for cards with Gemini AI
If card detected: Blur entire screen
"""

import cv2
import numpy as np
import google.generativeai as genai
import base64
import json
import time
import threading
from PIL import Image
import io
import os


class SimpleCreditCardDetector:
    def __init__(self, api_key: str):
        """Initialize the simple credit card detector"""
        self.api_key = api_key
        self.model = None
        self.setup_gemini()

        # Camera settings
        self.cap = None
        self.is_running = False

        # Detection settings
        self.detection_interval = 6.0  # Check every 6 seconds
        self.last_detection_time = 0
        self.max_daily_requests = 500
        self.request_count = 0
        self.daily_reset_time = time.time()

        # Screen blur settings
        self.card_detected = False  # True = blur entire screen
        self.blur_intensity = 51

        # Threading
        self.detection_thread = None
        self.frame_lock = threading.Lock()
        self.current_frame = None

    def setup_gemini(self):
        """Configure Gemini AI with API key"""
        try:
            genai.configure(api_key=self.api_key)
            print("✅ API key configured")

            # Try different model names to find one that works
            model_attempts = [
                # "models/gemini-1.5-flash-8b",
                # "gemini-1.5-flash-8b",
                # "gemini-1.5-flash-latest",
                # "gemini-1.5-flash",
                # "gemini-1.5-pro-latest",
                # "gemini-pro-vision",
                ## "models/gemini-2.5-pro",
                # "models/gemini-2.5-flash",
                "models/gemini-2.5-flash-lite",
                "models/gemini-flash-latest",
                "models/gemini-flash-lite-latest",
                "models/gemini-pro-latest",
            ]

            for model_name in model_attempts:
                try:
                    print(f"🔄 Testing model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)

                    # Test the model with a simple request
                    test_response = self.model.generate_content("Say 'test'")
                    if test_response and test_response.text:
                        print(f"✅ Using working model: {model_name}")
                        break

                except Exception as e:
                    print(f"   ❌ {model_name}: Failed")
                    continue

            if self.model is None:
                raise Exception("No working Gemini models found!")

        except Exception as e:
            print(f"❌ Gemini setup error: {e}")
            raise

    def start_camera(self, camera_index: int = 0) -> bool:
        """Initialize camera"""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                return False

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            print("📹 Camera started successfully")
            return True

        except Exception as e:
            print(f"❌ Camera error: {e}")
            return False

    def detect_cards_with_gemini(self, frame) -> bool:
        """Use Gemini to detect if ANY credit cards are present"""
        if self.model is None:
            return False

        try:
            # Convert frame to image for Gemini
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            pil_image = pil_image.resize((640, 480), Image.Resampling.LANCZOS)

            prompt = """Look at this image and determine if there are any credit cards, debit cards, or payment cards visible.

Respond with ONLY this JSON format:
{"detected": true} if you see any payment cards
{"detected": false} if you see no payment cards

Look for:
- Rectangular cards with numbers
- Credit card logos (Visa, Mastercard, Amex, etc.)
- Cards being held or on surfaces
- Any kind of payment card

Just respond with the JSON, nothing else."""

            response = self.model.generate_content([prompt, pil_image])

            if response and hasattr(response, "text") and response.text:
                response_text = response.text.strip()

                # Clean the response to extract JSON
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]

                response_text = response_text.strip()

                # Try to parse JSON
                try:
                    result = json.loads(response_text)
                    return result.get("detected", False)
                except json.JSONDecodeError:
                    # Try to find JSON manually
                    if '"detected": true' in response_text.lower():
                        return True
                    elif '"detected": false' in response_text.lower():
                        return False
                    else:
                        print(f"⚠️  Couldn't parse response: {response_text}")
                        return False

            return False

        except Exception as e:
            print(f"❌ Gemini detection error: {e}")
            return False

    def blur_entire_screen(self, frame):
        """Apply blur to the entire frame"""
        blurred_frame = cv2.GaussianBlur(
            frame, (self.blur_intensity, self.blur_intensity), 0
        )

        # Add warning overlay
        overlay = blurred_frame.copy()

        # Semi-transparent red overlay
        cv2.rectangle(
            overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1
        )
        blurred_frame = cv2.addWeighted(blurred_frame, 0.85, overlay, 0.15, 0)

        # Warning text in center
        text = "PAYMENT CARD DETECTED - SCREEN BLURRED"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 3

        # Get text size for centering
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = (frame.shape[0] + text_size[1]) // 2

        # Text background
        cv2.rectangle(
            blurred_frame,
            (text_x - 20, text_y - 40),
            (text_x + text_size[0] + 20, text_y + 10),
            (0, 0, 0),
            -1,
        )

        # Warning text
        cv2.putText(
            blurred_frame,
            text,
            (text_x, text_y),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
        )

        # Shield icon (simple)
        shield_center = (frame.shape[1] // 2, text_y - 80)
        cv2.circle(blurred_frame, shield_center, 30, (255, 255, 255), -1)
        cv2.circle(blurred_frame, shield_center, 25, (0, 0, 255), -1)
        cv2.putText(
            blurred_frame,
            "!",
            shield_center,
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255, 255, 255),
            3,
        )

        return blurred_frame

    def detection_worker(self):
        """Background thread that checks for cards every 6 seconds"""
        while self.is_running:
            current_time = time.time()

            # Reset daily counter every 24 hours
            if current_time - self.daily_reset_time > 86400:
                self.request_count = 0
                self.daily_reset_time = current_time
                print("🔄 Daily request counter reset")

            # Check daily limit
            if self.request_count >= self.max_daily_requests:
                print(
                    f"⚠️  Daily limit reached ({self.max_daily_requests}). Detection paused."
                )
                time.sleep(60)
                continue

            # Check if it's time for detection
            if current_time - self.last_detection_time >= self.detection_interval:
                with self.frame_lock:
                    if self.current_frame is not None:
                        frame_to_check = self.current_frame.copy()
                    else:
                        time.sleep(0.5)
                        continue

                print(
                    f"🔍 Checking for cards... (Request {self.request_count + 1}/{self.max_daily_requests})"
                )

                # Run detection
                cards_found = self.detect_cards_with_gemini(frame_to_check)
                self.request_count += 1

                # Update screen blur state
                if cards_found:
                    if not self.card_detected:
                        print("🚨 CARD DETECTED! Blurring entire screen...")
                    self.card_detected = True
                else:
                    if self.card_detected:
                        print("✅ No cards detected. Screen unblurred.")
                    self.card_detected = False

                self.last_detection_time = current_time

            time.sleep(0.1)

    def run(self):
        """Main loop"""
        if not self.start_camera():
            return

        if self.model is None:
            print("❌ No AI model available")
            return

        self.is_running = True

        # Start detection thread
        self.detection_thread = threading.Thread(
            target=self.detection_worker, daemon=True
        )
        self.detection_thread.start()

        print("\n" + "=" * 60)
        print("🛡️  SIMPLE PAYMENT CARD SCREEN PROTECTION")
        print("=" * 60)
        print("🔍 Checks for cards every 6 seconds")
        print("🌫️  Blurs ENTIRE screen when cards detected")
        print("📱 Perfect for streaming protection!")
        print("\n⌨️  Controls:")
        print("  • 'q' or ESC: Quit")
        print("  • 'b': Increase blur strength")
        print("  • 'v': Decrease blur strength")
        print("  • 'f': Force check now")
        print("  • 'c': Clear detection (unblur)")
        print("\n🚀 Starting protection...")

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Camera read failed")
                    break

                # Update current frame for detection thread
                with self.frame_lock:
                    self.current_frame = frame.copy()

                # Apply full screen blur if card detected
                if self.card_detected:
                    display_frame = self.blur_entire_screen(frame)
                else:
                    display_frame = frame.copy()

                # Status information
                next_check = max(
                    0,
                    int(
                        self.detection_interval
                        - (time.time() - self.last_detection_time)
                    ),
                )

                status_items = [
                    f"🎯 Card Status: {'DETECTED' if self.card_detected else 'NOT DETECTED'}",
                    f"🤖 API Calls: {self.request_count}/{self.max_daily_requests}",
                    f"⏱️  Next Check: {next_check}s",
                    f"🌫️  Blur Level: {self.blur_intensity}",
                ]

                y_pos = 30
                for item in status_items:
                    # Status background for visibility
                    text_size = cv2.getTextSize(item, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[
                        0
                    ]
                    cv2.rectangle(
                        display_frame,
                        (10, y_pos - 20),
                        (15 + text_size[0], y_pos + 5),
                        (0, 0, 0),
                        -1,
                    )

                    # Status text
                    color = (0, 255, 0) if not self.card_detected else (255, 255, 255)
                    cv2.putText(
                        display_frame,
                        item,
                        (12, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        color,
                        2,
                    )
                    y_pos += 35

                # Main status at bottom
                main_status = (
                    "🛡️  SCREEN PROTECTED" if self.card_detected else "🔍 MONITORING..."
                )
                status_color = (0, 0, 255) if self.card_detected else (0, 255, 0)

                cv2.putText(
                    display_frame,
                    main_status,
                    (10, display_frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    status_color,
                    3,
                )

                cv2.imshow("Simple Card Protection", display_frame)

                # Handle controls
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:  # Quit
                    break
                elif key == ord("b"):  # Increase blur
                    self.blur_intensity = min(self.blur_intensity + 10, 101)
                    if self.blur_intensity % 2 == 0:
                        self.blur_intensity += 1
                    print(f"🔧 Blur strength: {self.blur_intensity}")
                elif key == ord("v"):  # Decrease blur
                    self.blur_intensity = max(self.blur_intensity - 10, 11)
                    if self.blur_intensity % 2 == 0:
                        self.blur_intensity -= 1
                    print(f"🔧 Blur strength: {self.blur_intensity}")
                elif key == ord("f"):  # Force check now
                    self.last_detection_time = 0
                    print("🔍 Forcing immediate check...")
                elif key == ord("c"):  # Clear detection
                    self.card_detected = False
                    print("🔄 Detection cleared - screen unblurred")

        except KeyboardInterrupt:
            print("\n⏹️  Stopping protection...")

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        self.is_running = False

        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=3)

        if self.cap:
            self.cap.release()

        cv2.destroyAllWindows()
        print("🧹 Cleanup completed")


def main():
    """Main function"""
    print("🛡️  SIMPLE CREDIT CARD SCREEN PROTECTION")
    print("=" * 50)
    print("Every 6 seconds → Check for cards → Blur entire screen if found")
    print()

    # ADD YOUR GEMINI API KEY HERE:
    api_key = "AIzaSyDHBqE7rgdWUGpk7o5m-CGAJB6tuIPyck0"

    if api_key == "YOUR_API_KEY_HERE" or not api_key:
        print("❌ Please add your Gemini API key to the code!")
        print('Find this line: api_key = "YOUR_API_KEY_HERE"')
        print("Replace YOUR_API_KEY_HERE with your actual API key")
        return

    try:
        detector = SimpleCreditCardDetector(api_key)
        detector.run()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("📦 Required: pip install opencv-python google-generativeai pillow numpy")
    print()
    main()
