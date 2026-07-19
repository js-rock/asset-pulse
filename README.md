# ⚡AssetPulse: Intelligent File Watcher & Sync Engine

**A lightweight, automated watch folder utility for media professionals. Created with Python.**

## 🎯 Why I Made This

AssetPulse represents my transition from Post-Production Supervisor to AI Engineer. It serves as the baseline 'pulse' for many AI projects moving forward, acting as the ingestion layer that solves high-friction production pipeline problems. 

It demonstrates clean, scalable software architecture through **event-driven design**, **modular Python engineering**, and **state-preserving file synchronization**.

## 🔍 Overview

AssetPulse is a high-performance, event-driven monitoring utility. Unlike standard watchers that spam logs with every partial write, AssetPulse batches changes, waits for transfer stability, and provides two distinct modes of operation:
1.  **Report Mode:** A clear, categorized audit trail of media and sidecar files.
2.  **Sync Mode:** Automated copying of files from a source to a destination while preserving critical metadata (timestamps, permissions).

## 🚀 Key Features
- **🖥️ GUI-Based Management:** Easily set watch folders, define destinations, and monitor incoming traffic via a clean `tkinter` interface.
- **⚙️ Dual-Mode Operation:** 
  - *Watch & Report:* Traditional monitoring for auditing purposes.
  - *Watch & Sync:* Automated duplication of files to backup or processing directories.
- **🧠 Configurable Batch Processing:** Uses a debounced engine to group rapid file changes into logical events, preventing "partial transfer" spam and ensuring data integrity before copying.
- **💾 Metadata Preservation:** When syncing, AssetPulse utilizes `shutil.copy2` to preserve original creation/modification timestamps and permissions, critical for media workflows.
- **📂 Recursive Monitoring:** Tracks nested folder structures in real-time.
- **🏷️ Media/Sidecar Classification:** Automatically identifies file types (Video, Photo, or Non-Media) and logs them with relevant file statistics (size, path).
- **Extensible Architecture:** Built with clean Separation of Concerns (`handler.py`, `copy_engine.py`), ready to serve as the ingestion engine for future automated processing pipelines.

## 🛠️ Tech Stack
- **Language:** Python 3.8+
- **GUI:** `tkinter` (Standard Python interface)
- **Core Logic:** 
  - `watchdog` (Event-driven file system monitoring)
  - `shutil` (Robust file copying with metadata preservation)
- **Concurrency:** `threading` (Non-blocking background processing for both logging and syncing)

## 💻 Installation & Usage

1. **Clone the repo:**
   ```bash
   git clone https://github.com/js-rock/asset-pulse.git
   cd asset-pulse
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the watcher:**
   ```bash
   python main.py
   ```
   
4. **Configuration:**
   * Use the GUI buttons to select your **Source Folder** (to watch) and optionally a **Destination Folder** (for sync mode).
   * Logs are written to `asset_pulse.log` in the root `logs/` directory.

## 🗺️ Roadmap (Next Steps)

As this project evolves toward a fully automated ingest solution, the following features are planned:

- [ ] **🔔 Desktop Notifications:** Native OS pop-ups for immediate awareness of sync completion or errors.
- [ ] **🌐 Webhook Integration:** Send alerts to Slack/Discord/Telegram when specific file types are detected.
- [ ] **📊 Advanced Metadata Extraction:** Automated logging of file EXIF/Media data (resolution, codec, duration) to a CSV/JSON manifest.
- [ ] **📟 CLI Arguments:** Dynamic folder selection via command line (`--source`, `--dest`) for headless server deployments.