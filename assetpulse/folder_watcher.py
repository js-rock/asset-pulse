import os
import time
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

watched_folder = 'F:/_DummyNAS/test_watch'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('folder_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Define media file extensions
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpg', '.mpeg', '.3gp', '.m4v'}
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.raw', '.cr2', '.nef', '.orf', '.sr2'}

class FolderMonitorHandler(FileSystemEventHandler):
    """Handles file system events"""

    def __init__(self):
        self.notified_files = set()  # Initialize notified files set for each instance

    def is_media_file(self, file_path):
        """Check if a file is a video or photo"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in VIDEO_EXTENSIONS or ext in PHOTO_EXTENSIONS

    def get_file_type(self, file_path):
        """Get the type of media file"""
        _, ext = os.path.splitext(file_path.lower())
        if ext in VIDEO_EXTENSIONS:
            return "VIDEO"
        elif ext in PHOTO_EXTENSIONS:
            return "PHOTO"
        return "UNKNOWN"

    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"File Modified: {event.src_path}")
            # Check if the modified file is a media file
            if self.is_media_file(event.src_path):
                file_type = self.get_file_type(event.src_path)
                file_size = os.path.getsize(event.src_path)
                logger.info(f"MODIFIED {file_type}: {event.src_path} (Size: {file_size} bytes)")
                self.show_notification(file_type, event.src_path, file_size)
        else:
            logger.info(f"Folder Modified: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"File Created: {event.src_path}")
            # Check if the created file is a media file
            if self.is_media_file(event.src_path):
                file_type = self.get_file_type(event.src_path)
                file_size = os.path.getsize(event.src_path)
                logger.info(f"NEW {file_type}: {event.src_path} (Size: {file_size} bytes)")
                self.show_notification(file_type, event.src_path, file_size)
        else:
            logger.info(f"Folder Created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File Deleted: {event.src_path}")
        else:
            logger.info(f"Folder Deleted: {event.src_path}")

    def on_moved(self, event):
        if not event.is_directory:
            logger.info(f"File Moved: {event.src_path} -> {event.dest_path}")
            # Check if the moved file is a media file
            if self.is_media_file(event.dest_path):
                file_type = self.get_file_type(event.dest_path)
                file_size = os.path.getsize(event.dest_path)
                logger.info(f"MOVED {file_type}: {event.src_path} -> {event.dest_path} (Size: {file_size} bytes)")
                self.show_notification(file_type, event.dest_path, file_size)
        else:
            logger.info(f"Folder Moved: {event.src_path} -> {event.dest_path}")

    def show_notification(self, file_type, file_path, file_size):
        """Show a simple notification about detected media file"""
        # Prevent duplicate notifications for the same file
        file_key = os.path.abspath(file_path)  # Use absolute path for unique identification
        if file_key in self.notified_files:
            return  # Skip if already notified

        # Mark this file as notified
        self.notified_files.add(file_key)

        # First, always log to console (this should always work)
        console_message = f"NEW {file_type}: {file_path} (Size: {file_size} bytes)"
        print(console_message)
        print(f"Notification: Please decide what to do with this file (ingest, convert, or leave as is)")

        try:
            # Try to use tkinter for GUI notification (if available)
            import tkinter as tk
            from tkinter import messagebox

            # Create a minimal GUI notification
            root = tk.Tk()
            root.withdraw()  # Hide the main window

            # Show notification dialog with action options
            message = f"New {file_type} detected!\n\nFile: {os.path.basename(file_path)}\nSize: {file_size} bytes\nPath: {file_path}\n\nWhat would you like to do?"
            result = messagebox.askquestion("Media File Detected", message + "\n\nChoose an action:",
                                          icon='info', type='yesnocancel',
                                          default='yes')

            # Process the user's choice
            if result == 'yes':
                print("User chose: Ingest")
            elif result == 'no':
                print("User chose: Convert")
            elif result == 'cancel':
                print("User chose: Leave as is")

            root.destroy()
        except ImportError:
            # tkinter not available - this is fine, we already logged to console
            print("GUI notification not available (tkinter not found)")
        except Exception as e:
            # Other GUI errors - log them but continue
            print(f"GUI notification failed: {e}")
            print("Continuing with console notification only")

def monitor_folder(folder_path):
    """Monitor a folder for changes"""
    if not os.path.exists(folder_path):
        logger.error(f"Folder does not exist: {folder_path}")
        return

    logger.info(f"Starting to monitor folder: {folder_path}")

    # Create event handler and observer
    event_handler = FolderMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)

    # Start observer
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping folder monitor...")
        observer.stop()

    observer.join()

def start_media_monitor():
    """Start media monitoring using the watched folder from folder_watcher"""
    monitor_folder(watched_folder)

if __name__ == "__main__":
    # Monitor the folder where this script is located
    folder_to_monitor = watched_folder
    monitor_folder(folder_to_monitor)