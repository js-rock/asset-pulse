"""
Configuration module for Folder Monitor.
Holds all settings, extensions, and debounce rules.
"""

from dataclasses import dataclass, field
from typing import Set


@dataclass
class WatcherConfig:
    """Centralized configuration for the folder monitor."""
    
    # Directories to watch
    watched_folders: list[str] = field(default_factory=lambda: ['F:/_DummyNAS/test_watch'])
    
    # File extensions (now lowercase for case-insensitive matching)
    VIDEO_EXTENSIONS: Set[str] = frozenset({
        '.mp4', '.MP4', '.avi', '.mkv', '.mov', '.MOV', '.wmv', '.flv', 
        '.webm', '.mpg', '.mpeg', '.3gp', '.m4v'
    })
    
    PHOTO_EXTENSIONS: Set[str] = frozenset({
        '.jpg', '.JPG', '.jpeg', '.png', '.PNG', '.gif', '.bmp', '.tiff', 
        '.webp', '.raw', '.cr2', '.nef', '.NEF' '.orf', '.sr2'
    })
    
    # Extensions to ignore entirely (even if they exist in folders)
    IGNORED_EXTENSIONS: Set[str] = frozenset({
        '.tmp', '.log', '.part', '.json'#, '.xml', '.nfo' # Example ignores
    })

    # Debounce settings
    DEBOUNCE_DELAY: float = 10.0  # Seconds
    CHECK_INTERVAL: float = 0.5  # Seconds (how often the processor thread wakes up)
    
    # Logging settings
    LOG_FILE: str = 'folder_monitor.log'
    LOG_FORMAT: str = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT: int = 5

    @property
    def ALL_MEDIA_EXTENSIONS(self) -> Set[str]:
        """Union of video and photo extensions."""
        return self.VIDEO_EXTENSIONS | self.PHOTO_EXTENSIONS

    def get_file_type(self, file_path: str) -> str:
        """Determine the type of media file based on extension."""
        _, ext = self._get_extension(file_path)
        # Normalize to lowercase for comparison
        ext_lower = ext.lower()
        
        if ext_lower in self.VIDEO_EXTENSIONS:
            return "VIDEO"
        elif ext_lower in self.PHOTO_EXTENSIONS:
            return "PHOTO"
        return "UNKNOWN"

    def is_media_file(self, file_path: str) -> bool:
        """Check if a file is a valid media file (case-insensitive)."""
        if not file_path:
            return False
        _, ext = self._get_extension(file_path)
        # Normalize to lowercase for comparison
        return ext.lower() in self.ALL_MEDIA_EXTENSIONS

    def _get_extension(self, file_path: str) -> tuple:
        """Helper to safely get extension."""
        import os
        name, ext = os.path.splitext(file_path)
        return name, ext

# Singleton instance for easy access throughout the app
config = WatcherConfig()