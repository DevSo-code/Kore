"""Video download service using yt-dlp.

This module wraps yt-dlp for video downloading with format parsing,
progress hooks, and download management.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Callable

import yt_dlp

from src.constants import OUTPUT_DIR

logger = logging.getLogger(__name__)


class VideoDownloader:
    """Service for downloading videos using yt-dlp."""

    def __init__(self, output_dir: str | Path = OUTPUT_DIR) -> None:
        """Initialize the video downloader.

        Args:
            output_dir: Directory to save downloaded videos.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_video_info(self, url: str) -> dict[str, Any]:
        """Get video information from URL.

        Args:
            url: Video URL.

        Returns:
            Dictionary with video metadata.

        Raises:
            Exception: If info retrieval fails.
        """
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                    "formats": self._parse_formats(info.get("formats", [])),
                }
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            raise

    def _parse_formats(self, formats: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Parse and filter video formats.

        Args:
            formats: Raw format list from yt-dlp.

        Returns:
            Filtered list of usable formats.
        """
        usable_formats = []

        for fmt in formats:
            # Filter for video-only formats with audio
            if fmt.get("vcodec") != "none" and fmt.get("acodec") != "none":
                usable_formats.append(
                    {
                        "format_id": fmt.get("format_id"),
                        "ext": fmt.get("ext"),
                        "resolution": fmt.get("resolution"),
                        "height": fmt.get("height"),
                        "width": fmt.get("width"),
                        "filesize": fmt.get("filesize"),
                        "fps": fmt.get("fps"),
                    }
                )

        # Sort by height (quality)
        usable_formats.sort(key=lambda x: x.get("height", 0), reverse=True)
        return usable_formats

    def download(
        self,
        url: str,
        format_id: str | None = None,
        resolution: str | None = None,
        progress_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> Path:
        """Download a video.

        Args:
            url: Video URL.
            format_id: Specific format ID to download.
            resolution: Target resolution (e.g., "1080p", "720p").
            progress_callback: Optional callback for progress updates.

        Returns:
            Path to downloaded file.

        Raises:
            Exception: If download fails.
        """
        def _progress_hook(d: dict[str, Any]) -> None:
            """Internal progress hook for yt-dlp."""
            if progress_callback:
                if d["status"] == "downloading":
                    progress_callback(
                        {
                            "status": "downloading",
                            "downloaded_bytes": d.get("downloaded_bytes", 0),
                            "total_bytes": d.get("total_bytes") or d.get("total_bytes_estimate", 0),
                            "speed": d.get("speed", 0),
                            "eta": d.get("eta", 0),
                            "filename": d.get("filename"),
                        }
                    )
                elif d["status"] == "finished":
                    progress_callback({"status": "finished", "filename": d.get("filename")})

        # Build format selector
        format_selector = "bestvideo+bestaudio/best"
        if resolution:
            format_selector = f"bestvideo[height<={resolution[:-1]}]+bestaudio/best[height<={resolution[:-1]}]"
        if format_id:
            format_selector = format_id

        ydl_opts = {
            "format": format_selector,
            "outtmpl": str(self.output_dir / "%(title)s.%(ext)s"),
            "progress_hooks": [_progress_hook],
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                output_path = Path(filename)

                logger.info(f"Download completed: {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise

    def download_async(
        self,
        url: str,
        format_id: str | None = None,
        resolution: str | None = None,
        progress_callback: Callable[[dict[str, Any]], None] | None = None,
        completion_callback: Callable[[Path], None] | None = None,
        error_callback: Callable[[Exception], None] | None = None,
    ) -> threading.Thread:
        """Download a video in a background thread.

        Args:
            url: Video URL.
            format_id: Specific format ID to download.
            resolution: Target resolution.
            progress_callback: Optional callback for progress updates.
            completion_callback: Optional callback when download completes.
            error_callback: Optional callback if download fails.

        Returns:
            Thread object for the background task.
        """
        def _task() -> None:
            try:
                result = self.download(url, format_id, resolution, progress_callback)
                if completion_callback:
                    completion_callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)

        thread = threading.Thread(target=_task, daemon=True)
        thread.start()
        return thread

    def get_available_resolutions(self, url: str) -> list[str]:
        """Get available resolutions for a video.

        Args:
            url: Video URL.

        Returns:
            List of available resolution strings.
        """
        info = self.get_video_info(url)
        resolutions = set()

        for fmt in info["formats"]:
            if fmt.get("resolution"):
                resolutions.add(fmt["resolution"])

        return sorted(list(resolutions), key=lambda x: int(x[:-1]) if x[:-1].isdigit() else 0, reverse=True)
