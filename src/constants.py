"""Constants for Kore application.

This module contains all constant values used throughout the application,
including paths, color tokens, and default values.
"""

from __future__ import annotations

from pathlib import Path
from platformdirs import PlatformDirs

# Application metadata
APP_NAME = "Kore"
APP_VERSION = "1.0.0"
APP_AUTHOR = "KoreTeam"

# Platform-specific directories
DIRS = PlatformDirs(APP_NAME, APP_AUTHOR)
CONFIG_DIR = Path(DIRS.user_config_dir)
CACHE_DIR = Path(DIRS.user_cache_dir)
OUTPUT_DIR = Path(DIRS.user_documents_path) / APP_NAME

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Database path
DB_PATH = CONFIG_DIR / "kore.db"

# Color tokens (from DESIGN.md)
COLOR_BG_BASE = "#0F1117"
COLOR_BG_SURFACE = "#1A1D27"
COLOR_BG_ELEVATED = "#22263A"
COLOR_BG_HOVER = "#2A2F47"
COLOR_BORDER = "#2E3250"
COLOR_BORDER_FOCUS = "#5C6BC0"

COLOR_SURFACE_CONTAINER = "#1e1f26"
COLOR_SURFACE_CONTAINER_LOW = "#191b22"
COLOR_SURFACE_CONTAINER_LOWEST = "#0c0e14"
COLOR_SURFACE_CONTAINER_HIGH = "#282a30"
COLOR_SURFACE_CONTAINER_HIGHEST = "#33343b"

COLOR_ACCENT_PRIMARY = "#6C63FF"
COLOR_ACCENT_SECONDARY = "#00D4AA"
COLOR_ACCENT_DANGER = "#FF5C6C"
COLOR_ACCENT_WARNING = "#FFB347"

COLOR_TEXT_PRIMARY = "#E8EAFF"
COLOR_TEXT_SECONDARY = "#8B90B8"
COLOR_TEXT_MUTED = "#5A5F80"

# Window dimensions
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 700
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 850

# UI constants
STATUS_BAR_HEIGHT = 28
SIDEBAR_WIDTH = 200
TITLE_BAR_HEIGHT = 32
BUTTON_CORNER_RADIUS = 8
CARD_CORNER_RADIUS = 12

# Supported image formats
SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg", ".webp"]

# Default settings
DEFAULT_THEME = "dark"
DEFAULT_OUTPUT_DIR = str(OUTPUT_DIR)
DEFAULT_GPU_ACCELERATION = True
DEFAULT_LAST_ACTIVE_TAB = "image"

# Database table names
TABLE_SETTINGS = "settings"
TABLE_DOWNLOAD_HISTORY = "download_history"
TABLE_PROCESSING_QUEUE = "processing_queue"
