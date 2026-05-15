"""Pydantic models for application settings.

This module contains data models for application configuration and settings.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Theme(str, Enum):
    """Available theme options."""

    DARK = "dark"
    LIGHT = "light"


class Tab(str, Enum):
    """Available tabs in the application."""

    IMAGE = "image"
    VIDEO = "video"
    SETTINGS = "settings"


class DownloadStatus(str, Enum):
    """Status of a download job."""

    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingStatus(str, Enum):
    """Status of an image processing job."""

    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class ProcessingOperation(str, Enum):
    """Types of image processing operations."""

    BG_REMOVAL = "bg_removal"


class AppSettings(BaseModel):
    """Application settings model.

    This model represents the application configuration stored in the database.
    """

    theme: Theme = Field(default=Theme.DARK, description="Application theme")
    default_output_dir: str = Field(
        default="~/Kore", description="Default output directory for files"
    )
    gpu_acceleration: bool = Field(
        default=True, description="Enable GPU acceleration for image processing"
    )
    last_active_tab: Tab = Field(
        default=Tab.IMAGE, description="Last active tab"
    )

    @field_validator("default_output_dir")
    @classmethod
    def expand_home(cls, v: str) -> str:
        """Expand ~ to home directory in path."""
        return v.replace("~", "~")  # Will be expanded by pathlib


class DownloadHistory(BaseModel):
    """Download history entry model.

    This model represents a completed video download record.
    """

    id: int | None = Field(default=None, description="Database ID")
    url: str = Field(..., description="Video URL")
    title: str | None = Field(default=None, description="Video title")
    format_id: str = Field(..., description="Format identifier from yt-dlp")
    resolution: str | None = Field(default=None, description="Video resolution")
    file_path: str = Field(..., description="Local file path")
    file_size_bytes: int | None = Field(default=None, description="File size in bytes")
    status: DownloadStatus = Field(
        default=DownloadStatus.COMPLETED, description="Download status"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp of download"
    )


class ProcessingQueue(BaseModel):
    """Image processing queue entry model.

    This model represents a background image processing job.
    """

    id: int | None = Field(default=None, description="Database ID")
    input_path: str = Field(..., description="Input image path")
    output_path: str | None = Field(default=None, description="Output image path")
    operation: ProcessingOperation = Field(
        default=ProcessingOperation.BG_REMOVAL, description="Processing operation"
    )
    status: ProcessingStatus = Field(
        default=ProcessingStatus.PENDING, description="Processing status"
    )
    error_message: str | None = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when job was created"
    )
    completed_at: datetime | None = Field(
        default=None, description="Timestamp when job completed"
    )
