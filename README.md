# AssetPulse: Intelligent File Watcher

**A lightweight Python automation tool for media professionals.**

## Overview

AssetPulse is a high-performance, event-driven file monitoring utility designed for post-production environments. It bridges the gap between manual file ingestion and automated digital workflows by providing real-time, batch-processed logging of incoming media assets.

## About This Project

AssetPulse serves as the foundational "ingest engine" for a larger automation system. This MVP focuses on robust file detection and organized logging, ensuring that no asset is lost during the transfer process.

## The Problem

In professional post-production, manually auditing large batches of camera rushes or raw photos is prone to human error and time-consuming. AssetPulse automates the "watcher" layer, ensuring every incoming asset is identified, timestamped, and logged immediately upon arrival.

## Key Features (MVP)

- **Debounced Batch Processing:** Groups rapid file changes into single logical events to prevent log spam and ensure transfers are complete before processing.
- **Recursive Monitoring:** Detects new files within a specified root directory and all its subfolders in real-time.
- **Detailed Logging:** Maintains a rotating log file (`folder_monitor.log`) with precise timestamps and file statistics (size, path, type).
- **Media Classification:** Automatically categorizes files into Images, Videos, or Audio for easier filtering.
- **Modular Architecture:** Built with clean, extensible Python logic (Separation of Concerns), ready to integrate with downstream processing pipelines.

## Tech Stack

- **Language:** Python 3.8+
- **Core Logic:** `watchdog` (File system events), `pathlib` (Path handling)
- **Concurrency:** `threading` (Non-blocking file processing)

## Installation & Usage

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
   Edit `config.py` to set your `watched_folders` and debounce timing.

4. **Run the watcher:**
   ```bash
   python main.py
   ```
   *Logs are written to `folder_monitor.log` in the root directory.*

## Roadmap (Next Steps)

As this project evolves toward a fully automated ingest solution, the following features are planned:

- [ ] **Desktop Notifications:** Native OS pop-ups for immediate awareness.
- [ ] **Webhook Integration:** Send alerts to Slack/Discord/Telegram.
- [ ] **Metadata Extraction:** Automated logging of file EXIF/Media data to a CSV/JSON manifest.
- [ ] **CLI Arguments:** Dynamic folder selection via command line (`--path`).

## Why This Matters

AssetPulse represents my transition from Post-Production Supervisor to AI Engineer. It demonstrates my ability to take a manual, high-friction production problem and solve it through clean, scalable software architecture, event-driven design, and modular Python engineering.