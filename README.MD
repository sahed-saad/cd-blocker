## 🛡️ CD Blocker

Real-time credit card or sensitive information detection and blurring for live streamers.

### 🚨 The Problem
- Streamers accidentally show credit cards or any sensitive card-related info on stream → identity theft, financial fraud, career damage.

### ✨ Solution
An AI-powered relay app that sits between the streamer and YouTube/Twitch, automatically detecting and blurring those sensitive information in real-time before the video ever reaches the platform, or while they stream.

### 🔧 How It Works
- Gemini detects objects that might be credit cards
- Google Cloud Vision recognizes pattern in those regions
- Pattern matching validates if it's actually sensitive card or related information
- Auto-blur the sensitive area while streaming

### 🚀 Key Features
- ⚡ Real-time processing (< 300ms latency)
- 🎯 Credit card and sensitive info detection with validation (format checks)
- 🎛️ Streamlined and auto blur intensity
- 📺 Works with any streaming platform

### 🛠️ Quick Start
```bash
pip install -r requirements.txt
python app.py
```

If you use Google Cloud Vision, ensure your credentials are configured (for example, `GOOGLE_APPLICATION_CREDENTIALS` pointing to your service account JSON key).

### 🧰 Tech
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

