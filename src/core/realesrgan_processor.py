"""Real-ESRGAN image upscaling processor.

This module handles image upscaling using the Real-ESRGAN deep learning model.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Callable

import torch
from PIL import Image
from py_real_esrgan.model import RealESRGAN

from src.constants import CACHE_DIR

logger = logging.getLogger(__name__)


class RealESRGANProcessor:
    """Processor for Real-ESRGAN image upscaling."""

    def __init__(self, use_gpu: bool = True) -> None:
        """Initialize the Real-ESRGAN processor.

        Args:
            use_gpu: Whether to use GPU acceleration if available.
        """
        self.use_gpu = use_gpu
        self.model: RealESRGAN | None = None
        self.model_loaded = False
        self._lock = threading.Lock()

        # Model weights path
        self.model_path = CACHE_DIR / "RealESRGAN_x4plus.pth"

    def _load_model(self, scale: int = 4) -> None:
        """Load the Real-ESRGAN model.

        Args:
            scale: Upscaling factor for the model.
        """
        with self._lock:
            if self.model_loaded and self.model is not None:
                # Check if scale matches, if not reload
                if hasattr(self.model, 'scale') and self.model.scale == scale:
                    return

            try:
                # Determine device
                device = torch.device("cuda" if self.use_gpu and torch.cuda.is_available() else "cpu")
                logger.info(f"Using device: {device}")

                # Create the model
                self.model = RealESRGAN(device, scale=scale)
                
                # Load weights (will download if not present)
                # Using the correct model name for Real-ESRGAN x4plus
                # py-real-esrgan expects weights/ prefix
                self.model.load_weights(
                    'weights/RealESRGAN_x4plus.pth',
                    download=True
                )

                self.model_loaded = True
                logger.info("Real-ESRGAN model loaded successfully")

            except Exception as e:
                logger.error(f"Failed to load Real-ESRGAN model: {e}")
                raise

    def upscale_image(
        self,
        input_path: Path,
        output_path: Path,
        scale: int = 4,
        progress_callback: Callable[[float], None] | None = None,
    ) -> Path:
        """Upscale an image using Real-ESRGAN.

        Args:
            input_path: Path to the input image.
            output_path: Path where the upscaled image will be saved.
            scale: Upscaling factor (default: 4).
            progress_callback: Optional callback for progress updates (0.0 to 1.0).

        Returns:
            Path to the upscaled image.

        Raises:
            Exception: If upscaling fails.
        """
        self._load_model(scale)

        try:
            if progress_callback:
                progress_callback(0.1)

            # Load the input image
            pil_image = Image.open(input_path).convert("RGB")

            if progress_callback:
                progress_callback(0.3)

            # Run super-resolution
            sr_image = self.model.predict(pil_image)

            if progress_callback:
                progress_callback(0.8)

            # Save the result
            sr_image.save(output_path)
            logger.info(f"Saved upscaled image to {output_path}")

            if progress_callback:
                progress_callback(1.0)

            return output_path

        except Exception as e:
            logger.error(f"Failed to upscale image: {e}")
            raise

    def upscale_image_async(
        self,
        input_path: Path,
        output_path: Path,
        scale: int = 4,
        progress_callback: Callable[[float], None] | None = None,
        completion_callback: Callable[[Path], None] | None = None,
        error_callback: Callable[[Exception], None] | None = None,
    ) -> None:
        """Upscale an image asynchronously.

        Args:
            input_path: Path to the input image.
            output_path: Path where the upscaled image will be saved.
            scale: Upscaling factor (default: 4).
            progress_callback: Optional callback for progress updates (0.0 to 1.0).
            completion_callback: Optional callback called on success.
            error_callback: Optional callback called on error.
        """
        def _upscale() -> None:
            try:
                result = self.upscale_image(
                    input_path, output_path, scale, progress_callback
                )
                if completion_callback:
                    completion_callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)

        thread = threading.Thread(target=_upscale, daemon=True)
        thread.start()
