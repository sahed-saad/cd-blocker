#!/usr/bin/env python3
"""
WebSocket Streaming Credit Card Detector Backend
Streams camera feed with real-time credit card detection to frontend
"""

import asyncio
import websockets
import json
import cv2
import base64
import threading
import time
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingCreditCardDetector:
    def __init__(self, api_key: str):
        """Initialize the streaming credit card detector"""
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
        self.card_detected = False
        self.blur_intensity = 51
        
        # Threading and WebSocket
        self.detection_thread = None
        self.streaming_thread = None
        self.frame_lock = threading.Lock()
        self.current_frame = None
        self.connected_clients = set()
        self.event_loop = None  # Store the main event loop
        
        # Streaming settings
        self.stream_fps = 15  # Reduced FPS for better performance
        self.frame_quality = 60  # JPEG quality (0-100)

    def setup_gemini(self):
        """Configure Gemini AI with API key"""
        try:
            genai.configure(api_key=self.api_key)
            logger.info("✅ API key configured")
            
            model_attempts = [
                "models/gemini-2.5-flash-lite",
                "models/gemini-flash-latest",
                "models/gemini-flash-lite-latest",
                "models/gemini-pro-latest",
            ]
            
            for model_name in model_attempts:
                try:
                    logger.info(f"🔄 Testing model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Test the model with a simple request
                    test_response = self.model.generate_content("Say 'test'")
                    if test_response and test_response.text:
                        logger.info(f"✅ Using working model: {model_name}")
                        break
                        
                except Exception as e:
                    logger.warning(f"   ❌ {model_name}: Failed - {e}")
                    continue
            
            if self.model is None:
                raise Exception("No working Gemini models found!")
                
        except Exception as e:
            logger.error(f"❌ Gemini setup error: {e}")
            raise

    def start_camera(self, camera_index: int = 0) -> bool:
        """Initialize camera"""
        try:
            self.cap = cv2.VideoCapture(1)
            if not self.cap.isOpened():
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info("📹 Camera started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Camera error: {e}")
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
            
            if response and hasattr(response, 'text') and response.text:
                response_text = response.text.strip()
                
                # Clean the response to extract JSON
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0]
                elif '```' in response_text:
                    response_text = response_text.split('```')[1].split('```')[0]
                
                response_text = response_text.strip()
                
                # Try to parse JSON
                try:
                    result = json.loads(response_text)
                    return result.get('detected', False)
                except json.JSONDecodeError:
                    # Try to find JSON manually
                    if '"detected": true' in response_text.lower():
                        return True
                    elif '"detected": false' in response_text.lower():
                        return False
                    else:
                        logger.warning(f"⚠️  Couldn't parse response: {response_text}")
                        return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Gemini detection error: {e}")
            return False

    def blur_entire_screen(self, frame):
        """Apply blur to the entire frame"""
        blurred_frame = cv2.GaussianBlur(frame, (self.blur_intensity, self.blur_intensity), 0)
        
        # Add warning overlay
        overlay = blurred_frame.copy()
        
        # Semi-transparent red overlay
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
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
        cv2.rectangle(blurred_frame, (text_x - 20, text_y - 40), 
                     (text_x + text_size[0] + 20, text_y + 10), (0, 0, 0), -1)
        
        # Warning text
        cv2.putText(blurred_frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
        
        # Shield icon (simple)
        shield_center = (frame.shape[1] // 2, text_y - 80)
        cv2.circle(blurred_frame, shield_center, 30, (255, 255, 255), -1)
        cv2.circle(blurred_frame, shield_center, 25, (0, 0, 255), -1)
        cv2.putText(blurred_frame, "!", shield_center, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        return blurred_frame

    def detection_worker(self):
        """Background thread that checks for cards every 6 seconds"""
        while self.is_running:
            current_time = time.time()
            
            # Reset daily counter every 24 hours
            if current_time - self.daily_reset_time > 86400:
                self.request_count = 0
                self.daily_reset_time = current_time
                logger.info("🔄 Daily request counter reset")
            
            # Check daily limit
            if self.request_count >= self.max_daily_requests:
                logger.warning(f"⚠️  Daily limit reached ({self.max_daily_requests}). Detection paused.")
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
                
                logger.info(f"🔍 Checking for cards... (Request {self.request_count + 1}/{self.max_daily_requests})")
                
                # Run detection
                cards_found = self.detect_cards_with_gemini(frame_to_check)
                self.request_count += 1
                
                # Update screen blur state
                if cards_found:
                    if not self.card_detected:
                        logger.info("🚨 CARD DETECTED! Blurring entire screen...")
                    self.card_detected = True
                else:
                    if self.card_detected:
                        logger.info("✅ No cards detected. Screen unblurred.")
                    self.card_detected = False
                
                self.last_detection_time = current_time
                
                # Send detection status to all connected clients
                if self.event_loop and self.event_loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast_detection_status(),
                        self.event_loop
                    )
            
            time.sleep(0.1)

    async def broadcast_detection_status(self):
        """Send detection status to all connected clients"""
        if not self.connected_clients:
            return
        
        status_message = {
            "type": "detection_status",
            "card_detected": self.card_detected,
            "request_count": self.request_count,
            "max_requests": self.max_daily_requests,
            "next_check": max(0, int(self.detection_interval - (time.time() - self.last_detection_time))),
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all connected clients
        disconnected_clients = set()
        for client in self.connected_clients:
            try:
                await client.send(json.dumps(status_message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.connected_clients -= disconnected_clients

    def frame_to_base64(self, frame):
        """Convert OpenCV frame to base64 encoded JPEG"""
        try:
            # Encode frame to JPEG
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.frame_quality]
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            
            # Convert to base64
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64
        except Exception as e:
            logger.error(f"Error encoding frame: {e}")
            return None

    async def handle_client(self, websocket):
        """Handle individual WebSocket client connection"""
        logger.info(f"New client connected: {websocket.remote_address}")
        self.connected_clients.add(websocket)
        
        try:
            # Send initial connection message
            await websocket.send(json.dumps({
                "type": "connection",
                "message": "Connected to Credit Card Detection Stream",
                "timestamp": datetime.now().isoformat()
            }))
            
            # Handle incoming messages from client
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get("type") == "force_check":
                        self.last_detection_time = 0
                        logger.info("🔍 Client requested immediate check...")
                    elif data.get("type") == "clear_detection":
                        self.card_detected = False
                        logger.info("🔄 Client cleared detection - screen unblurred")
                        await self.broadcast_detection_status()
                    elif data.get("type") == "get_status":
                        await websocket.send(json.dumps({
                            "type": "detection_status",
                            "card_detected": self.card_detected,
                            "request_count": self.request_count,
                            "max_requests": self.max_daily_requests,
                            "next_check": max(0, int(self.detection_interval - (time.time() - self.last_detection_time))),
                            "timestamp": datetime.now().isoformat()
                        }))
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client: {message}")
                except Exception as e:
                    logger.error(f"Error handling client message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {websocket.remote_address}")
        finally:
            self.connected_clients.discard(websocket)

    async def stream_frames(self):
        """Stream video frames to all connected clients"""
        while self.is_running:
            if not self.connected_clients:
                await asyncio.sleep(0.1)
                continue
            
            with self.frame_lock:
                if self.current_frame is None:
                    await asyncio.sleep(0.1)
                    continue
                frame = self.current_frame.copy()
            
            # Apply blur if card detected
            if self.card_detected:
                frame = self.blur_entire_screen(frame)
            
            # Convert frame to base64
            frame_base64 = self.frame_to_base64(frame)
            if frame_base64 is None:
                await asyncio.sleep(1.0 / self.stream_fps)
                continue
            
            # Create frame message
            frame_message = {
                "type": "video_frame",
                "frame": frame_base64,
                "card_detected": self.card_detected,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to all connected clients
            disconnected_clients = set()
            for client in self.connected_clients:
                try:
                    await client.send(json.dumps(frame_message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
                except Exception as e:
                    logger.error(f"Error sending frame to client: {e}")
                    disconnected_clients.add(client)
            
            # Remove disconnected clients
            self.connected_clients -= disconnected_clients
            
            # Control frame rate
            await asyncio.sleep(1.0 / self.stream_fps)

    def camera_worker(self):
        """Camera capture worker thread"""
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                time.sleep(1)
                continue
            
            ret, frame = self.cap.read()
            if not ret:
                logger.error("❌ Camera read failed")
                time.sleep(1)
                continue
            
            with self.frame_lock:
                self.current_frame = frame
            
            time.sleep(1.0 / 30)  # 30 FPS camera capture

    async def start_server(self, host="localhost", port=8765):
        """Start the WebSocket server"""
        logger.info(f"🚀 Starting WebSocket server on ws://{host}:{port}")
        
        # Store the event loop for thread communication
        self.event_loop = asyncio.get_running_loop()
        
        # Start camera
        if not self.start_camera():
            logger.error("Failed to start camera")
            return
        
        self.is_running = True
        
        # Start camera worker thread
        camera_thread = threading.Thread(target=self.camera_worker, daemon=True)
        camera_thread.start()
        
        # Start detection worker thread
        self.detection_thread = threading.Thread(target=self.detection_worker, daemon=True)
        self.detection_thread.start()
        
        # Start frame streaming task
        streaming_task = asyncio.create_task(self.stream_frames())
        
        # Start WebSocket server
        server = await websockets.serve(self.handle_client, host, port)
        
        logger.info("=" * 60)
        logger.info("🛡️  CREDIT CARD DETECTION STREAMING SERVER")
        logger.info("=" * 60)
        logger.info(f"📡 WebSocket Server: ws://{host}:{port}")
        logger.info("🔍 Checks for cards every 6 seconds")
        logger.info("🌫️  Blurs ENTIRE screen when cards detected")
        logger.info("📱 Streaming to connected web clients")
        logger.info("=" * 60)
        
        try:
            await server.wait_closed()
        finally:
            self.cleanup()
            streaming_task.cancel()

    def cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up resources...")
        self.is_running = False
        
        if self.cap:
            self.cap.release()
        
        logger.info("✅ Cleanup completed")


async def main():
    """Main function"""
    # ADD YOUR GEMINI API KEY HERE:
    api_key = "YOUR_API_KEY_HERE"
    
    if api_key == "YOUR_API_KEY_HERE" or not api_key:
        print("❌ Please add your Gemini API key to the code!")
        print('Find this line: api_key = "YOUR_API_KEY_HERE"')
        print("Replace YOUR_API_KEY_HERE with your actual API key")
        return
    
    try:
        detector = StreamingCreditCardDetector(api_key)
        await detector.start_server(host="localhost", port=8765)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("📦 Required: pip install opencv-python google-generativeai pillow numpy websockets")
    print()
    asyncio.run(main())