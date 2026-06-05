import os
import time
import logging
import threading
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
ALL_MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | PHOTO_EXTENSIONS

# Debounce configuration
DEBOUNCE_DELAY = 2.0  # Wait 2 seconds after the last event before reporting

class FolderMonitorHandler(FileSystemEventHandler):
    """Handles file system events with debouncing to suppress noise from folder drops"""

    def __init__(self):
        self.notified_files = set()
        self.recently_created = {}
        
        # Structure for debouncing: { parent_abs_path: {'timestamp': float, 'items': list} }
        self.pending_batches = {}
        self.lock = threading.Lock()
        self._processed_batches = set() # Track recently processed batches to avoid duplicates

    def is_media_file(self, file_path):
        """Check if a file is a video or photo"""
        if not os.path.isfile(file_path):
            return False
        _, ext = os.path.splitext(file_path.lower())
        return ext in ALL_MEDIA_EXTENSIONS

    def get_file_type(self, file_path):
        """Get the type of media file"""
        _, ext = os.path.splitext(file_path.lower())
        if ext in VIDEO_EXTENSIONS:
            return "VIDEO"
        elif ext in PHOTO_EXTENSIONS:
            return "PHOTO"
        return "UNKNOWN"

    def get_file_extension(self, file_path):
        """Get the file extension if it exists"""
        _, ext = os.path.splitext(file_path.lower())
        return ext

    def _get_parent_dir(self, path):
        """Get absolute path of the parent directory"""
        return os.path.abspath(os.path.dirname(path))

    def _process_batch(self, parent_path, items):
        """Process and report a batch of new items"""
        if not items:
            return

        # Filter out items that might have been moved/deleted before processing
        valid_items = [i for i in items if os.path.exists(i)]
        if not valid_items:
            return

        # Classify items
        media_items = [i for i in valid_items if self.is_media_file(i)]
        folders = [i for i in valid_items if os.path.isdir(i)]
        
        # Non-media files: Files that exist, are files, have an extension, but are NOT media
        non_media_items = []
        for i in valid_items:
            if not os.path.isdir(i):
                ext = self.get_file_extension(i)
                # Only include if it HAS an extension and is NOT media
                if ext and ext not in ALL_MEDIA_EXTENSIONS:
                    non_media_items.append(i)

        file_count = len(valid_items) - len(folders)
        folder_count = len(folders)
        media_count = len(media_items)
        non_media_count = len(non_media_items)

        # Log summary for the parent folder
        logger.info(f"Folder Batch Detected: {parent_path}")
        
        # Report Media Files if any
        if media_count > 0:
            logger.info(f"  -> Found {media_count} new media file(s) in batch")
            for item in media_items:
                try:
                    size = os.path.getsize(item)
                    ftype = self.get_file_type(item)
                    logger.info(f"  - NEW {ftype}: {os.path.basename(item)} ({size} bytes)")
                except OSError:
                    logger.warning(f"  - Could not read size: {os.path.basename(item)}")

        # Report Folders
        if folder_count > 0:
            logger.info(f"  -> Found {folder_count} new subfolder(s)")

        # Report Non-Media Files if any
        if non_media_count > 0:
            # Print the specific filenames of non-media items
            non_media_names = [os.path.basename(item) for item in non_media_items]
            logger.info(f"  -> Found {non_media_count} non-media file(s): {', '.join(non_media_names)}")

        # Trigger notification if there are media files
        if media_count > 0:
            self.show_batch_notification(media_items)

    def show_batch_notification(self, media_items):
        """Show a simple notification about detected media file"""
        # Just a placeholder for future GUI implementation
        pass

    def on_created(self, event):
        # Ignore directory creation events for batch purposes, only track files for now?
        # No, we want to track folders too, but let's ensure we don't double count
        if event.is_directory:
            # We track directory creation to detect new folders, but we don't add it to 'items' 
            # in the same way as files. We'll handle folders in _process_batch via os.path.isdir check
            pass
        
        abs_parent = self._get_parent_dir(event.src_path)
        now = time.time()

        with self.lock:
            # If we already processed a batch for this parent very recently (within 0.1s), ignore
            # This prevents the "Atmos" multiple reports issue
            batch_key = f"{abs_parent}_{int(now // 2)}" # Group by 2-second intervals roughly
            if batch_key in self._processed_batches:
                return
          
      
            if abs_parent in self.pending_batches:
                # We already have a pending batch for this folder, just add to it
                # Only add if it's not already in the list (avoid duplicates from fast events)
                if event.src_path not in self.pending_batches[abs_parent]['items']:
                    self.pending_batches[abs_parent]['items'].append(event.src_path)
                self.pending_batches[abs_parent]['timestamp'] = now  # Reset the timer
            else:
                # Start a new batch for this parent folder
                self.pending_batches[abs_parent] = {
                    'timestamp': now,
                    'items': [event.src_path]
                }

    def on_modified(self, event):
        # Ignore modification events to reduce noise. 
        # Folders are usually reported via 'created' or 'moved' when dropped.
        pass

    def on_moved(self, event):
        # Treat moved files as new files for simplicity in this context
        dest_parent = self._get_parent_dir(event.dest_path)
        now = time.time()

        with self.lock:
            if dest_parent in self.pending_batches:
                if event.dest_path not in self.pending_batches[dest_parent]['items']:
                    self.pending_batches[dest_parent]['items'].append(event.dest_path)
                self.pending_batches[dest_parent]['timestamp'] = now
            else:
                self.pending_batches[dest_parent] = {
                    'timestamp': now,
                    'items': [event.dest_path]
                }

    def on_deleted(self, event):
        pass

# Global handler instance
global_handler = FolderMonitorHandler()

# Thread to process pending batches
def batch_processor():
    """Thread that periodically checks pending batches and processes them"""
    while True:
        time.sleep(0.5)  # Check every half second
        
        with global_handler.lock:
            now = time.time()
            parents_to_remove = []
            
            for parent_path, batch_info in list(global_handler.pending_batches.items()):
                if now - batch_info['timestamp'] >= DEBOUNCE_DELAY:
                    # Timer expired, process the batch
                    items = batch_info['items']
                    parents_to_remove.append(parent_path)
                    
                    # Mark this batch as processed for this time interval to avoid duplicate reports
                    batch_key = f"{parent_path}_{int(now // 2)}"
                    global_handler._processed_batches.add(batch_key)
                    
                    # Keep the set from growing too large
                    if len(global_handler._processed_batches) > 100:
                        global_handler._processed_batches.clear()
                    
                    # Process the batch
                    global_handler._process_batch(parent_path, items)
            
            # Remove processed batches
            for parent_path in parents_to_remove:
                del global_handler.pending_batches[parent_path]

# Start the batch processor thread
batch_thread = threading.Thread(target=batch_processor, daemon=True)
batch_thread.start()

def monitor_folder(folder_path):
    if not os.path.exists(folder_path):
        logger.error(f"Folder does not exist: {folder_path}")
        return

    logger.info(f"Starting to monitor folder: {folder_path}")

    event_handler = global_handler
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping folder monitor...")
        observer.stop()

    observer.join()

def start_media_monitor():
    monitor_folder(watched_folder)

if __name__ == "__main__":
    folder_to_monitor = watched_folder
    monitor_folder(folder_to_monitor)