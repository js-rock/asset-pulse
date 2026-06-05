"""
Main entry point for Folder Monitor.
"""

import os
import sys
import time
import logging
import threading
from logging.handlers import RotatingFileHandler

# Add the script directory to path to ensure imports work regardless of CWD
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from handler import FolderMonitorHandler, BatchProcessor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def setup_logging():
    """Configure logging with rotation."""
    # Create handlers
    file_handler = RotatingFileHandler(
        filename=config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT
    )
    console_handler = logging.StreamHandler()

    # Set format
    formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def monitor_folder(folder_path: str, handler: FolderMonitorHandler):
    """Start monitoring a specific folder."""
    if not os.path.exists(folder_path):
        logging.error(f"Folder does not exist: {folder_path}")
        return

    logging.info(f"Starting to monitor folder: {folder_path}")

    observer = Observer()
    observer.schedule(handler, folder_path, recursive=True)
    observer.start()

    return observer


def start_media_monitor():
    """Initialize and start the folder monitor system."""
    logger = setup_logging()
    
    # Create handler and processor
    event_handler = FolderMonitorHandler()
    processor = BatchProcessor(event_handler)
    
    # Start the batch processor thread
    processor_thread = threading.Thread(target=processor.run, daemon=True)
    processor_thread.start()
    logging.info("Batch processor thread started.")

    observers = []
    for folder in config.watched_folders:
        obs = monitor_folder(folder, event_handler)
        observers.append(obs)

    try:
        logging.info("Folder monitor is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping folder monitor...")
        for obs in observers:
            obs.stop()
            obs.join()
        logging.info("Folder monitor stopped.")


if __name__ == "__main__":
    start_media_monitor()
