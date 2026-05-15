"""Settings tab for application configuration.

This module contains the UI and logic for the settings feature.
"""

from __future__ import annotations

import logging
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from src.constants import (
    CARD_CORNER_RADIUS,
    COLOR_ACCENT_PRIMARY,
    COLOR_BG_HOVER,
    COLOR_BORDER,
    COLOR_SURFACE_CONTAINER,
    COLOR_SURFACE_CONTAINER_HIGH,
    COLOR_SURFACE_CONTAINER_LOW,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)
from src.db.repository import DatabaseRepository
from src.models.settings import AppSettings

logger = logging.getLogger(__name__)


class SettingsTab(ctk.CTkFrame):
    """Settings tab for application configuration."""

    def __init__(self, parent: ctk.CTkFrame, app: ctk.CTk) -> None:
        """Initialize the Settings tab.

        Args:
            parent: Parent widget.
            app: Main application instance.
        """
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.db = DatabaseRepository()
        self.settings = self.db.get_app_settings()

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the Settings tab UI with modern aesthetic."""
        # Main container with padding
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header Section
        self.header = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 30))

        self.title_group = ctk.CTkFrame(self.header, fg_color="transparent")
        self.title_group.pack(side="left")

        self.title_label = ctk.CTkLabel(
            self.title_group,
            text="Settings",
            font=("Inter", 18, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.title_label.pack(fill="x")

        self.subtitle_label = ctk.CTkLabel(
            self.title_group,
            text="Configure application behavior and system preferences.",
            font=("Inter", 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.subtitle_label.pack(fill="x")

        # Settings Cards
        self.scroll_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        # Output Directory Card
        self.dir_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.dir_card.pack(fill="x", pady=(0, 15))

        self.dir_title = ctk.CTkLabel(
            self.dir_card, text="Storage & Paths", font=("Inter", 13, "bold"), text_color=COLOR_TEXT_PRIMARY
        )
        self.dir_title.pack(padx=20, pady=(20, 5), anchor="w")

        self.dir_desc = ctk.CTkLabel(
            self.dir_card, text="Default location for saved files", font=("Inter", 11), text_color=COLOR_TEXT_MUTED
        )
        self.dir_desc.pack(padx=20, pady=(0, 15), anchor="w")

        self.dir_input_frame = ctk.CTkFrame(self.dir_card, fg_color="transparent")
        self.dir_input_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.output_dir_entry = ctk.CTkEntry(
            self.dir_input_frame,
            placeholder_text=self.settings.default_output_dir,
            font=("Inter", 12),
            height=36,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            border_color=COLOR_BORDER,
        )
        self.output_dir_entry.insert(0, self.settings.default_output_dir)
        self.output_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_button = ctk.CTkButton(
            self.dir_input_frame,
            text="Browse",
            font=("Inter", 12),
            height=36,
            width=80,
            fg_color=COLOR_SURFACE_CONTAINER_HIGH,
            hover_color=COLOR_BG_HOVER,
            command=self._browse_output_dir,
        )
        self.browse_button.pack(side="right")

        # Performance Card
        self.perf_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.perf_card.pack(fill="x", pady=(0, 15))

        self.perf_title = ctk.CTkLabel(
            self.perf_card, text="Performance", font=("Inter", 13, "bold"), text_color=COLOR_TEXT_PRIMARY
        )
        self.perf_title.pack(padx=20, pady=(20, 5), anchor="w")

        self.gpu_frame = ctk.CTkFrame(self.perf_card, fg_color="transparent")
        self.gpu_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.gpu_label_group = ctk.CTkFrame(self.gpu_frame, fg_color="transparent")
        self.gpu_label_group.pack(side="left")

        self.gpu_label = ctk.CTkLabel(
            self.gpu_label_group, text="GPU Acceleration", font=("Inter", 12), text_color=COLOR_TEXT_PRIMARY
        )
        self.gpu_label.pack(anchor="w")

        self.gpu_desc = ctk.CTkLabel(
            self.gpu_label_group, text="Use GPU for faster processing", font=("Inter", 11), text_color=COLOR_TEXT_MUTED
        )
        self.gpu_desc.pack(anchor="w")

        self.gpu_switch = ctk.CTkSwitch(
            self.gpu_frame,
            text="",
            width=40,
            progress_color=COLOR_ACCENT_PRIMARY,
        )
        self.gpu_switch.pack(side="right")
        if self.settings.gpu_acceleration:
            self.gpu_switch.select()

        # Appearance Card
        self.app_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.app_card.pack(fill="x", pady=(0, 15))

        self.app_title = ctk.CTkLabel(
            self.app_card, text="Appearance", font=("Inter", 13, "bold"), text_color=COLOR_TEXT_PRIMARY
        )
        self.app_title.pack(padx=20, pady=(20, 5), anchor="w")

        self.theme_frame = ctk.CTkFrame(self.app_card, fg_color="transparent")
        self.theme_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.theme_label = ctk.CTkLabel(
            self.theme_frame, text="Application Theme", font=("Inter", 12), text_color=COLOR_TEXT_PRIMARY
        )
        self.theme_label.pack(side="left")

        self.theme_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            values=["Dark", "Light"],
            font=("Inter", 12),
            height=32,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            button_color=COLOR_SURFACE_CONTAINER_HIGH,
            dropdown_hover_color=COLOR_BG_HOVER,
        )
        self.theme_menu.pack(side="right")
        self.theme_menu.set(self.settings.theme.value.capitalize())

        # Save Button
        self.save_settings_button = ctk.CTkButton(
            self.container,
            text="Save Changes",
            font=("Inter", 14, "bold"),
            height=45,
            fg_color=COLOR_ACCENT_PRIMARY,
            hover_color=COLOR_BG_HOVER,
            command=self._save_settings,
        )
        self.save_settings_button.pack(fill="x", side="bottom")

    def _browse_output_dir(self) -> None:
        """Open file browser to select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_entry.delete(0, "end")
            self.output_dir_entry.insert(0, directory)

    def _toggle_gpu(self) -> None:
        """Toggle GPU acceleration setting."""
        self.settings.gpu_acceleration = self.gpu_switch.get()

    def _change_theme(self, choice: str) -> None:
        """Change theme setting.

        Args:
            choice: Selected theme.
        """
        self.settings.theme = choice.lower()

    def _save_settings(self) -> None:
        """Save all settings."""
        self.settings.default_output_dir = self.output_dir_entry.get()
        self.settings.gpu_acceleration = self.gpu_switch.get()
        self.settings.theme = self.theme_menu.get().lower()

        try:
            self.db.save_app_settings(self.settings)
            self.app.set_status("Settings saved")
            self.app.show_toast("Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            self.app.show_toast(f"Failed to save settings: {e}", is_error=True)
