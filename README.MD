## 🛡️ AI CD Blocker

Real-time credit card detection and blurring for live streamers.

### 🚨 The Problem
- Streamers accidentally show credit cards on stream → identity theft, financial fraud, career damage.

### ✨ Solution
An AI-powered relay app that sits between the streamer and YouTube/Twitch, automatically detecting and blurring credit cards in real-time before the video ever reaches the platform.

### 🔧 How It Works
- YOLOv8 detects objects that might be credit cards
- Google Cloud Vision reads text in those regions
- Pattern matching validates if it's actually a credit card number
- Auto-blur the sensitive area before streaming

### 🚀 Key Features
- ⚡ Real-time processing (< 300ms latency)
- 🎯 Credit card number detection with validation (Luhn and format checks)
- 🎛️ Adjustable blur intensity
- 📺 Works with any streaming platform

### 🛠️ Quick Start
```bash
pip install -r requirements.txt
python app.py
```

If you use Google Cloud Vision, ensure your credentials are configured (for example, `GOOGLE_APPLICATION_CREDENTIALS` pointing to your service account JSON key).

### 🧰 Tech
- YOLOv8 (Ultralytics)
- OpenCV
- Google Cloud Vision API

### 📁 Project Structure (initial)
```
.
├─ app.py              # Entry point (stub)
├─ requirements.txt    # Python dependencies
└─ README.md           # You are here
```

### 🎬 Demo
2-minute demo video showing live credit card detection and blurring: https://youtu.be/HuIr3hJLkiU

—

Built for BYTE Hacks 2025 - Innovation & Creative Expression Track

