"""Image processing service using rembg.

This module wraps rembg for background removal with GPU detection
and async execution support.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Callable

import onnxruntime as ort
from PIL import Image
from rembg import new_session, remove

from src.constants import CACHE_DIR

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Service for image background removal using rembg."""

    def __init__(self, use_gpu: bool = True) -> None:
        """Initialize the image processor.

        Args:
            use_gpu: Whether to attempt GPU acceleration.
        """
        self.use_gpu = use_gpu and self._check_gpu_available()
        self.session = None
        self._initialize_session()

    def _check_gpu_available(self) -> bool:
        """Check if GPU acceleration is available.

        Returns:
            True if GPU is available, False otherwise.
        """
        try:
            # Check for CUDA execution providers
            available_providers = ort.get_available_providers()
            logger.info(f"Available ONNX Runtime providers: {available_providers}")
            return "CUDAExecutionProvider" in available_providers
        except Exception as e:
            logger.warning(f"Failed to check GPU availability: {e}")
            return False

    def _initialize_session(self) -> None:
        """Initialize the rembg session with GPU or CPU."""
        try:
            if self.use_gpu:
                logger.info("Attempting to initialize GPU session...")
                self.session = new_session("u2net", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
                logger.info("GPU session initialized successfully")
            else:
                logger.info("Initializing CPU session...")
                self.session = new_session("u2net", providers=["CPUExecutionProvider"])
                logger.info("CPU session initialized successfully")
        except Exception as e:
            logger.warning(f"GPU initialization failed: {e}. Falling back to CPU.")
            self.use_gpu = False
            try:
                self.session = new_session("u2net", providers=["CPUExecutionProvider"])
                logger.info("CPU session initialized successfully (fallback)")
            except Exception as e2:
                logger.error(f"Failed to initialize CPU session: {e2}")
                raise

    def remove_background(
        self,
        input_path: str | Path,
        output_path: str | Path,
        alpha_matting: bool = False,
        alpha_matting_foreground_threshold: int = 240,
        alpha_matting_background_threshold: int = 10,
        alpha_matting_erode_size: int = 10,
        post_process_mask: bool = False,
        progress_callback: Callable[[float], None] | None = None,
    ) -> Path:
        """Remove background from an image.

        Args:
            input_path: Path to input image.
            output_path: Path to save output image.
            alpha_matting: Whether to use alpha matting.
            alpha_matting_foreground_threshold: Foreground threshold for alpha matting.
            alpha_matting_background_threshold: Background threshold for alpha matting.
            alpha_matting_erode_size: Erode size for alpha matting.
            post_process_mask: Whether to post-process the mask.
            progress_callback: Optional callback for progress updates (0-1).

        Returns:
            Path to the output image.

        Raises:
            Exception: If processing fails.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input image not found: {input_path}")

        if progress_callback:
            progress_callback(0.1)

        try:
            # Load image
            input_image = Image.open(input_path)

            if progress_callback:
                progress_callback(0.3)

            # Remove background
            output_image = remove(
                input_image,
                session=self.session,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=alpha_matting_background_threshold,
                alpha_matting_erode_size=alpha_matting_erode_size,
                post_process_mask=post_process_mask,
            )

            if progress_callback:
                progress_callback(0.8)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save output
            output_image.save(output_path, format="PNG")

            if progress_callback:
                progress_callback(1.0)

            logger.info(f"Background removed successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            raise

    def remove_background_async(
        self,
        input_path: str | Path,
        output_path: str | Path,
        alpha_matting: bool = False,
        alpha_matting_foreground_threshold: int = 240,
        alpha_matting_background_threshold: int = 10,
        alpha_matting_erode_size: int = 10,
        post_process_mask: bool = False,
        progress_callback: Callable[[float], None] | None = None,
        completion_callback: Callable[[Path], None] | None = None,
        error_callback: Callable[[Exception], None] | None = None,
    ) -> threading.Thread:
        """Remove background from an image in a background thread.

        Args:
            input_path: Path to input image.
            output_path: Path to save output image.
            alpha_matting: Whether to use alpha matting.
            alpha_matting_foreground_threshold: Foreground threshold for alpha matting.
            alpha_matting_background_threshold: Background threshold for alpha matting.
            alpha_matting_erode_size: Erode size for alpha matting.
            post_process_mask: Whether to post-process the mask.
            progress_callback: Optional callback for progress updates (0-1).
            completion_callback: Optional callback when processing completes.
            error_callback: Optional callback if processing fails.

        Returns:
            Thread object for the background task.
        """
        def _task() -> None:
            try:
                result = self.remove_background(
                    input_path,
                    output_path,
                    alpha_matting=alpha_matting,
                    alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                    alpha_matting_background_threshold=alpha_matting_background_threshold,
                    alpha_matting_erode_size=alpha_matting_erode_size,
                    post_process_mask=post_process_mask,
                    progress_callback=progress_callback,
                )
                if completion_callback:
                    completion_callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)

        thread = threading.Thread(target=_task, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def get_supported_formats() -> list[str]:
        """Get list of supported image formats.

        Returns:
            List of supported file extensions.
        """
        return [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]

    @staticmethod
    def is_supported_format(file_path: str | Path) -> bool:
        """Check if a file format is supported.

        Args:
            file_path: Path to check.

        Returns:
            True if format is supported, False otherwise.
        """
        return Path(file_path).suffix.lower() in ImageProcessor.get_supported_formats()
