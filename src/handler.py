"""
Handler module for Folder Monitor.
Contains the Watchdog event handler and debouncing logic.
"""

import os
import time
import logging
from threading import Lock
from watchdog.events import FileSystemEventHandler

from config import config

logger = logging.getLogger(__name__)


class FolderMonitorHandler(FileSystemEventHandler):
    """Handles file system events with debouncing to suppress noise from folder drops"""

    def __init__(self):
        self.pending_batches = {}
        self.lock = Lock()
        self._processed_batches = set()

    def _get_parent_dir(self, path: str) -> str:
        return os.path.abspath(os.path.dirname(path))

    def _process_batch(self, parent_path: str, items: list):
        """Process and report a batch of new items"""
        if not items:
            return

        # Filter out items that might have been moved/deleted before processing
        valid_items = [i for i in items if os.path.exists(i)]
        if not valid_items:
            return

        # Classify items
        media_items = [i for i in valid_items if config.is_media_file(i)]
        folders = [i for i in valid_items if os.path.isdir(i)]
        
        # Non-media files: Files that exist, are files, have an extension, but are NOT media
        non_media_items = []
        for i in valid_items:
            if not os.path.isdir(i):
                _, ext = config._get_extension(i)
                # Only include if it HAS an extension, is NOT ignored, and is NOT media
                if ext and ext not in config.IGNORED_EXTENSIONS and ext not in config.ALL_MEDIA_EXTENSIONS:
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
                    ftype = config.get_file_type(item)
                    logger.info(f"  - NEW {ftype}: {os.path.basename(item)} ({size} bytes)")
                except OSError:
                    logger.warning(f"  - Could not read size: {os.path.basename(item)}")

        # Report Folders
        if folder_count > 0:
            logger.info(f"  -> Found {folder_count} new subfolder(s)")

        # Report Non-Media Files if any
        if non_media_count > 0:
            non_media_names = [os.path.basename(item) for item in non_media_items]
            logger.info(f"  -> Found {non_media_count} non-media file(s): {', '.join(non_media_names)}")

        # Trigger notification if there are media files
        if media_count > 0:
            self.show_batch_notification(media_items)

    def show_batch_notification(self, media_items):
        """Placeholder for GUI or external notifications"""
        pass

    def on_created(self, event):
        abs_parent = self._get_parent_dir(event.src_path)
        now = time.time()

        with self.lock:
            batch_key = f"{abs_parent}_{int(now // config.CHECK_INTERVAL)}"
            if batch_key in self._processed_batches:
                return
            
            if abs_parent in self.pending_batches:
                if event.src_path not in self.pending_batches[abs_parent]['items']:
                    self.pending_batches[abs_parent]['items'].append(event.src_path)
                self.pending_batches[abs_parent]['timestamp'] = now
            else:
                self.pending_batches[abs_parent] = {
                    'timestamp': now,
                    'items': [event.src_path]
                }

    def on_modified(self, event):
        pass

    def on_moved(self, event):
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


class BatchProcessor:
    """Thread that periodically checks pending batches and processes them"""
    
    def __init__(self, handler: FolderMonitorHandler):
        self.handler = handler

    def run(self):
        """Main loop for the processor thread"""
        while True:
            time.sleep(config.CHECK_INTERVAL)
            
            with self.handler.lock:
                now = time.time()
                parents_to_remove = []
                
                for parent_path, batch_info in list(self.handler.pending_batches.items()):
                    if now - batch_info['timestamp'] >= config.DEBOUNCE_DELAY:
                        items = batch_info['items']
                        parents_to_remove.append(parent_path)
                        
                        batch_key = f"{parent_path}_{int(now // config.CHECK_INTERVAL)}"
                        self.handler._processed_batches.add(batch_key)
                        
                        if len(self.handler._processed_batches) > 100:
                            self.handler._processed_batches.clear()
                        
                        self.handler._process_batch(parent_path, items)
                
                for parent_path in parents_to_remove:
                    del self.handler.pending_batches[parent_path]
