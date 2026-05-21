"""Spotify Downloader tab for Spotify track downloading.

This module contains the UI and logic for the Spotify download feature.
"""

from __future__ import annotations

import logging
import subprocess
import sys
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
from src.core.spotify_downloader import SpotifyDownloader

logger = logging.getLogger(__name__)


class SpotifyTab(ctk.CTkFrame):
    """Spotify Downloader tab with URL input and download."""

    def __init__(self, parent: ctk.CTkFrame, app: ctk.CTk) -> None:
        """Initialize the Spotify tab.

        Args:
            parent: Parent widget.
            app: Main application instance.
        """
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.spotify_downloader = SpotifyDownloader()
        self.db = DatabaseRepository()
        self.current_track_info: dict | None = None
        self.downloaded_file_path: Path | None = None
        self.download_history: list[dict] = []

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the Spotify tab UI with modern layout."""
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
            text="Spotify Downloader",
            font=("Inter", 18, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.title_label.pack(fill="x")

        self.subtitle_label = ctk.CTkLabel(
            self.title_group,
            text="Download audio from YouTube with Spotify metadata.",
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
            placeholder_text="Spotify URL or search query (e.g., 'Artist - Song Name')",
            font=("Inter", 12),
            height=36,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            border_color=COLOR_BORDER,
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Download Type and Format Row
        self.options_row = ctk.CTkFrame(self.container, fg_color="transparent")
        self.options_row.pack(fill="x", pady=(0, 20))

        # Download Type
        self.type_frame = ctk.CTkFrame(self.options_row, fg_color="transparent")
        self.type_frame.pack(side="left", padx=(0, 20))

        self.type_label = ctk.CTkLabel(
            self.type_frame,
            text="Download Type",
            font=("Inter", 11, "bold"),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.type_label.pack(anchor="w", pady=(0, 5))

        self.download_type = ctk.CTkSegmentedButton(
            self.type_frame,
            values=["Track", "Playlist", "Search"],
            font=("Inter", 11),
            height=32,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            selected_color=COLOR_ACCENT_PRIMARY,
            selected_hover_color=COLOR_BG_HOVER,
            unselected_color=COLOR_SURFACE_CONTAINER_LOW,
            unselected_hover_color=COLOR_BG_HOVER,
        )
        self.download_type.pack(fill="x")
        self.download_type.set("Track")

        # Format Selector
        self.format_frame = ctk.CTkFrame(self.options_row, fg_color="transparent")
        self.format_frame.pack(side="left", fill="x", expand=True)

        self.format_label = ctk.CTkLabel(
            self.format_frame,
            text="Audio Format",
            font=("Inter", 11, "bold"),
            text_color=COLOR_TEXT_SECONDARY,
        )
        self.format_label.pack(anchor="w", pady=(0, 5))

        self.format_menu = ctk.CTkOptionMenu(
            self.format_frame,
            values=["MP3 (320 kbps)", "M4A (higher quality)", "OPUS (best quality)"],
            font=("Inter", 12),
            height=32,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            button_color=COLOR_SURFACE_CONTAINER_HIGH,
            dropdown_hover_color=COLOR_BG_HOVER,
        )
        self.format_menu.pack(fill="x")
        self.format_menu.set("MP3 (320 kbps)")

        # Download Button
        self.download_button = ctk.CTkButton(
            self.options_row,
            text="Download",
            font=("Inter", 13, "bold"),
            height=36,
            width=120,
            fg_color=COLOR_ACCENT_SECONDARY,
            text_color="#002118",
            hover_color="#00b491",
            command=self._start_download,
        )
        self.download_button.pack(side="right")

        # Progress Section
        self.progress_container = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.progress_container.pack(fill="x", pady=(0, 20))

        self.progress_frame = ctk.CTkFrame(self.progress_container, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=15, pady=15)

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=6,
            corner_radius=3,
            progress_color=COLOR_ACCENT_SECONDARY,
        )
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=("Inter", 11),
            text_color=COLOR_TEXT_MUTED,
        )
        self.status_label.pack(anchor="w")

        # Download History Section
        self.history_container = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.history_container.pack(fill="both", expand=True)

        self.history_header = ctk.CTkFrame(
            self.history_container,
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
            self.history_container,
            fg_color="transparent",
        )
        self.history_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

    def _start_download(self) -> None:
        """Start the download process."""
        url_or_query = self.url_entry.get().strip()
        if not url_or_query:
            self.app.show_toast("Please enter a Spotify URL or search query", is_error=True)
            return

        download_type = self.download_type.get()
        format_choice = self.format_menu.get()
        audio_format_map = {
            "MP3 (320 kbps)": "mp3",
            "M4A (higher quality)": "m4a",
            "OPUS (best quality)": "opus",
        }
        audio_format = audio_format_map.get(format_choice, "mp3")

        self.download_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.app.set_status("Starting download...")

        def progress_callback(percent: int, message: str) -> None:
            """Update progress during download using thread-safe approach."""
            # Use after() to schedule UI updates on the main thread
            def _update_ui() -> None:
                if self.progress_bar.winfo_exists():
                    self.progress_bar.set(percent / 100)
                if self.status_label.winfo_exists():
                    self.status_label.configure(text=message)
                self.app.update()

            self.app.after(0, _update_ui)

        def completion_callback(result: dict) -> None:
            """Handle download completion using thread-safe approach."""
            def _update_ui() -> None:
                if self.progress_bar.winfo_exists():
                    self.progress_bar.set(1)
                if self.download_button.winfo_exists():
                    self.download_button.configure(state="normal")

                if result.get("success"):
                    metadata = result.get("metadata", {})
                    title = metadata.get("title", "Unknown")
                    artist = metadata.get("artist", "Unknown")
                    if self.status_label.winfo_exists():
                        self.status_label.configure(text=f"✓ Downloaded: {artist} - {title}")
                    self.app.set_status(f"Downloaded: {artist} - {title}")
                    self.app.show_toast(f"Downloaded: {artist} - {title}")

                    # Add to download history
                    self.download_history.insert(0, {
                        "title": title,
                        "artist": artist,
                        "file_path": result.get("file_path"),
                        "format": audio_format,
                    })
                    if self.history_scrollable.winfo_exists():
                        self._display_history()
                else:
                    error = result.get("error", "Unknown error")
                    if self.status_label.winfo_exists():
                        self.status_label.configure(text=f"✗ Error: {error}")
                    self.app.show_toast(f"Download failed: {error}", is_error=True)

            self.app.after(0, _update_ui)

        def error_callback(error: Exception) -> None:
            """Handle download error using thread-safe approach."""
            logger.error(f"Download failed: {error}")

            def _update_ui() -> None:
                if self.progress_bar.winfo_exists():
                    self.progress_bar.set(0)
                if self.download_button.winfo_exists():
                    self.download_button.configure(state="normal")
                if self.status_label.winfo_exists():
                    self.status_label.configure(text=f"✗ Error: {str(error)}")
                self.app.show_toast(f"Download failed: {error}", is_error=True)

            self.app.after(0, _update_ui)

        # Start async download based on type
        if download_type == "Track":
            self.spotify_downloader.download_track_async(
                url_or_query,
                audio_format=audio_format,
                progress_callback=progress_callback,
                completion_callback=completion_callback,
                error_callback=error_callback,
            )
        elif download_type == "Playlist":
            def playlist_completion(results: list) -> None:
                """Handle playlist download completion using thread-safe approach."""
                successful = sum(1 for r in results if r.get("success"))
                total = len(results)

                def _update_ui() -> None:
                    if self.progress_bar.winfo_exists():
                        self.progress_bar.set(1)
                    if self.download_button.winfo_exists():
                        self.download_button.configure(state="normal")
                    if self.status_label.winfo_exists():
                        self.status_label.configure(text=f"✓ Downloaded {successful}/{total} tracks")
                    self.app.show_toast(f"Playlist download complete: {successful}/{total} tracks")

                    # Add successful downloads to history
                    for result in results:
                        if result.get("success"):
                            self.download_history.insert(0, {
                                "title": result.get("track_name", "Unknown"),
                                "artist": "Playlist",
                                "file_path": result.get("file_path"),
                                "format": audio_format,
                            })
                    if self.history_scrollable.winfo_exists():
                        self._display_history()

                self.app.after(0, _update_ui)

            self.spotify_downloader.download_playlist_async(
                url_or_query,
                audio_format=audio_format,
                progress_callback=progress_callback,
                completion_callback=playlist_completion,
                error_callback=error_callback,
            )
        else:  # Search
            self.spotify_downloader.download_track_async(
                url_or_query,
                audio_format=audio_format,
                progress_callback=progress_callback,
                completion_callback=completion_callback,
                error_callback=error_callback,
            )

    def _open_output_folder(self) -> None:
        """Open the output folder in the file manager."""
        output_dir = self.spotify_downloader.output_dir

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

    def _display_history(self) -> None:
        """Display download history in the scrollable frame."""
        # Clear existing items
        for widget in self.history_scrollable.winfo_children():
            widget.destroy()

        if not self.download_history:
            no_history_label = ctk.CTkLabel(
                self.history_scrollable,
                text="No download history",
                font=("Inter", 12),
                text_color=COLOR_TEXT_MUTED,
            )
            no_history_label.pack(pady=20)
            return

        for entry in self.download_history[:20]:  # Show last 20
            item_frame = ctk.CTkFrame(
                self.history_scrollable,
                fg_color=COLOR_BG_BASE,
                corner_radius=6,
            )
            item_frame.pack(fill="x", pady=(5, 0))

            # Title and Artist
            title_label = ctk.CTkLabel(
                item_frame,
                text=f"{entry.get('artist', 'Unknown')} - {entry.get('title', 'Unknown')}",
                font=("Inter", 12, "bold"),
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w",
            )
            title_label.pack(fill="x", padx=10, pady=(8, 2))

            # Format
            format_label = ctk.CTkLabel(
                item_frame,
                text=f"Format: {entry.get('format', 'Unknown').upper()}",
                font=("Inter", 10),
                text_color=COLOR_TEXT_MUTED,
                anchor="w",
            )
            format_label.pack(fill="x", padx=10, pady=(0, 8))

            # Open folder button
            open_button = ctk.CTkButton(
                item_frame,
                text="Open Folder",
                font=("Inter", 10),
                height=28,
                width=90,
                fg_color="transparent",
                border_color=COLOR_BORDER,
                border_width=1,
            )
            open_button.pack(side="right", padx=10, pady=(0, 8))
            open_button.configure(command=self._open_output_folder)
