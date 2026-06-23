import tkinter as tk
from tkinter import ttk
import logging
import time

class FolderMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Asset Pulse Folder Watcher")
        self.root.geometry("800x600")
        
        # Configure the main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 1. Log Text Area (Scrollable)
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(self.text_frame, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(self.text_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 2. Button Area (Placeholder for future buttons)
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.btn_watch = ttk.Button(self.button_frame, text="Set Watch Folder", command=self.on_set_watch)
        self.btn_watch.pack(side=tk.LEFT, padx=5)
        
        self.btn_source = ttk.Button(self.button_frame, text="Set Source Files", command=self.on_set_source)
        self.btn_source.pack(side=tk.LEFT, padx=5)
        
        # Initialize Logging Handler
        self.setup_logging_handler()
        
        # Initial Info
        self.append_log("GUI Initialized. Waiting for logs...")

    def setup_logging_handler(self):
        """Custom logging handler that pushes messages to the Tkinter Text widget."""
        class TkHandler(logging.Handler):
            def __init__(self, gui_instance):
                super().__init__()
                self.gui = gui_instance
                
            def emit(self, record):
                log_entry = self.format(record)
                # Schedule GUI update in the main thread to avoid threading issues
                self.gui.root.after(0, self.gui._update_log, log_entry)
                
        # Create the handler
        tk_handler = TkHandler(self)
        tk_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Attach to the root logger
        logger = logging.getLogger()
        logger.addHandler(tk_handler)

    def _update_log(self, message):
        """Append message to the text widget safely."""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END) # Auto-scroll to bottom
        self.log_text.configure(state=tk.DISABLED)

    def append_log(self, message):
        """Helper to append non-logged messages directly."""
        self._update_log(message)

    def on_set_watch(self):
        # Placeholder for future functionality
        self.append_log("Action: Set Watch Folder clicked.")

    def on_set_source(self):
        # Placeholder for future functionality
        self.append_log("Action: Set Source Files clicked.")