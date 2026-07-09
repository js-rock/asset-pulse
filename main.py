# NOTES:
# in gui.py, Source + transfers buttons commented out for future uses cases. Re-enable them when needed.
# in config.py, ignored extensions have been commented out for future uses cases. Re-enable them when needed.
# - lines 64 & 65 in handler.py is connected to the ignored extensions and also needed to be commented out.


import os
import sys
import time
import logging
import threading
import tkinter as tk
from tkinter import messagebox


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import config, load_config
from src.handler import FolderMonitorHandler, BatchProcessor
from src.gui import FolderMonitorGUI

# Global variables to control the monitor state
global_observers = []
global_processor = None

def start_media_monitor():
    global global_observers, global_processor

    # 1. Setup Basic Logging
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [] # Clear existing handlers

    # 2. Initialize GUI
    root = tk.Tk()
    gui = FolderMonitorGUI(root)
    
    # 3. Setup Monitor Logic
    event_handler = FolderMonitorHandler()
    event_handler.gui = gui
    global_processor = BatchProcessor(event_handler)
    
    # Start the batch processor thread
    processor_thread = threading.Thread(target=global_processor.run, daemon=True)
    processor_thread.start()

    # 4. Start Initial Observers
    global_observers = setup_observers(event_handler, gui)

    # 5. Run GUI
    try:
        root.mainloop()
    except KeyboardInterrupt:
        gui.append_log("Stopping folder monitor...")
    finally:
        for obs in global_observers:
            obs.stop()
            obs.join()

def setup_observers(event_handler, gui=None):
    """Helper to start observers based on current config.watched_folders"""
    observers = []
    
    # Get the list of folders from the loaded config
    folders_to_watch = config.watched_folders
    
    if not folders_to_watch:
        if gui:
            gui.append_log("No folders configured to watch. Please set a watch folder in the GUI.")
        return observers

    for folder in folders_to_watch:
        # Check if folder exists
        if not os.path.exists(folder):
            if gui:
                gui.append_log(f"Warning: Watched folder does not exist: {folder}")
            continue
            
        from watchdog.observers import Observer
        
        obs = Observer()
        obs.schedule(event_handler, folder, recursive=True)
        obs.start()
        observers.append(obs)
        if gui:
            gui.append_log(f"Starting to monitor folder: {folder}")
            
    return observers

if __name__ == "__main__":
    start_media_monitor()