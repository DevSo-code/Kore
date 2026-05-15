"""Update checker service for GitHub releases.

This module checks for updates via GitHub releases API.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from src.constants import APP_NAME, APP_VERSION

logger = logging.getLogger(__name__)


class UpdateChecker:
    """Service for checking application updates."""

    def __init__(self, repo_owner: str = "yourusername", repo_name: str = "kore") -> None:
        """Initialize the update checker.

        Args:
            repo_owner: GitHub repository owner.
            repo_name: GitHub repository name.
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    def check_for_updates(self) -> dict[str, Any] | None:
        """Check for available updates.

        Returns:
            Dictionary with update info if update available, None otherwise.
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()

            release_data = response.json()
            latest_version = release_data.get("tag_name", "").lstrip("v")

            if self._is_newer_version(latest_version, APP_VERSION):
                return {
                    "current_version": APP_VERSION,
                    "latest_version": latest_version,
                    "release_url": release_data.get("html_url"),
                    "release_notes": release_data.get("body"),
                    "download_url": self._get_download_url(release_data),
                }

            return None

        except requests.RequestException as e:
            logger.error(f"Failed to check for updates: {e}")
            return None

    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Check if latest version is newer than current.

        Args:
            latest: Latest version string.
            current: Current version string.

        Returns:
            True if latest is newer, False otherwise.
        """
        try:
            latest_parts = [int(x) for x in latest.split(".")]
            current_parts = [int(x) for x in current.split(".")]

            return latest_parts > current_parts
        except (ValueError, AttributeError):
            return False

    def _get_download_url(self, release_data: dict[str, Any]) -> str | None:
        """Get download URL for the current platform.

        Args:
            release_data: GitHub release data.

        Returns:
            Download URL or None.
        """
        import sys

        assets = release_data.get("assets", [])
        platform = sys.platform

        for asset in assets:
            name = asset.get("name", "").lower()
            if platform == "win32" and "exe" in name:
                return asset.get("browser_download_url")
            elif platform == "linux" and ("appimage" in name or "tar.gz" in name):
                return asset.get("browser_download_url")
            elif platform == "darwin" and "dmg" in name:
                return asset.get("browser_download_url")

        return None
