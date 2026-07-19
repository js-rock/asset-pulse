# src/asset_pulse/gui.py
import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, filedialog
from .config import save_config, saved_watch_folder, saved_source_files, load_config
from .os_utils import open_watched_folder
from .copy_engine import copy_engine 

class FolderMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AssetPulse Monitor")
        self.root.geometry("1000x440")

        # Variables to hold UI state
        self.watch_folder_path = tk.StringVar(value=saved_watch_folder)
        self.source_files_path = tk.StringVar(value=saved_source_files)

        # 1. Main Frame to hold Sidebar and Log
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- LEFT COLUMN: Controls ---
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Label for context
        ttk.Label(self.left_frame, text="Configuration & Actions").pack(anchor=tk.CENTER, pady=(0, 10))

        # Copy Status Label
        self.lbl_copy_status = ttk.Label(self.left_frame, text="", foreground="blue")
        self.lbl_copy_status.pack(fill=tk.X, pady=5)

        # Watch Folder Button
        self.btn_watch = ttk.Button(
            self.left_frame, 
            text="Set Watch Folder", 
            command=self.on_set_watch
        )
        self.btn_watch.pack(fill=tk.X, pady=2)

        # Reveal Watch Folder Button
        self.btn_reveal = ttk.Button(
            self.left_frame, 
            text="Reveal Watch Folder", 
            command=self.on_reveal_watch,
            state=tk.DISABLED
        )
        self.btn_reveal.pack(fill=tk.X, pady=2)

        # Optional Hints
        self.lbl_source_hint = ttk.Label(
            self.left_frame,
            text="Optional: Use these or drag and drop.",
            foreground="gray",
            font=("Segoe UI", 8)
        )
        self.lbl_source_hint.pack(fill=tk.X, pady=(5, 2))

        # Source Files Button
        self.btn_source = ttk.Button(
            self.left_frame, 
            text="Set Source Folder", 
            command=self.on_set_source
        )
        self.btn_source.pack(fill=tk.X, pady=2)

        # Start Copy Button
        self.btn_copy = ttk.Button(
            self.left_frame,
            text="Start Copy",
            command=self.on_start_copy
        )
        self.btn_copy.pack(fill=tk.X, pady=2)

        # --- PROGRESS & ETA PACK ---
        self.progress_frame = ttk.Frame(self.left_frame)
        self.progress_frame.pack(fill=tk.X, pady=(15, 0))

        self.lbl_current_file = ttk.Label(self.progress_frame, text="", font=("Segoe UI", 8), foreground="gray")
        self.lbl_current_file.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=2)

        self.lbl_eta = ttk.Label(self.progress_frame, text="", font=("Segoe UI", 9))
        self.lbl_eta.pack(anchor=tk.E)

        # Connect the background engine callback loop directly to the engine instance
        copy_engine.set_progress_callback(self.trigger_ui_progress_update)

        # --- TOTALS DISPLAY ---
        self.lbl_totals = ttk.Label(self.left_frame, text="", justify=tk.LEFT, font=("Segoe UI", 9, "bold"))
        self.lbl_totals.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0), anchor=tk.W)

        # --- RIGHT COLUMN: Log Output ---
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Log Header
        self.log_header_frame = ttk.Frame(self.right_frame)
        self.log_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.log_header_frame, text="Activity Log").pack(side=tk.LEFT, anchor=tk.W)
        
        self.btn_clear_log = ttk.Button(
            self.log_header_frame, 
            text="Clear Log File (.txt)", 
            command=self.on_clear_log
        )
        self.btn_clear_log.pack(side=tk.RIGHT, padx=5)
        
        self.btn_reveal_log = ttk.Button(
            self.log_header_frame, 
            text="Reveal Log Folder", 
            command=lambda: open_watched_folder("logs")
        )
        self.btn_reveal_log.pack(side=tk.RIGHT)

        # Scrollable Active Log Text Area
        self.log_frame = ttk.Frame(self.right_frame)
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(self.log_frame, state=tk.DISABLED, bg="#f0f0f0", font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Initialize Logging Handler
        self.setup_logging_handler()
        
        # Initial Info
        current_watch = self.watch_folder_path.get()
        if current_watch:
            self.append_log(f"Restored previous session. Watch Folder: {current_watch}")
            self.btn_reveal.config(state=tk.NORMAL)
        else:
            self.append_log("GUI Initialized. Please select a watch folder.")

        self.update_button_labels()

    def setup_logging_handler(self):
        """Custom logging handler that pushes messages to the Tkinter Text widget."""
        self.logger = logging.getLogger("AssetPulse")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        self.file_handler = logging.FileHandler("logs/asset_pulse.log")
        self.file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)

        class TkHandler(logging.Handler):
            def __init__(self, gui_instance):
                super().__init__()
                self.gui = gui_instance
                self.setFormatter(formatter)
            
            def emit(self, record):
                log_entry = self.format(record)
                self.gui.root.after(0, self.gui._update_log, log_entry)
        
        tk_handler = TkHandler(self)
        self.logger.addHandler(tk_handler)

        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.addHandler(self.file_handler)
        root_logger.addHandler(tk_handler)
        root_logger.setLevel(logging.INFO)

    def _update_log(self, message):
        """Append message to the text widget safely."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.update_button_labels()

    def append_log(self, message):
        """Helper to log messages using our configured logger."""
        self.logger.info(message)

    def on_set_watch(self):
        """Opens a folder selection dialog for the Watch Folder."""
        folder_path = filedialog.askdirectory(
            title="Select the Folder to Watch",
            initialdir=os.path.expanduser("~")
        )
        if folder_path:
            current_watch = self.watch_folder_path.get()
            if current_watch != folder_path:
                self.watch_folder_path.set(folder_path)
                self.update_button_labels()
                save_config({"watch_folder": folder_path, "source_files": self.source_files_path.get()})
                self.append_log(f"Watch Folder Changed: {folder_path}")
                self.append_log("Relaunching application.")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                save_config({"watch_folder": folder_path, "source_files": self.source_files_path.get()})
                self.append_log(f"Watch Folder Set: {folder_path}")
                self.btn_reveal.config(state=tk.NORMAL)
        else:
            self.append_log("Watch Folder selection cancelled.")

    def on_reveal_watch(self):
        """Opens the currently set Watch Folder in the system file explorer."""
        folder_path = self.watch_folder_path.get()
        if not folder_path:
            return
        try:
            open_watched_folder(folder_path)
            self.append_log(f"Revealed watched folder in Explorer: {folder_path}")
        except Exception as e:
            self.append_log(f"Error revealing the watched folder: {e}")
 
    def on_set_source(self):
        """Opens a folder selection dialog for the Source Folder."""
        folder_path = filedialog.askdirectory(
            title="Select the Source Folder for Copy",
            initialdir=os.path.expanduser("~")
        )
        if folder_path:
            self.source_files_path.set(folder_path)
            current_config = load_config()
            current_config['source_files'] = folder_path
            save_config(current_config)
            
            self.btn_source.config(text=f"Source: {os.path.basename(folder_path)}")
            self.append_log(f"Source Folder Set: {folder_path}")
        else:
            self.append_log("Source Folder selection cancelled.") 

    def on_clear_log(self):
        """Safely breaks system locks, truncates disk file sizes, and clears the UI stream."""
        try:
            self.file_handler.close()
            
            log_path = "logs/asset_pulse.log"
            if os.path.exists(log_path):
                with open(log_path, "w") as f:
                    f.truncate(0)
            
            self.file_handler.stream = open(log_path, "a")
            
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete("1.0", tk.END)
            self.log_text.config(state=tk.DISABLED)
            
            self.append_log("Log history cleared successfully.")
        except Exception as e:
            print(f"Error executing log purge sequences: {e}")

    def _calculate_binary_size_label(self, total_bytes):
        """Generates exact, absolute string representations for data validation."""
        if total_bytes == 0:
            return "Size: 0 Bytes"
        bytes_line = f"Size: {total_bytes:,} Bytes"
        bytes_float = float(total_bytes)
        for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
            if bytes_float < 1024.0:
                if unit == 'Bytes':
                    return bytes_line
                return f"{bytes_line}\nSize on Disk: {bytes_float:.2f} {unit}"
            bytes_float /= 1024.0
        return f"{bytes_line}\nSize on Disk: {bytes_float:.2f} PB"

    def update_button_labels(self):
        """Helper to update button text and execute recursive directory metrics."""
        watch_val = self.watch_folder_path.get()
        if watch_val:
            display_watch = watch_val if len(watch_val) < 25 else ".../" + watch_val.split("/")[-1]
            self.btn_watch.config(text=f"Watched: {display_watch}")
            self.btn_reveal.config(state=tk.NORMAL)
            
            try:
                files_count = 0
                folders_count = 0
                total_bytes = 0
          
                if os.path.exists(watch_val):
                    for root_dir, dirs, files in os.walk(watch_val):
                        files_count += len(files)
                        folders_count += len(dirs)
                        for f in files:
                            fp = os.path.join(root_dir, f)
                            try:
                                total_bytes += os.path.getsize(fp)
                            except OSError:
                                continue
          
                size_output_lines = self._calculate_binary_size_label(total_bytes)
                self.lbl_totals.config(
                    text=f"Contains:\n{files_count:,} Files\n{folders_count:,} Folders\n{size_output_lines}"
                )
            except Exception:
                self.lbl_totals.config(text="Contains:\nCalculation Error")
        else:
            self.btn_watch.config(text="Set Watch Folder")
            self.btn_reveal.config(state=tk.DISABLED)
            self.lbl_totals.config(text="")

    def on_start_copy(self):
        """Triggered when the Copy button is clicked."""
        watch_folder = self.watch_folder_path.get()       # Destination
        source_folder = self.source_files_path.get()      # Origin

        if not watch_folder or not source_folder:
            self.append_log("Error: Both Watch Folder (Destination) and Source Folder (Origin) must be set.")
            return

        # Validate Source (Origin) exists
        if not os.path.isdir(source_folder):
            self.append_log(f"Error: Source Folder (Origin) does not exist: {source_folder}")
            return

        # Validate Destination exists or create it
        if not os.path.isdir(watch_folder):
            try:
                os.makedirs(watch_folder)
                self.append_log(f"Created destination folder: {watch_folder}")
            except Exception as e:
                self.append_log(f"Error creating destination folder: {e}")
                return

        self.lbl_copy_status.config(text="Starting Folder Sync...")
        self.append_log(f"Starting sync from {source_folder} to {watch_folder}")

        # Add a single sync task to the engine
        try:
            # This triggers the NEW RobustCopyEngine folder sync logic
            copy_engine.add_sync_task(source_folder, watch_folder)
            self.append_log("Sync task added to queue. Files will be copied in background.")
        except Exception as e:
            self.append_log(f"Error adding sync task: {e}")

    def flash_log(self):
        self.root.after(0, self._perform_flash)

    def _perform_flash(self):
        self.log_text.config(bg="#e0f7fa")
        self.root.after(1000, lambda: self.log_text.config(bg="white"))

    def trigger_ui_progress_update(self, copied, total, current_filename, eta_string):
        """Thread-safe proxy mapping that pushes updates to the Tkinter execution main loop."""
        self.root.after(0, self._safe_ui_progress_update, copied, total, current_filename, eta_string)

    def _safe_ui_progress_update(self, copied, total, current_filename, eta_string):
        if total > 0:
            percentage = (copied / total) * 100
            self.progress_bar["value"] = percentage
            self.lbl_current_file.config(text=f"Copying: {current_filename}")
            self.lbl_eta.config(text=eta_string)
            
            # Static state instead of rapid percentage updates
            if copied == total:
                self.lbl_copy_status.config(text="Idle", foreground="gray")
            else:
                self.lbl_copy_status.config(text="Syncing...", foreground="blue")
        else:
            self.progress_bar["value"] = 0
            self.lbl_current_file.config(text="")
            self.lbl_eta.config(text="")
            self.lbl_copy_status.config(text="Idle", foreground="gray")