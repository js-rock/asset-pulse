# AssetPulse: Intelligent File Watcher


**A lightweight Python automation tool for media professionals.**

## Overview

AssetPulse is an event-driven file monitoring utility designed to bridge the gap between high-pressure production environments and automated digital workflows. Built for photographers, videographers, and post-production professionals, it provides real-time visibility into incoming data, ensuring that files are identified and logged as soon as they hit your local storage.

## About This Project
This is a minimal prototype built as part of a larger automation system. 
The current implementation focuses on core file watching functionality and notification systems.

## The Problem
In professional post-production and creative freelancing, manual file auditing is a significant source of friction. Whether you are managing camera rushes or raw photography assets, tracking file ingestion is prone to human error. AssetPulse automates this "watcher" layer, ensuring every incoming asset is acknowledged immediately upon arrival.

## Key Features
**Recursive Monitoring:** Detects new files within a specified root directory and all its subfolders.

**Real-time Alerts:** Triggered notifications via desktop pop-ups the moment a new file is detected.

**Media-Agnostic:** Designed to handle diverse file types typical in high-end media workflows (CAMERARAW, ProRES, MXF, DNG, JPEG, etc.).

**Modular Architecture:** Built with clean, extensible Python logic, ready to integrate with downstream processing pipelines.

## Tech Stack
**Language:** Python 3.x

**Core Logic:** [Insert Library, e.g., watchdog or os/pathlib]

**UI/Interface: [e.g., tkinter or flet]**

## Roadmap (Next Steps)
As this project evolves toward a fully automated ingest solution, the following features are in active development:

Automated Thumbnail Generation: Auto-generate proxy previews for visual archival.

Cloud Sync Integration: Triggered uploads to remote storage upon detection.

Metadata Extraction: Automated logging of file EXIF/Media data to a CSV/JSON manifest.

## Usage
Clone the repo: git clone https://github.com/js-rock/asset-pulse.git

Install dependencies: pip install -r requirements.txt

Run the watcher: python main.py --path /your/media/directory

# Why This Matters
AssetPulse is the foundation of my shift from Post-Production Supervisor to AI Engineer. It demonstrates my ability to take a manual, high-friction production problem and solve it through clean, scalable software architecture.