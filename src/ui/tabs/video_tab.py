"""Video Grab tab for video downloading.

This module contains the UI and logic for the video download feature.
"""

from __future__ import annotations

import logging
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from src.constants import (
    COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_SECONDARY,
    COLOR_BG_BASE,
    COLOR_BG_ELEVATED,
    COLOR_BG_HOVER,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_SURFACE_CONTAINER,
    COLOR_SURFACE_CONTAINER_HIGH,
    COLOR_SURFACE_CONTAINER_LOW,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    CARD_CORNER_RADIUS,
)
from src.db.repository import DatabaseRepository
from src.models.settings import DownloadHistory
from src.core.video_downloader import VideoDownloader

logger = logging.getLogger(__name__)


class VideoTab(ctk.CTkFrame):
    """Video Grab tab with URL input and download."""

    def __init__(self, parent: ctk.CTkFrame, app: ctk.CTk) -> None:
        """Initialize the Video tab.

        Args:
            parent: Parent widget.
            app: Main application instance.
        """
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.video_downloader = VideoDownloader()
        self.db = DatabaseRepository()
        self.current_video_info: dict | None = None
        self.downloaded_file_path: Path | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the Video tab UI with modern layout."""
        # Main container with padding
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header Section
        self.header = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 20))

        self.title_group = ctk.CTkFrame(self.header, fg_color="transparent")
        self.title_group.pack(side="left")

        self.title_label = ctk.CTkLabel(
            self.title_group,
            text="Video Grab",
            font=("Inter", 18, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.title_label.pack(fill="x")

        self.subtitle_label = ctk.CTkLabel(
            self.title_group,
            text="High-speed media extraction from 1000+ supported sites.",
            font=("Inter", 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.subtitle_label.pack(fill="x")

        # URL Input Area
        self.url_container = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.url_container.pack(fill="x", pady=(0, 20))

        self.url_frame = ctk.CTkFrame(self.url_container, fg_color="transparent")
        self.url_frame.pack(fill="x", padx=15, pady=15)

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Paste a video link (YouTube, Vimeo, X...)",
            font=("Inter", 12),
            height=36,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            border_color=COLOR_BORDER,
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.fetch_button = ctk.CTkButton(
            self.url_frame,
            text="Fetch Info",
            font=("Inter", 12, "bold"),
            height=36,
            width=100,
            fg_color=COLOR_ACCENT_PRIMARY,
            hover_color=COLOR_BG_HOVER,
            command=self._fetch_video_info,
        )
        self.fetch_button.pack(side="left")

        # Bento Grid for Info and History
        self.grid_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True)
        self.grid_container.grid_columnconfigure(0, weight=3)  # Left: Video Info
        self.grid_container.grid_columnconfigure(1, weight=2)  # Right: History
        self.grid_container.grid_rowconfigure(0, weight=1)

        # Left Column: Video Info & Download Options
        self.info_column = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.info_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Video Info Card
        self.info_card = ctk.CTkFrame(
            self.info_column,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.info_card.pack(fill="both", expand=True)

        # Placeholder when no info is fetched
        self.placeholder_label = ctk.CTkLabel(
            self.info_card,
            text="Enter a URL to fetch video details",
            font=("Inter", 12),
            text_color=COLOR_TEXT_MUTED,
        )
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        # Info content (hidden initially)
        self.info_content = ctk.CTkFrame(self.info_card, fg_color="transparent")
        
        self.video_title_label = ctk.CTkLabel(
            self.info_content,
            text="",
            font=("Inter", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
            wraplength=400,
            justify="left",
        )
        self.video_title_label.pack(padx=20, pady=(20, 5), anchor="w")

        self.video_duration_label = ctk.CTkLabel(
            self.info_content,
            text="",
            font=("Inter", 12),
            text_color=COLOR_TEXT_MUTED,
        )
        self.video_duration_label.pack(padx=20, pady=(0, 20), anchor="w")

        # Options in Info Card
        self.options_frame = ctk.CTkFrame(self.info_content, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=20, pady=10)

        self.quality_label = ctk.CTkLabel(
            self.options_frame, text="Target Quality", font=("Inter", 11, "bold"), text_color=COLOR_TEXT_SECONDARY
        )
        self.quality_label.pack(anchor="w", pady=(0, 5))

        self.quality_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=["Best", "4K", "1080p", "720p", "480p", "Audio Only"],
            font=("Inter", 12),
            height=32,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            button_color=COLOR_SURFACE_CONTAINER_HIGH,
            dropdown_hover_color=COLOR_BG_HOVER,
        )
        self.quality_menu.pack(fill="x")
        self.quality_menu.set("Best")

        self.download_button = ctk.CTkButton(
            self.info_content,
            text="Start Download",
            font=("Inter", 14, "bold"),
            height=45,
            fg_color=COLOR_ACCENT_SECONDARY,
            text_color="#002118",
            hover_color="#00b491",
            state="disabled",
            command=self._download_video,
        )
        self.download_button.pack(fill="x", padx=20, pady=20, side="bottom")

        # Progress bar (integrated at bottom of info card)
        self.progress_bar = ctk.CTkProgressBar(
            self.info_card,
            height=4,
            corner_radius=0,
            progress_color=COLOR_ACCENT_SECONDARY,
        )
        self.progress_bar.pack(fill="x", side="bottom")
        self.progress_bar.set(0)

        # Right Column: History
        self.history_column = ctk.CTkFrame(
            self.grid_container,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.history_column.grid(row=0, column=1, sticky="nsew")

        self.history_header = ctk.CTkFrame(
            self.history_column,
            fg_color=COLOR_SURFACE_CONTAINER_HIGH,
            height=36,
            corner_radius=0,
        )
        self.history_header.pack(fill="x")
        self.history_header.pack_propagate(False)

        self.history_title = ctk.CTkLabel(
            self.history_header,
            text="Download History",
            font=("Inter", 12, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.history_title.pack(side="left", padx=15)

        self.history_scrollable = ctk.CTkScrollableFrame(
            self.history_column,
            fg_color="transparent",
        )
        self.history_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        self._load_download_history()

    def _fetch_video_info(self) -> None:
        """Fetch video information from the URL."""
        url = self.url_entry.get().strip()
        if not url:
            self.app.show_toast("Please enter a video URL", is_error=True)
            return

        self.fetch_button.configure(state="disabled")
        self.app.set_status("Fetching video info...")

        try:
            info = self.video_downloader.get_video_info(url)
            self.current_video_info = info

            # Show video info
            self.video_title_label.configure(text=info["title"])
            duration = info.get("duration")
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                self.video_duration_label.configure(text=f"Duration: {minutes}:{seconds:02d}")
            else:
                self.video_duration_label.configure(text="Duration: Unknown")

            # Show info content, hide placeholder
            self.placeholder_label.place_forget()
            self.info_content.pack(fill="both", expand=True)

            # Enable download button
            self.download_button.configure(state="normal")

            self.app.set_status("Video info loaded")

        except Exception as e:
            logger.error(f"Failed to fetch video info: {e}")
            self.app.show_toast(f"Failed to fetch video info: {e}", is_error=True)
            self.info_content.pack_forget()
            self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
            self.download_button.configure(state="disabled")

        finally:
            self.fetch_button.configure(state="normal")

    def _download_video(self) -> None:
        """Download the video."""
        url = self.url_entry.get().strip()
        if not url or not self.current_video_info:
            return

        quality = self.quality_menu.get()
        resolution_map = {
            "Best": None,
            "4K": "2160p",
            "1080p": "1080p",
            "720p": "720p",
            "480p": "480p",
            "Audio Only": None,
        }
        resolution = resolution_map.get(quality)

        self.download_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.app.set_status("Downloading...")

        def progress_callback(progress_data: dict) -> None:
            """Update progress during download."""
            if progress_data["status"] == "downloading":
                downloaded = progress_data.get("downloaded_bytes", 0)
                total = progress_data.get("total_bytes", 1)
                percent = downloaded / total if total else 0
                self.progress_bar.set(percent)
                
                speed = progress_data.get("speed", 0)
                if speed:
                    speed_mb = speed / 1024 / 1024
                    self.app.set_status(f"Downloading... {speed_mb:.1f} MB/s")
            elif progress_data["status"] == "finished":
                self.progress_bar.set(1)

        def completion_callback(result: Path) -> None:
            """Handle download completion."""
            self.downloaded_file_path = result
            self.progress_bar.set(1)
            self.download_button.configure(state="normal")
            self.app.set_status(f"Done. Saved to {result}")
            self.app.show_toast("Download completed!")

            # Save to download history
            try:
                history_entry = DownloadHistory(
                    url=url,
                    title=self.current_video_info.get("title") if self.current_video_info else "Unknown",
                    format_id=resolution or "best",
                    resolution=resolution,
                    file_path=str(result),
                    status="completed",
                )
                self.db.add_download_history(history_entry)
                self._load_download_history()
            except Exception as e:
                logger.error(f"Failed to save download history: {e}")

        def error_callback(error: Exception) -> None:
            """Handle download error."""
            logger.error(f"Download failed: {error}")
            self.progress_bar.set(0)
            self.download_button.configure(state="normal")
            self.app.show_toast(f"Download failed: {error}", is_error=True)

        # Start async download
        self.video_downloader.download_async(
            url,
            resolution=resolution,
            progress_callback=progress_callback,
            completion_callback=completion_callback,
            error_callback=error_callback,
        )

    def _open_output_folder(self) -> None:
        """Open the output folder in the file manager."""
        import subprocess
        import sys

        output_dir = self.video_downloader.output_dir

        try:
            if sys.platform == "win32":
                subprocess.run(["explorer", str(output_dir)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(output_dir)])
            else:
                subprocess.run(["xdg-open", str(output_dir)])
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
            self.app.show_toast(f"Failed to open folder: {e}", is_error=True)

    def _load_download_history(self) -> None:
        """Load and display download history."""
        try:
            history = self.db.get_download_history(limit=20)
            self._display_history(history)
        except Exception as e:
            logger.error(f"Failed to load download history: {e}")

    def _display_history(self, history: list[DownloadHistory]) -> None:
        """Display download history in the scrollable frame.

        Args:
            history: List of DownloadHistory entries.
        """
        # Clear existing items
        for widget in self.history_scrollable.winfo_children():
            widget.destroy()

        if not history:
            no_history_label = ctk.CTkLabel(
                self.history_scrollable,
                text="No download history",
                font=("Inter", 12),
                text_color=COLOR_TEXT_MUTED,
            )
            no_history_label.pack(pady=20)
            return

        for entry in history:
            item_frame = ctk.CTkFrame(
                self.history_scrollable,
                fg_color=COLOR_BG_BASE,
                corner_radius=6,
            )
            item_frame.pack(fill="x", pady=(5, 0))

            # Title
            title_label = ctk.CTkLabel(
                item_frame,
                text=entry.title or "Unknown",
                font=("Inter", 12, "bold"),
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w",
            )
            title_label.pack(fill="x", padx=10, pady=(8, 2))

            # URL
            url_label = ctk.CTkLabel(
                item_frame,
                text=entry.url,
                font=("Inter", 10),
                text_color=COLOR_TEXT_MUTED,
                anchor="w",
            )
            url_label.pack(fill="x", padx=10, pady=(0, 2))

            # Metadata
            metadata_text = f"{entry.resolution or 'Unknown'} • {entry.format_id}"
            metadata_label = ctk.CTkLabel(
                item_frame,
                text=metadata_text,
                font=("Inter", 10),
                text_color=COLOR_TEXT_MUTED,
                anchor="w",
            )
            metadata_label.pack(fill="x", padx=10, pady=(0, 8))

            # Re-download button
            redownload_button = ctk.CTkButton(
                item_frame,
                text="Re-download",
                font=("Inter", 10),
                height=30,
                fg_color="transparent",
                border_color=COLOR_BORDER,
                border_width=1,
            )
            redownload_button.pack(side="right", padx=10, pady=(0, 8))
            redownload_button.configure(command=lambda e=entry: self._redownload(e))

    def _redownload(self, entry: DownloadHistory) -> None:
        """Re-download a video from history.

        Args:
            entry: DownloadHistory entry to re-download.
        """
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, entry.url)
        self._fetch_video_info()
