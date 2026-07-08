import os
import subprocess
import platform

def open_watched_folder(path: str):
    """
    Opens the given folder path in the native file explorer.
    Cross-platform: Windows (explorer), macOS (open), Linux (xdg-open).
    """

    if not os.path.isdir(path):
        raise ValueError(f"Path is not a directory: {path}")
    
    system = platform.system()

    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin": # macos
        subprocess.Popen(["open", path])
    else:  # Linux
        subprocess.Popen(["xdg-open", path])