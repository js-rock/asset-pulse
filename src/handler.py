"""
Handler module for Folder Monitor.
Contains the Watchdog event handler and debouncing logic.
"""

import os
import time
import logging
from threading import Lock
from watchdog.events import FileSystemEventHandler

from src.config import config

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
        """Process and report a batch of new or deleted items"""
        if not items:
            return

        # Separate existing and deleted items
        # If an item exists, it was likely created or moved there.
        # If it doesn't exist, it was likely deleted.
        existing_items = [i for i in items if os.path.exists(i)]
        deleted_items = [i for i in items if not os.path.exists(i)]

        # If there are no existing items, we treat it as a deletion batch
        if not existing_items:
            self._report_deleted_items(parent_path, deleted_items)
            return

        # If there are existing items, process them as "Found"
        self._report_found_items(parent_path, existing_items)
        
        # If there are also deletions, report them separately
        if deleted_items:
            self._report_deleted_items(parent_path, deleted_items)

    def _report_found_items(self, parent_path: str, items: list):
        """Process and report found items with specific batch type headers"""
        
        # Classify items
        media_items = [i for i in items if config.is_media_file(i)]
        folders = [i for i in items if os.path.isdir(i)]
        
        # Non-media files: Files that exist, are files, have an extension, but are NOT media
        non_media_items = []
        for i in items:
            if not os.path.isdir(i):
                _, ext = config._get_extension(i)
                # Only include if it HAS an extension, is NOT ignored, and is NOT media
                # if ext and ext not in config.IGNORED_EXTENSIONS and ext not in config.ALL_MEDIA_EXTENSIONS:
                #     non_media_items.append(i)

        file_count = len(items) - len(folders)
        folder_count = len(folders)
        media_count = len(media_items)
        non_media_count = len(non_media_items)

        # Only show the "Batch Detected" header if we have MORE than 1 item
        if len(items) > 1:
            # Determine the primary type of this batch to customize the log header
            if media_count > 0 and folder_count == 0 and non_media_count == 0:
                header = f"Media Batch Detected: {parent_path}"
            elif folder_count > 0 and media_count == 0 and non_media_count == 0:
                header = f"Folder Batch Detected: {parent_path}"
            elif non_media_count > 0 and media_count == 0 and folder_count == 0:
                header = f"File Batch Detected: {parent_path}"
            else:
                header = f"Batch Detected: {parent_path}"
            
            logger.info(header)

        # Report Media Files if any
        if media_count > 0:
            # Optional: Add a count summary for media
            logger.info(f"  -> Found {media_count} new media file(s)")
            for item in media_items:
                try:
                    size = os.path.getsize(item)
                    ftype = config.get_file_type(item)
                    # Format: - TYPE: filename (size)
                    logger.info(f"  - NEW {ftype}: {os.path.basename(item)} ({size} bytes)")
                except OSError:
                    logger.warning(f"  - Could not read size: {os.path.basename(item)}")

        # Report Folders
        if folder_count > 0:
            logger.info(f"  -> Found {folder_count} new subfolder(s)")
            for item in folders:
                logger.info(f"  - NEW FOLDER: {os.path.basename(item)}")

        # --- REPORT NON-MEDIA FILES (ONE PER LINE) ---
        if non_media_count > 0:
            # We just iterate through every single non-media item
            for item in non_media_items:
                basename = os.path.basename(item)
                _, ext = config._get_extension(item)
                # Format: - EXTENSION: filename
                # This makes it easy to read and search
                logger.info(f"  - NEW {ext}: {basename}")

        # Trigger notification if there are media files
        if media_count > 0:
            self.show_batch_notification(media_items)

    def _report_deleted_items(self, parent_path: str, items: list):
        """Report items that were deleted"""
        logger.info(f"Folder Deletions Detected: {parent_path}")
        
        deleted_media = []
        deleted_non_media = []
        
        for item in items:
            # Since the file is deleted, we check the extension to determine type
            _, ext = config._get_extension(item)
            
            # Check if it looks like a media file based on extension
            if ext and ext in config.ALL_MEDIA_EXTENSIONS:
                deleted_media.append(item)
            else:
                # Add to non-media list. 
                # Note: We don't filter by IGNORED_EXTENSIONS here because if it was deleted,
                # we usually want to know what was removed, even if it's a config file.
                # However, if you want to hide junk deletions, uncomment the line below:
                # if ext and ext in config.IGNORED_EXTENSIONS: continue
                deleted_non_media.append(item)
        
        # --- REPORT DELETED MEDIA (One per line with type) ---
        if deleted_media:
            logger.info(f"  -> Deleted {len(deleted_media)} media file(s)")
            for item in deleted_media:
                ftype = config.get_file_type(item)
                logger.info(f"  - DELETED {ftype}: {os.path.basename(item)}")
        
        # --- REPORT DELETED NON-MEDIA (One per line) ---
        if deleted_non_media:
            # Now we iterate individually instead of grouping
            logger.info(f"  -> Deleted {len(deleted_non_media)} other file(s)")
            for item in deleted_non_media:
                _, ext = config._get_extension(item)
                # Format: - DELETED [EXT]: filename
                logger.info(f"  - DELETED {ext}: {os.path.basename(item)}")

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
        """Capture deletion events into the pending batch"""
        parent_path = self._get_parent_dir(event.src_path)
        now = time.time()

        with self.lock:
            # Prevent duplicate processing of the same debounce window
            batch_key = f"{parent_path}_{int(now // config.CHECK_INTERVAL)}"
            if batch_key in self._processed_batches:
                return

            if parent_path in self.pending_batches:
                if event.src_path not in self.pending_batches[parent_path]['items']:
                    self.pending_batches[parent_path]['items'].append(event.src_path)
                self.pending_batches[parent_path]['timestamp'] = now
            else:
                self.pending_batches[parent_path] = {
                    'timestamp': now,
                    'items': [event.src_path]
                }


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