import os
import shutil
import time
import logging
import threading
import hashlib
from pathlib import Path
from typing import List, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SyncTask:
    source_folder: str
    destination_folder: str

class RobustCopyEngine:
    def __init__(self):
        self.task_queue: List[SyncTask] = []
        self.queue_lock = threading.Lock()
        self.stop_event = threading.Event()
        
        
        # Callback for progress reporting: fn(copied_bytes, total_bytes, current_file, eta_str)
        self.progress_callback: Callable[[int, int, str, str], None] = None
        
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def set_progress_callback(self, callback: Callable[[int, int, str, str], None]):
        """Registers the GUI update hook."""
        self.progress_callback = callback

    def add_sync_task(self, source_folder: str, destination_folder: str):
        """Add a folder sync task."""
        with self.queue_lock:
            self.task_queue.append(SyncTask(source_folder, destination_folder))

    def stop(self):
        self.stop_event.set()
        self.worker_thread.join(timeout=10)

    def _process_queue(self):
        while not self.stop_event.is_set():
            task = None
            with self.queue_lock:
                if self.task_queue:
                    task = self.task_queue.pop(0)
            
            if task:
                self._execute_folder_sync(task)
            else:
                if self.stop_event.wait(timeout=0.5):
                    break

    def _execute_folder_sync(self, task: SyncTask):
        source_path = Path(task.source_folder).resolve()
        dest_root = Path(task.destination_folder).resolve()

        if not source_path.exists():
            logger.error(f"Source folder does not exist: {source_path}")
            return

        final_dest_path = dest_root / source_path.name
        final_dest_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting sync: {source_path} -> {final_dest_path}")

        try:
            # Phase 1: Scan sizes for an accurate total payload size
            all_files = []
            total_bytes = 0
            for root, dirs, files in os.walk(source_path):
                rel_dir = os.path.relpath(root, source_path)
                dest_dir = os.path.join(final_dest_path, rel_dir)
                os.makedirs(dest_dir, exist_ok=True)
                
                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    
                    # Check if file actually needs a transfer
                    needs_update = True
                    if os.path.exists(dest_file):
                        src_stat = os.stat(src_file)
                        dest_stat = os.stat(dest_file)
                        if src_stat.st_size == dest_stat.st_size and abs(src_stat.st_mtime - dest_stat.st_mtime) < 1:
                            needs_update = False
                            
                    if needs_update:
                        f_size = os.path.getsize(src_file)
                        total_bytes += f_size
                        all_files.append((src_file, dest_file, f_size))

            if not all_files:
                logger.info("Everything up to date. Nothing to sync.")
                if self.progress_callback:
                    self.progress_callback(0, 0, "Idle", "ETA: 00:00")
                return

            # Phase 2: Copy items using a shared timer across the whole task
            copied_bytes = 0
            start_time = time.time()
            last_ui_update = 0

            for src_file, dest_file, f_size in all_files:
                if self.stop_event.is_set():
                    break
                
                # Chunked internal file sync loop
                temp_dest = dest_file + '.tmp'
                try:
                    with open(src_file, 'rb') as fsrc, open(temp_dest, 'wb') as fdest:
                        while True:
                            if self.stop_event.is_set():
                                break
                            chunk = fsrc.read(1024 * 1024) # 1MB blocks
                            if not chunk:
                                break
                            fdest.write(chunk)
                            copied_bytes += len(chunk)
                            
                            # Smooth UI throttled update (Max 10 updates per second to protect Tkinter thread)
                            now = time.time()
                            if now - last_ui_update > 0.1:
                                elapsed = now - start_time
                                speed = copied_bytes / elapsed if elapsed > 0 else 0
                                remaining_bytes = total_bytes - copied_bytes
                                
                                if speed > 0:
                                    eta_secs = remaining_bytes / speed
                                    mins, secs = divmod(int(eta_secs), 60)
                                    eta_str = f"ETA: {mins}:{secs:02d} ({speed / (1024*1024):.1f} MB/s)"
                                else:
                                    eta_str = "ETA: Calculating..."

                                if self.progress_callback:
                                    self.progress_callback(copied_bytes, total_bytes, os.path.basename(src_file), eta_str)
                                last_ui_update = now

                    # Final verification and atomic step
                    if not self._verify_integrity(src_file, temp_dest):
                        logger.warning(f"Integrity check failed for {src_file}")
                        if os.path.exists(temp_dest):
                            os.remove(temp_dest)
                        continue
                    else:
                        logger.info(f"Verified {os.path.basename(src_file)} is bit perfect.")

                    if os.path.exists(dest_file):
                        os.remove(dest_file)
                    os.rename(temp_dest, dest_file)
                    shutil.copystat(src_file, dest_file)

                except Exception as e:
                    logger.error(f"Error transferring {src_file}: {e}")
                    if os.path.exists(temp_dest):
                        try: os.remove(temp_dest)
                        except: pass

            # Complete
            if self.progress_callback:
                self.progress_callback(total_bytes, total_bytes, "Sync Finished", "ETA: 00:00")
            logger.info(f"Sync completed: {source_path} -> {final_dest_path}")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")

    def _verify_integrity(self, src: str, dst: str) -> bool:
        """Calculates and compares SHA-256 hashes for bit-perfect verification."""
        try:
            return self._get_file_hash(src) == self._get_file_hash(dst)
        except Exception as e:
            logger.error(f"Hash verification error: {e}")
            return False

    def _get_file_hash(self, file_path: str) -> str:
        """Helper to compute hash."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""): # 64KB chunks are faster
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


copy_engine = RobustCopyEngine()