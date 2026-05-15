"""SQLite database repository for Kore.

This module handles all database operations including schema initialization
and data access for settings, download history, and processing queue.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from src.constants import (
    DB_PATH,
    DEFAULT_GPU_ACCELERATION,
    DEFAULT_LAST_ACTIVE_TAB,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_THEME,
    TABLE_DOWNLOAD_HISTORY,
    TABLE_PROCESSING_QUEUE,
    TABLE_SETTINGS,
)
from src.models.settings import (
    AppSettings,
    DownloadHistory,
    DownloadStatus,
    ProcessingQueue,
    ProcessingStatus,
)


class DatabaseRepository:
    """Repository for SQLite database operations."""

    _instance: DatabaseRepository | None = None
    _lock = threading.Lock()

    def __new__(cls) -> DatabaseRepository:
        """Ensure singleton pattern for database connection."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize database connection and create schema."""
        self.db_path = DB_PATH
        self._ensure_database_exists()
        self._create_schema()
        self._seed_default_settings()

    @contextmanager
    def _get_connection(self):
        """Get a database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_database_exists(self) -> None:
        """Ensure database file and parent directory exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _create_schema(self) -> None:
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            # Settings table
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE_SETTINGS} (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Download history table
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE_DOWNLOAD_HISTORY} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    format_id TEXT NOT NULL,
                    resolution TEXT,
                    file_path TEXT NOT NULL,
                    file_size_bytes INTEGER,
                    status TEXT CHECK(status IN ('completed','failed','cancelled')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Processing queue table
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TABLE_PROCESSING_QUEUE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_path TEXT NOT NULL,
                    output_path TEXT,
                    operation TEXT CHECK(operation IN ('bg_removal')),
                    status TEXT CHECK(status IN ('pending','processing','done','error')),
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
                """
            )

    def _seed_default_settings(self) -> None:
        """Seed default settings if they don't exist."""
        defaults = {
            "theme": DEFAULT_THEME,
            "default_output_dir": DEFAULT_OUTPUT_DIR,
            "gpu_acceleration": str(DEFAULT_GPU_ACCELERATION).lower(),
            "last_active_tab": DEFAULT_LAST_ACTIVE_TAB,
        }

        with self._get_connection() as conn:
            for key, value in defaults.items():
                cursor = conn.execute(
                    f"SELECT 1 FROM {TABLE_SETTINGS} WHERE key = ?", (key,)
                )
                if cursor.fetchone() is None:
                    conn.execute(
                        f"INSERT INTO {TABLE_SETTINGS} (key, value) VALUES (?, ?)",
                        (key, value),
                    )

    def get_setting(self, key: str) -> str | None:
        """Get a setting value by key.

        Args:
            key: Setting key.

        Returns:
            Setting value or None if not found.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"SELECT value FROM {TABLE_SETTINGS} WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
            return row["value"] if row else None

    def set_setting(self, key: str, value: str) -> None:
        """Set a setting value.

        Args:
            key: Setting key.
            value: Setting value.
        """
        with self._get_connection() as conn:
            conn.execute(
                f"""
                INSERT INTO {TABLE_SETTINGS} (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP
                """,
                (key, value, value),
            )

    def get_app_settings(self) -> AppSettings:
        """Get all application settings.

        Returns:
            AppSettings model with current values.
        """
        theme = self.get_setting("theme") or DEFAULT_THEME
        output_dir = self.get_setting("default_output_dir") or DEFAULT_OUTPUT_DIR
        gpu = self.get_setting("gpu_acceleration") or str(DEFAULT_GPU_ACCELERATION).lower()
        last_tab = self.get_setting("last_active_tab") or DEFAULT_LAST_ACTIVE_TAB

        return AppSettings(
            theme=theme,
            default_output_dir=output_dir,
            gpu_acceleration=gpu == "true",
            last_active_tab=last_tab,
        )

    def save_app_settings(self, settings: AppSettings) -> None:
        """Save application settings.

        Args:
            settings: AppSettings model to save.
        """
        self.set_setting("theme", settings.theme.value)
        self.set_setting("default_output_dir", settings.default_output_dir)
        self.set_setting("gpu_acceleration", str(settings.gpu_acceleration).lower())
        self.set_setting("last_active_tab", settings.last_active_tab.value)

    def add_download_history(self, entry: DownloadHistory) -> int:
        """Add a download history entry.

        Args:
            entry: DownloadHistory model.

        Returns:
            ID of the inserted record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"""
                INSERT INTO {TABLE_DOWNLOAD_HISTORY}
                (url, title, format_id, resolution, file_path, file_size_bytes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.url,
                    entry.title,
                    entry.format_id,
                    entry.resolution,
                    entry.file_path,
                    entry.file_size_bytes,
                    entry.status.value,
                ),
            )
            return cursor.lastrowid

    def get_download_history(self, limit: int = 50) -> list[DownloadHistory]:
        """Get recent download history.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of DownloadHistory models.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"""
                SELECT * FROM {TABLE_DOWNLOAD_HISTORY}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [
                DownloadHistory(
                    id=row["id"],
                    url=row["url"],
                    title=row["title"],
                    format_id=row["format_id"],
                    resolution=row["resolution"],
                    file_path=row["file_path"],
                    file_size_bytes=row["file_size_bytes"],
                    status=DownloadStatus(row["status"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in rows
            ]

    def add_processing_queue(self, entry: ProcessingQueue) -> int:
        """Add a processing queue entry.

        Args:
            entry: ProcessingQueue model.

        Returns:
            ID of the inserted record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"""
                INSERT INTO {TABLE_PROCESSING_QUEUE}
                (input_path, output_path, operation, status, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    entry.input_path,
                    entry.output_path,
                    entry.operation.value,
                    entry.status.value,
                    entry.error_message,
                ),
            )
            return cursor.lastrowid

    def update_processing_status(
        self, job_id: int, status: ProcessingStatus, error_message: str | None = None
    ) -> None:
        """Update processing queue status.

        Args:
            job_id: Job ID to update.
            status: New status.
            error_message: Optional error message.
        """
        with self._get_connection() as conn:
            if status == ProcessingStatus.DONE:
                conn.execute(
                    f"""
                    UPDATE {TABLE_PROCESSING_QUEUE}
                    SET status = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (status.value, job_id),
                )
            else:
                conn.execute(
                    f"""
                    UPDATE {TABLE_PROCESSING_QUEUE}
                    SET status = ?, error_message = ?
                    WHERE id = ?
                    """,
                    (status.value, error_message, job_id),
                )
