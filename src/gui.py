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
        self.root.geometry("600x400")

        # Variables to hold UI state
        self.watch_folder_path = tk.StringVar(value=saved_watch_folder)
        self.source_files_path = tk.StringVar(value=saved_source_files)

        # 1. Main Frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 2. Button Area with Path Display
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)

        # Watch Folder Button
        self.btn_watch = ttk.Button(
            self.button_frame, 
            text="Set Watch Folder", 
            command=self.on_set_watch
        )
        self.btn_watch.pack(side=tk.TOP, padx=5, anchor=tk.W)
        
        # Source Files Button
        self.btn_source = ttk.Button(
            self.button_frame, 
            text="Set Source Files", 
            command=self.on_set_source
        )
        self.btn_source.pack(side=tk.TOP, padx=5, anchor=tk.W)

        # 3. Log Text Area
        self.log_frame = ttk.Frame(self.main_frame)
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(self.log_frame, state=tk.DISABLED, bg="#f0f0f0")
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
            # 1. Save the path in the Variable
            self.watch_folder_path.set(folder_path)
            
            # 2. Update the UI text for the button
            self.update_button_labels()
            
            # 3. Save to persistent config file
            save_config({"watch_folder": folder_path, "source_files": self.source_files_path.get()})
            
            # 4. Log the action
            self.append_log(f"Watch Folder Set and Saved: {folder_path}")
        else:
            self.append_log("Watch Folder selection cancelled.")

    def on_set_source(self):
        """Opens a file selection dialog for Source Files."""
        file_paths = filedialog.askopenfilenames(
            title="Select Source Files",
            filetypes=[
                ("All Files", "*.*"),
                ("Media Files", "*.jpg *.png *.mp4 *.mov *.mp3 *.wav")
            ]
        )
        
        if file_paths:
            # 1. Save the path (join tuple into string)
            self.source_files_path.set("; ".join(file_paths))
            
            # 2. Update the UI text for the button
            self.update_button_labels()
            
            # 3. Save to persistent config file
            save_config({"watch_folder": self.watch_folder_path.get(), "source_files": "; ".join(file_paths)})
            
            # 4. Log the action
            self.append_log(f"Source Files Set and Saved: {len(file_paths)} file(s)")
        else:
            self.append_log("Source Files selection cancelled.")

    def update_button_labels(self):
        """Helper to update button text to show current selection or 'Not Set'."""
        watch_val = self.watch_folder_path.get()
        if watch_val:
            # Show full path in button text for clarity
            self.btn_watch.config(text=f"Watch: {watch_val}")
        else:
            self.btn_watch.config(text="Set Watch Folder")
        
        source_val = self.source_files_path.get()
        if source_val:
            self.btn_source.config(text=f"Source: {source_val}")
        else:
            self.btn_source.config(text="Set Source Files")