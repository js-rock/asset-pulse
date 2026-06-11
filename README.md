# ⚡AssetPulse: Intelligent File Watcher

**A lightweight automated watch folder reporting tool for media professionals. Created with Python.**

## 🎯 Why I Made This

AssetPulse represents my transition from Post-Production Supervisor to AI Engineer. It is the baseline 'pulse' of many AI projects moving forward as the watcher, which will demonstrate to solve high-friction production pipline problems and solve it through clean, scalable software architecture, event-driven design, and modular Python engineering.


## 🔍 Overview

AssetPulse is a high-performance, event-driven file monitoring utility designed for post-production environments. It bridges the gap between manual file ingestion and automated digital workflows by providing real-time, batch-processed logging of incoming media assets.

## 🏗️ About This Project

AssetPulse serves as the foundational "ingest engine" for a larger automation system. This MVP focuses on robust file detection and organized logging, ensuring that no asset is lost during the transfer process. It specifically addresses the challenges of monitoring large-scale transfers common in film and video production.

## 🛑 The Problem

In professional post-production, manually auditing large batches of camera rushes or raw photos is prone to human error and time-consuming. Standard file watchers often spam logs with every tiny change during a file write (e.g., size updates), creating noise rather than signal. AssetPulse automates the "watcher" layer, ensuring every incoming asset is identified, timestamped, and logged **only after** the transfer is complete.

## 🚀 Key Features (MVP)

- **Configurable Debounced Batch Processing:** Groups rapid file changes into single logical events. By default, it waits for 15 seconds of inactivity before processing, preventing "partial transfer" logs and ensuring files are fully written.
- **Temporary File Filtering:** Automatically ignores temporary files (`.tmp`, `.part`, etc.) generated during transfer, preventing false positives and duplicate entries.
- **Formatted Non-Media Reporting:** Clearly categorizes and groups non-media sidecars (subtitles, notes, logs) by extension in the logs, avoiding jumbled single-line outputs.
- **Recursive Monitoring:** Detects new files within a specified root directory and all its subfolders in real-time.
- **Detailed Logging:** Maintains a rotating log file (`folder_monitor.log`) with precise timestamps, file statistics (size, path, type), and batch summaries.
- **Media Classification:** Automatically categorizes files into Images, Videos, or Audio for easier filtering.
- **Modular Architecture:** Built with clean, extensible Python logic (Separation of Concerns), ready to integrate with downstream processing pipelines.

## 🛠️ Tech Stack

- **Language:** Python 3.8+
- **Core Logic:** `watchdog` (File system events), `pathlib` (Path handling)
- **Concurrency:** `threading` (Non-blocking file processing)

## 💻 Installation & Usage

1. **Clone the repo:**
   ```bash
   git clone https://github.com/js-rock/asset-pulse.git
   cd asset-pulse
   ```

2. **Install dependencies:**
   ```bash
   pip install watchdog
   ```

3. **Configure:**
   Edit `config.py` to set your:
   - `watched_folders`: List of directories to monitor.
   - `DEBOUNCE_DELAY`: Time (in seconds) to wait after the last file change before processing (recommended: 10-15s for large rushes).
   - `TEMP_EXTENSIONS`: List of file extensions to ignore during transfer (default includes `.tmp`, `.part`).

4. **Run the watcher:**
   ```bash
   python main.py
   ```
   *Logs are written to `folder_monitor.log` in the root directory.*

## 🗺️ Roadmap (Next Steps)

As this project evolves toward a fully automated ingest solution, the following features are planned:

- [ ] **🔔 Desktop Notifications:** Native OS pop-ups for immediate awareness.
- [ ] **🌐 Webhook Integration:** Send alerts to Slack/Discord/Telegram.
- [ ] **📊 Metadata Extraction:** Automated logging of file EXIF/Media data to a CSV/JSON manifest.
- [ ] **📟 CLI Arguments:** Dynamic folder selection via command line (`--path`).
