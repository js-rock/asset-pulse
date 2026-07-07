import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, filedialog
from src.config import save_config, saved_watch_folder, saved_source_files

class FolderMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AssetPulse Monitor")
        self.root.geometry("900x400")

        # Variables to hold UI state
        self.watch_folder_path = tk.StringVar(value=saved_watch_folder)
        self.source_files_path = tk.StringVar(value=saved_source_files)

        # 1. Main Frame to hold Sidebar and Log
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- LEFT COLUMN: Controls ---
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Label for context (optional but helpful)
        ttk.Label(self.left_frame, text="Configuration & Actions").pack(anchor=tk.CENTER, pady=(0, 10))

        # Watch Folder Button
        self.btn_watch = ttk.Button(
            self.left_frame, 
            text="Set Watch Folder", 
            command=self.on_set_watch
        )
        self.btn_watch.pack(fill=tk.X, pady=2)

        # Source Files Button (Directly below Watch)
        self.btn_source = ttk.Button(
            self.left_frame, 
            text="Set Source Folder", 
            command=self.on_set_source
        )
        self.btn_source.pack(fill=tk.X, pady=2)

        # Start Transfer Button (Directly below Source)
        self.btn_transfer = ttk.Button(
            self.left_frame,
            text="Start Transfer",
            command=self.on_start_transfer
        )
        self.btn_transfer.pack(fill=tk.X, pady=10) # Extra padding below to separate from logs
        
        # Make the Transfer button look distinct (optional)
        self.btn_transfer['style'] = 'Accent.TButton' if hasattr(ttk, 'Style') else ''

        # --- RIGHT COLUMN: Log Output ---
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Log Header
        ttk.Label(self.right_frame, text="Activity Log").pack(anchor=tk.W, pady=(0, 5))

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
        else:
            self.append_log("GUI Initialized. Please select a watch folder.")

        self.update_button_labels()

    def setup_logging_handler(self):
        """Custom logging handler that pushes messages to the Tkinter Text widget."""
        self.logger = logging.getLogger("AssetPulse")
        self.logger.setLevel(logging.INFO)

        self.logger.propagate = False
        
        # File Handler
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler("logs/asset_pulse.log")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Tkinter Handler
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

        # Configure root logger to avoid duplicates
        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.addHandler(file_handler)
        root_logger.addHandler(tk_handler)
        root_logger.setLevel(logging.INFO)

    def _update_log(self, message):
        """Append message to the text widget safely."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

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
            
            # Check if the folder actually changed
            if current_watch != folder_path:
                # 1. Update UI state
                self.watch_folder_path.set(folder_path)
                self.update_button_labels()
                
                # 2. Save to config
                save_config({"watch_folder": folder_path, "source_files": self.source_files_path.get()})
                
                # 3. Log the change
                self.append_log(f"Watch Folder Changed: {folder_path}")
                self.append_log("Relaunching application...")
                
                # 4. Force Relaunch
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                # Folder is the same, just save
                save_config({"watch_folder": folder_path, "source_files": self.source_files_path.get()})
                self.append_log(f"Watch Folder Set: {folder_path}")
        else:
            self.append_log("Watch Folder selection cancelled.")

    def on_set_source(self):
        """Opens a folder selection dialog for Source Files folder."""
        folder_path = filedialog.askdirectory(
            title="Select Source Folder",
            initialdir=os.path.expanduser("~")
        )
        
        if folder_path:
            # 1. Save the path
            self.source_files_path.set(folder_path)
            
            # 2. Update the UI text
            self.update_button_labels()
            
            # 3. Save to persistent config
            save_config({"watch_folder": self.watch_folder_path.get(), "source_files": folder_path})
            
            # 4. Log
            self.append_log(f"Source Folder Set: {folder_path}")
        else:
            self.append_log("Source Folder selection cancelled.")

    def update_button_labels(self):
        """Helper to update button text to show current selection or 'Not Set'."""
        watch_val = self.watch_folder_path.get()
        if watch_val:
            # Truncate long paths for display
            display_watch = watch_val if len(watch_val) < 25 else ".../" + watch_val.split("/")[-1]
            self.btn_watch.config(text=f"Watched: {display_watch}")
        else:
            self.btn_watch.config(text="Set Watch Folder")
        
        source_val = self.source_files_path.get()
        if source_val:
            # Truncate long paths for display
            display_source = source_val if len(source_val) < 25 else ".../" + source_val.split("/")[-1]
            self.btn_source.config(text=f"Source: {display_source}")
        else:
            self.btn_source.config(text="Set Source Folder")

    def on_start_transfer(self):
        # Placeholder for transfer logic 
        self.append_log("Transfer Button Clicked. Logic to be implemented")