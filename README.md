# ⚡AssetPulse: Intelligent File Watcher

**A lightweight automated watch folder reporting tool for media professionals. Created with Python.**

## 🎯 Why I Made This

AssetPulse represents my transition from Post-Production Supervisor to AI Engineer. It is the baseline 'pulse' of many AI projects moving forward as the watcher, which will demonstrate to solve high-friction production pipline problems and solve it through clean, scalable software architecture, event-driven design, and modular Python engineering.


## 🔍 Overview

AssetPulse is a high-performance, event-driven monitoring utility. Unlike standard watchers that spam logs with every partial write, AssetPulse batches changes, waits for transfer stability, and provides a clear, categorized audit trail of media and sidecar files.

## 🚀 Key Features
- **GUI-Based Management:** Easily set watch folders and monitor incoming traffic via a clean interface.
- **Configurable Batch Processing:** Uses a debounced engine to group rapid file changes into logical events, preventing "partial transfer" spam.
- **Log Maintenance:** Built-in "Clear Log File (.txt)" and "Reveal Log Folder" controls to keep your disk footprint clean and your data accessible.
- **Recursive Monitoring:** Tracks nested folder structures in real-time.
- **Media/Sidecar Classification:** Automatically identifies file types (Video, Photo, or Non-Media) and logs them with relevant file statistics (size, path).
- **Extensible Architecture:** Built with clean Separation of Concerns, ready to serve as the ingestion engine for future automated processing pipelines.

## 🛠️ Tech Stack
- **Language:** Python 3.8+
- **GUI:** `tkinter` (Standard Python interface)
- **Core Logic:** `watchdog` (Event-driven file system monitoring)
- **Concurrency:** `threading` (Non-blocking background processing)

## 💻 Installation & Usage

1. **Clone the repo:**
   ```bash
   git clone https:[https://github.com/js-rock/asset-pulse.git]
   cd asset-pulse

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the watcher:**
   ```bash
   python main.py
   ```
   *Logs are written to `asset_pulse.log` in the root > logs directory.*

## 🗺️ Roadmap (Next Steps)

As this project evolves toward a fully automated ingest solution, the following features are planned:

- [ ] **🔔 Desktop Notifications:** Native OS pop-ups for immediate awareness.
- [ ] **🌐 Webhook Integration:** Send alerts to Slack/Discord/Telegram.
- [ ] **📊 Metadata Extraction:** Automated logging of file EXIF/Media data to a CSV/JSON manifest.
- [ ] **📟 CLI Arguments:** Dynamic folder selection via command line (`--path`).
