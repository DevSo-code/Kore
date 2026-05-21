"""Spotify download service using spotDL.

This module wraps spotDL for downloading Spotify tracks from YouTube
with full metadata embedding.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Any, Callable

from src.constants import OUTPUT_DIR
from src.utils.decorators import retry_on_failure

logger = logging.getLogger(__name__)


class SpotifyDownloader:
    """Service for downloading Spotify tracks using spotDL."""

    def __init__(self, output_dir: str | Path = OUTPUT_DIR) -> None:
        """Initialize the Spotify downloader.

        Args:
            output_dir: Directory to save downloaded tracks.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _validate_dependencies(self) -> None:
        """Validate that required dependencies are installed."""
        required_commands = ["ffmpeg", "spotdl"]
        for cmd in required_commands:
            if shutil.which(cmd) is None:
                raise RuntimeError(f"{cmd} is not installed or not in PATH")

        # Check for yt-dlp (used internally by spotdl)
        try:
            import yt_dlp
            # Try to get version, but handle different version attribute names
            try:
                version = yt_dlp.__version__
            except AttributeError:
                version = "unknown"
            logger.info(f"yt-dlp version: {version}")
        except ImportError:
            logger.warning("yt-dlp not found, spotdl may not work properly")


    def download_track(
        self,
        url_or_query: str,
        audio_format: str = "mp3",
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> dict[str, Any]:
        """Download a single track from Spotify URL or search query.

        Args:
            url_or_query: Spotify URL or search query.
            audio_format: Audio format (mp3, m4a, opus).
            progress_callback: Optional callback for progress updates.

        Returns:
            Dictionary with download result.

        Raises:
            Exception: If download fails.
        """
        try:
            self._validate_dependencies()
            
            if progress_callback:
                progress_callback(10, "Fetching metadata from Spotify...")

            # Use subprocess to call spotdl with YouTube provider
            cmd = [
                "spotdl",
                "download",
                url_or_query,
                "--audio", "youtube",  # Use YouTube instead of YouTube Music
                "--format", audio_format,
                "--output", str(self.output_dir / "{artists} - {title}.{output-ext}"),
                "--overwrite", "skip",
            ]

            if progress_callback:
                progress_callback(30, "Searching YouTube and downloading...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,  # 10 minute timeout for better reliability
            )

            if result.returncode != 0:
                error_output = result.stderr if result.stderr else result.stdout
                if "No results found" in error_output or "LookupError" in error_output:
                    logger.warning(f"No results found for: {url_or_query}")
                    return {"success": False, "error": "No matching audio found on YouTube. Try a different track or search query."}
                logger.error(f"spotdl failed: {error_output}")
                # Return a user-friendly error message without exposing internals
                return {"success": False, "error": "Download failed. Please check your connection and try again."}

            if progress_callback:
                progress_callback(100, "Complete!")

            # Scan output directory for the most recently downloaded file
            # This is more reliable than parsing stdout
            downloaded_files = list(self.output_dir.glob(f"*.{audio_format}"))
            if downloaded_files:
                # Get the most recently modified file
                file_path = max(downloaded_files, key=lambda p: p.stat().st_mtime)
                return {
                    "success": True,
                    "file_path": str(file_path),
                    "metadata": {},
                }
            else:
                return {
                    "success": True,
                    "file_path": str(self.output_dir),
                    "metadata": {},
                }

        except subprocess.TimeoutExpired:
            logger.error("Download timed out")
            return {"success": False, "error": "Download timed out. Please try again."}
        except RuntimeError as e:
            # Dependency validation error
            logger.error(f"Dependency error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return {"success": False, "error": "Download failed. Please try again."}

    def download_playlist(
        self,
        spotify_url: str,
        audio_format: str = "mp3",
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> list[dict[str, Any]]:
        """Download entire Spotify playlist.

        Args:
            spotify_url: Spotify playlist URL.
            audio_format: Audio format (mp3, m4a, opus).
            progress_callback: Optional callback for progress updates.

        Returns:
            List of download results for each track.
        """
        try:
            self._validate_dependencies()
            
            if progress_callback:
                progress_callback(5, "Fetching playlist...")

            # Use subprocess to download playlist
            cmd = [
                "spotdl",
                "download",
                spotify_url,
                "--audio", "youtube",
                "--format", audio_format,
                "--output", str(self.output_dir / "{artists} - {title}.{output-ext}"),
                "--overwrite", "skip",
            ]

            if progress_callback:
                progress_callback(10, "Starting playlist download...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=1800,  # 30 minute timeout for playlists
            )

            if result.returncode != 0:
                error_output = result.stderr if result.stderr else result.stdout
                logger.error(f"Playlist download failed: {error_output}")
                return [{"track_name": "Playlist", "success": False, "error": "Playlist download failed. Please try again."}]

            if progress_callback:
                progress_callback(100, "Playlist download complete!")

            # Return success since spotdl handles the entire playlist
            return [{"track_name": "Playlist", "success": True, "file_path": str(self.output_dir)}]

        except subprocess.TimeoutExpired:
            logger.error("Playlist download timed out")
            return [{"track_name": "Playlist", "success": False, "error": "Download timed out. Please try again."}]
        except RuntimeError as e:
            logger.error(f"Dependency error: {e}")
            return [{"track_name": "Playlist", "success": False, "error": str(e)}]
        except Exception as e:
            logger.error(f"Playlist download failed: {e}")
            return [{"track_name": "Playlist", "success": False, "error": "Playlist download failed. Please try again."}]

    def download_track_async(
        self,
        url_or_query: str,
        audio_format: str = "mp3",
        progress_callback: Callable[[int, str], None] | None = None,
        completion_callback: Callable[[dict[str, Any]], None] | None = None,
        error_callback: Callable[[Exception], None] | None = None,
    ) -> threading.Thread:
        """Download a track in a background thread.

        Args:
            url_or_query: Spotify URL or search query.
            audio_format: Audio format (mp3, m4a, opus).
            progress_callback: Optional callback for progress updates.
            completion_callback: Optional callback when download completes.
            error_callback: Optional callback if download fails.

        Returns:
            Thread object for the background task.
        """
        def _task() -> None:
            try:
                result = self.download_track(url_or_query, audio_format, progress_callback)
                if completion_callback:
                    completion_callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)

        thread = threading.Thread(target=_task, daemon=True)
        thread.start()
        return thread

    def download_playlist_async(
        self,
        spotify_url: str,
        audio_format: str = "mp3",
        progress_callback: Callable[[int, str], None] | None = None,
        completion_callback: Callable[[list[dict[str, Any]]], None] | None = None,
        error_callback: Callable[[Exception], None] | None = None,
    ) -> threading.Thread:
        """Download a playlist in a background thread.

        Args:
            spotify_url: Spotify playlist URL.
            audio_format: Audio format (mp3, m4a, opus).
            progress_callback: Optional callback for progress updates.
            completion_callback: Optional callback when download completes.
            error_callback: Optional callback if download fails.

        Returns:
            Thread object for the background task.
        """
        def _task() -> None:
            try:
                result = self.download_playlist(spotify_url, audio_format, progress_callback)
                if completion_callback:
                    completion_callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)

        thread = threading.Thread(target=_task, daemon=True)
        thread.start()
        return thread
