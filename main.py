# main.py
import os
import sys
import time
import logging
import threading
import tkinter as tk
from tkinter import messagebox

# Add the script directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import config
from src.handler import FolderMonitorHandler, BatchProcessor
# Import the new GUI module
from src.gui import FolderMonitorGUI

# Note: We will remove the old file/console handlers in start_media_monitor 
# if we want the GUI to be the *only* output, or keep them for dual logging.
# For now, let's keep dual logging but ensure the GUI handles the stream.

def start_media_monitor():
    """Initialize and start the folder monitor system."""
    
    # 1. Setup Basic Logging (File/Console)
    # Create handlers
    file_handler = logging.FileHandler(config.LOG_FILE)
    console_handler = logging.StreamHandler(sys.stdout) # Use sys.stdout for better control if needed
    
    # Set format
    formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 2. Initialize GUI
    root = tk.Tk()
    gui = FolderMonitorGUI(root)
    
    # Start the GUI window in a separate thread? 
    # No, Tkinter mainloop should be in the main thread usually, 
    # but we need to start the watcher in a background thread so the GUI stays responsive.
    
    # 3. Setup Monitor Logic
    event_handler = FolderMonitorHandler()
    processor = BatchProcessor(event_handler)
    
    # Start the batch processor thread
    processor_thread = threading.Thread(target=processor.run, daemon=True)
    processor_thread.start()
    
    observers = []
    for folder in config.watched_folders:
        # Check if folder exists
        if not os.path.exists(folder):
            logger.warning(f"Watched folder does not exist: {folder}. Please set it via the GUI later.")
            continue
            
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        # We use event_handler from handler.py
        obs = Observer()
        obs.schedule(event_handler, folder, recursive=True)
        obs.start()
        observers.append(obs)
        logger.info(f"Starting to monitor folder: {folder}")

    logger.info("Folder monitor is running. Press Ctrl+C to stop.")

    # 4. Run GUI
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Stopping folder monitor...")
    finally:
        for obs in observers:
            obs.stop()
            obs.join()
        logging.shutdown()

if __name__ == "__main__":
    start_media_monitor()