"""Main application shell with sidebar navigation.

This module contains the root window controller and tab management.
"""

from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path
from typing import Any

import customtkinter as ctk

from src.constants import (
    APP_NAME,
    APP_VERSION,
    COLOR_ACCENT_DANGER,
    COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_SECONDARY,
    COLOR_ACCENT_WARNING,
    COLOR_BG_BASE,
    COLOR_BG_ELEVATED,
    COLOR_BG_HOVER,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_BORDER_FOCUS,
    COLOR_SURFACE_CONTAINER,
    COLOR_SURFACE_CONTAINER_HIGH,
    COLOR_SURFACE_CONTAINER_HIGHEST,
    COLOR_SURFACE_CONTAINER_LOW,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    SIDEBAR_WIDTH,
    STATUS_BAR_HEIGHT,
)
from src.db.repository import DatabaseRepository
from src.models.settings import AppSettings, Tab
from src.ui.theme import setup_dark_theme

logger = logging.getLogger(__name__)


class App(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__()

        # Setup theme
        setup_dark_theme()

        # Window configuration
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{MIN_WINDOW_WIDTH}x{MIN_WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.configure(fg_color=COLOR_BG_BASE)

        # Load settings
        self.db = DatabaseRepository()
        self.settings = self.db.get_app_settings()

        # Build UI
        self._build_ui()

        # Load last active tab
        self._switch_to_tab(self.settings.last_active_tab)

        # Bind keyboard shortcuts
        self._bind_keyboard_shortcuts()

        # Check for updates
        self._check_for_updates()

    def _build_ui(self) -> None:
        """Build the main UI layout."""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=COLOR_BG_BASE, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=SIDEBAR_WIDTH,
            fg_color=COLOR_SURFACE_CONTAINER_LOW,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Sidebar title section
        self.sidebar_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_header.pack(fill="x", padx=20, pady=(30, 40))

        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_header,
            text=APP_NAME,
            font=("Inter", 24, "bold"),
            text_color=COLOR_ACCENT_PRIMARY,
            anchor="w",
        )
        self.sidebar_title.pack(fill="x")

        self.sidebar_subtitle = ctk.CTkLabel(
            self.sidebar_header,
            text="Utility Suite",
            font=("Inter", 11),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.sidebar_subtitle.pack(fill="x")

        # Navigation buttons container
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=10)

        # Navigation buttons
        self.nav_buttons: dict[Tab, ctk.CTkButton] = {}
        self._create_nav_buttons()

        # Content area
        self.content_area = ctk.CTkFrame(
            self.main_container,
            fg_color=COLOR_BG_BASE,
            corner_radius=0,
        )
        self.content_area.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        # Tab frames
        self.tab_frames: dict[Tab, ctk.CTkFrame] = {}
        self._create_tab_frames()

        # Status bar
        self.status_bar = ctk.CTkFrame(
            self,
            height=STATUS_BAR_HEIGHT,
            fg_color=COLOR_SURFACE_CONTAINER_LOWEST,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=0,
        )
        self.status_bar.pack(side="bottom", fill="x")
        self.status_bar.pack_propagate(False)

        # Status content
        self.status_left = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        self.status_left.pack(side="left", padx=10, fill="y")

        self.status_indicator = ctk.CTkFrame(
            self.status_left, width=8, height=8, corner_radius=4, fg_color=COLOR_ACCENT_SECONDARY
        )
        self.status_indicator.pack(side="left", padx=(0, 8), pady=10)

        self.status_label = ctk.CTkLabel(
            self.status_left,
            text="System Ready",
            font=("Inter", 10),
            text_color=COLOR_TEXT_MUTED,
        )
        self.status_label.pack(side="left")

        # GPU Info in status bar
        self.gpu_label = ctk.CTkLabel(
            self.status_bar,
            text="GPU: Checking...",
            font=("Inter", 10),
            text_color=COLOR_TEXT_MUTED,
        )
        self.gpu_label.pack(side="left", padx=20)

        self.version_label = ctk.CTkLabel(
            self.status_bar,
            text=f"Kore v{APP_VERSION}",
            font=("Inter", 10),
            text_color=COLOR_TEXT_MUTED,
            anchor="e",
        )
        self.version_label.pack(side="right", padx=10)

    def _create_nav_buttons(self) -> None:
        """Create navigation buttons in sidebar."""
        nav_items = [
            (Tab.IMAGE, "Image", "🖼"),
            (Tab.VIDEO, "Video", "📹"),
            (Tab.SETTINGS, "Settings", "⚙"),
        ]

        for tab, label, icon in nav_items:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"  {icon}   {label}",
                font=("Inter", 13, "bold" if tab == Tab.IMAGE else "normal"),
                fg_color="transparent",
                hover_color=COLOR_BG_HOVER,
                text_color=COLOR_TEXT_SECONDARY,
                anchor="w",
                height=40,
                corner_radius=8,
            )
            btn.pack(fill="x", padx=5, pady=2)
            btn.configure(command=lambda t=tab: self._switch_to_tab(t))
            self.nav_buttons[tab] = btn

    def _create_tab_frames(self) -> None:
        """Create tab content frames."""
        for tab in Tab:
            frame = ctk.CTkFrame(
                self.content_area,
                fg_color=COLOR_BG_BASE,
            )
            self.tab_frames[tab] = frame

    def _switch_to_tab(self, tab: Tab) -> None:
        """Switch to the specified tab.

        Args:
            tab: Tab to switch to.
        """
        # Hide all tabs
        for frame in self.tab_frames.values():
            frame.pack_forget()

        # Reset all nav buttons
        for btn in self.nav_buttons.values():
            btn.configure(
                fg_color="transparent",
                text_color=COLOR_TEXT_SECONDARY,
            )

        # Show selected tab
        self.tab_frames[tab].pack(fill="both", expand=True, padx=10, pady=10)

        # Highlight selected nav button
        self.nav_buttons[tab].configure(
            fg_color=COLOR_BG_SURFACE,
            text_color=COLOR_TEXT_PRIMARY,
        )

        # Update settings
        self.settings.last_active_tab = tab
        self.db.save_app_settings(self.settings)

        # Load tab content
        self._load_tab_content(tab)

    def _load_tab_content(self, tab: Tab) -> None:
        """Load content for the specified tab.

        Args:
            tab: Tab to load content for.
        """
        # Clear existing content
        for widget in self.tab_frames[tab].winfo_children():
            widget.destroy()

        # Import and load tab content
        if tab == Tab.IMAGE:
            from src.ui.tabs.image_tab import ImageTab

            image_tab = ImageTab(self.tab_frames[tab], self)
            image_tab.pack(fill="both", expand=True)

        elif tab == Tab.VIDEO:
            from src.ui.tabs.video_tab import VideoTab

            video_tab = VideoTab(self.tab_frames[tab], self)
            video_tab.pack(fill="both", expand=True)

        elif tab == Tab.SETTINGS:
            from src.ui.tabs.settings_tab import SettingsTab

            settings_tab = SettingsTab(self.tab_frames[tab], self)
            settings_tab.pack(fill="both", expand=True)

    def set_status(self, message: str) -> None:
        """Update the status bar message.

        Args:
            message: Status message to display.
        """
        self.status_label.configure(text=message)

    def show_toast(self, message: str, is_error: bool = False) -> None:
        """Show a toast notification.

        Args:
            message: Message to display.
            is_error: Whether this is an error message.
        """
        # Create toast frame
        toast_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_SURFACE,
            border_color=COLOR_ACCENT_DANGER if is_error else COLOR_ACCENT_SECONDARY,
            border_width=2,
            corner_radius=8,
        )
        toast_frame.place(relx=0.98, rely=0.95, anchor="se", x=-10, y=-10)

        toast_label = ctk.CTkLabel(
            toast_frame,
            text=message,
            font=("Inter", 12),
            text_color=COLOR_TEXT_PRIMARY,
            wraplength=300,
        )
        toast_label.pack(padx=15, pady=10)

        # Auto-dismiss after 4 seconds
        self.after(4000, toast_frame.destroy)

        # Also update status bar
        self.set_status(message)

    def _bind_keyboard_shortcuts(self) -> None:
        """Bind keyboard shortcuts for quick navigation."""
        self.bind("<Control-1>", lambda e: self._switch_to_tab(Tab.IMAGE))
        self.bind("<Control-2>", lambda e: self._switch_to_tab(Tab.VIDEO))
        self.bind("<Control-3>", lambda e: self._switch_to_tab(Tab.SETTINGS))

    def _check_for_updates(self) -> None:
        """Check for application updates in the background."""
        from src.core.update_checker import UpdateChecker

        def check() -> None:
            try:
                checker = UpdateChecker()
                update_info = checker.check_for_updates()
                if update_info:
                    self.after(0, lambda: self._show_update_notification(update_info))
            except Exception as e:
                logger.error(f"Failed to check for updates: {e}")

        import threading

        thread = threading.Thread(target=check, daemon=True)
        thread.start()

    def _show_update_notification(self, update_info: dict[str, Any]) -> None:
        """Show update notification to user.

        Args:
            update_info: Update information dictionary.
        """
        message = f"Update available: v{update_info['latest_version']}"
        self.show_toast(message, is_error=False)
