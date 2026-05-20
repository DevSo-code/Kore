"""CustomTkinter theme configuration for Kore.

This module defines the dark theme based on the design system in DESIGN.md.
"""

from __future__ import annotations

import customtkinter as ctk

from src.constants import (
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
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_SURFACE_CONTAINER,
    COLOR_SURFACE_CONTAINER_LOW,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_SURFACE_CONTAINER_HIGH,
    COLOR_SURFACE_CONTAINER_HIGHEST,
)


def setup_dark_theme() -> None:
    """Configure CustomTkinter with the Kore dark theme."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def resolve_color(color: str | tuple[str, str]) -> str:
    """Resolve a color token (string or tuple) to a hex string for the current appearance mode."""
    if isinstance(color, tuple):
        mode = ctk.get_appearance_mode().lower()
        return color[0] if mode == "light" else color[1]
    return color


def get_color(color_name: str) -> str:
    """Get a color token by name.

    Args:
        color_name: Name of the color token.

    Returns:
        Hex color string.
    """
    color_map = {
        "bg_base": COLOR_BG_BASE,
        "bg_surface": COLOR_BG_SURFACE,
        "bg_elevated": COLOR_BG_ELEVATED,
        "bg_hover": COLOR_BG_HOVER,
        "surface_container": COLOR_SURFACE_CONTAINER,
        "surface_container_low": COLOR_SURFACE_CONTAINER_LOW,
        "surface_container_lowest": COLOR_SURFACE_CONTAINER_LOWEST,
        "surface_container_high": COLOR_SURFACE_CONTAINER_HIGH,
        "surface_container_highest": COLOR_SURFACE_CONTAINER_HIGHEST,
        "border": COLOR_BORDER,
        "border_focus": COLOR_BORDER_FOCUS,
        "accent_primary": COLOR_ACCENT_PRIMARY,
        "accent_secondary": COLOR_ACCENT_SECONDARY,
        "accent_danger": COLOR_ACCENT_DANGER,
        "accent_warning": COLOR_ACCENT_WARNING,
        "text_primary": COLOR_TEXT_PRIMARY,
        "text_secondary": COLOR_TEXT_SECONDARY,
        "text_muted": COLOR_TEXT_MUTED,
    }
    raw_color = color_map.get(color_name, COLOR_TEXT_PRIMARY)
    return resolve_color(raw_color)
