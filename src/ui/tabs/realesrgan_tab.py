"""Real-ESRGAN tab for image upscaling.

This module contains the UI and logic for the Real-ESRGAN image upscaling feature.
"""

from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image, ImageTk

from src.constants import (
    COLOR_ACCENT_PRIMARY,
    COLOR_BG_BASE,
    COLOR_BG_ELEVATED,
    COLOR_BG_HOVER,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_BORDER_FOCUS,
    COLOR_SURFACE_CONTAINER,
    COLOR_SURFACE_CONTAINER_HIGH,
    COLOR_SURFACE_CONTAINER_LOW,
    COLOR_SURFACE_CONTAINER_LOWEST,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    SUPPORTED_IMAGE_FORMATS,
    CARD_CORNER_RADIUS,
)
from src.core.realesrgan_processor import RealESRGANProcessor
from src.db.repository import DatabaseRepository
from src.models.settings import ProcessingOperation, ProcessingQueue, ProcessingStatus
from src.ui.theme import resolve_color

logger = logging.getLogger(__name__)


class RealESRGANTab(ctk.CTkFrame):
    """Real-ESRGAN tab with image upscaling functionality."""

    def __init__(self, parent: ctk.CTkFrame, app: ctk.CTk) -> None:
        """Initialize the Real-ESRGAN tab.

        Args:
            parent: Parent widget.
            app: Main application instance.
        """
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.realesrgan_processor = RealESRGANProcessor(use_gpu=True)
        self.db = DatabaseRepository()
        self.current_image_path: Path | None = None
        self.upscaled_image_path: Path | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the Real-ESRGAN tab UI with bento layout."""
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
            text="Image Upscaling",
            font=("Inter", 18, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.title_label.pack(fill="x")

        self.subtitle_label = ctk.CTkLabel(
            self.title_group,
            text="4× super-resolution upscaling using Real-ESRGAN deep learning model.",
            font=("Inter", 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.subtitle_label.pack(fill="x")

        self.actions_group = ctk.CTkFrame(self.header, fg_color="transparent")
        self.actions_group.pack(side="right")

        self.save_button = ctk.CTkButton(
            self.actions_group,
            text="Save As",
            font=("Inter", 12),
            height=32,
            fg_color="transparent",
            border_color=COLOR_BORDER,
            border_width=1,
            hover_color=COLOR_BG_HOVER,
            state="disabled",
            command=self._save_image,
        )
        self.save_button.pack(side="left", padx=(0, 10))

        self.process_button = ctk.CTkButton(
            self.actions_group,
            text="Upscale 4×",
            font=("Inter", 12, "bold"),
            height=32,
            fg_color=COLOR_ACCENT_PRIMARY,
            hover_color=COLOR_BG_HOVER,
            state="disabled",
            command=self._process_image,
        )
        self.process_button.pack(side="left")

        # Bento Grid
        self.grid_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True)
        self.grid_container.grid_columnconfigure(0, weight=2)  # Left column (Settings & Upload)
        self.grid_container.grid_columnconfigure(1, weight=3)  # Right column (Workspace)
        self.grid_container.grid_rowconfigure(0, weight=1)

        # Left Column: Upload & Settings
        self.left_column = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Drop Zone
        self.drop_zone = ctk.CTkFrame(
            self.left_column,
            fg_color=COLOR_BG_SURFACE,
            border_color=COLOR_BORDER,
            border_width=2,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.drop_zone.pack(fill="both", expand=True, pady=(0, 10))
        self.drop_zone.bind("<Button-1>", self._browse_file)

        self.upload_icon = ctk.CTkLabel(
            self.drop_zone,
            text="📤",
            font=("Inter", 32),
        )
        self.upload_icon.place(relx=0.5, rely=0.4, anchor="center")

        self.drop_label = ctk.CTkLabel(
            self.drop_zone,
            text="Upload Source Image",
            font=("Inter", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.drop_label.place(relx=0.5, rely=0.55, anchor="center")

        self.drop_sublabel = ctk.CTkLabel(
            self.drop_zone,
            text="Drag and drop or click to browse\nPNG, JPG, WEBP (Max 20MB)",
            font=("Inter", 11),
            text_color=COLOR_TEXT_MUTED,
            justify="center",
        )
        self.drop_sublabel.place(relx=0.5, rely=0.65, anchor="center")

        # Upscaling Settings
        self.settings_card = ctk.CTkFrame(
            self.left_column,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
            height=180,
        )
        self.settings_card.pack(fill="x")
        self.settings_card.pack_propagate(False)

        self.settings_title = ctk.CTkLabel(
            self.settings_card,
            text="Upscaling Settings",
            font=("Inter", 13, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.settings_title.pack(padx=15, pady=(15, 10), anchor="w")

        # Scale Factor
        self.scale_frame = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.scale_frame.pack(fill="x", padx=15, pady=5)

        self.scale_label_group = ctk.CTkFrame(self.scale_frame, fg_color="transparent")
        self.scale_label_group.pack(fill="x")

        self.scale_label = ctk.CTkLabel(
            self.scale_label_group, text="Scale Factor", font=("Inter", 11), text_color=COLOR_TEXT_SECONDARY
        )
        self.scale_label.pack(side="left")

        self.scale_value = ctk.CTkLabel(
            self.scale_label_group, text="4×", font=("JetBrains Mono", 11), text_color=COLOR_ACCENT_PRIMARY
        )
        self.scale_value.pack(side="right")

        self.scale_slider = ctk.CTkSlider(
            self.scale_frame,
            from_=2,
            to=8,
            number_of_steps=6,
            height=16,
            button_color=COLOR_ACCENT_PRIMARY,
            button_hover_color=COLOR_ACCENT_PRIMARY,
            progress_color=COLOR_ACCENT_PRIMARY,
        )
        self.scale_slider.set(4)
        self.scale_slider.pack(fill="x", pady=(5, 0))
        self.scale_slider.configure(command=lambda v: self.scale_value.configure(text=f"{int(v)}×"))

        # GPU Acceleration Toggle
        self.gpu_frame = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.gpu_frame.pack(fill="x", padx=15, pady=10)

        self.gpu_label = ctk.CTkLabel(
            self.gpu_frame, text="GPU Acceleration", font=("Inter", 11), text_color=COLOR_TEXT_SECONDARY
        )
        self.gpu_label.pack(side="left")

        self.gpu_switch = ctk.CTkSwitch(
            self.gpu_frame,
            text="",
            width=40,
            progress_color=COLOR_ACCENT_PRIMARY,
        )
        self.gpu_switch.pack(side="right")
        self.gpu_switch.select()

        # Right Column: Workspace
        self.workspace_column = ctk.CTkFrame(
            self.grid_container,
            fg_color=COLOR_SURFACE_CONTAINER,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=CARD_CORNER_RADIUS,
        )
        self.workspace_column.grid(row=0, column=1, sticky="nsew")

        # Workspace Header (Tabs)
        self.workspace_header = ctk.CTkFrame(
            self.workspace_column,
            fg_color=COLOR_SURFACE_CONTAINER_HIGH,
            height=36,
            corner_radius=0,
        )
        self.workspace_header.pack(fill="x")
        self.workspace_header.pack_propagate(False)

        self.tab_original = ctk.CTkButton(
            self.workspace_header,
            text="Original",
            font=("Inter", 12, "bold"),
            fg_color="transparent",
            text_color=COLOR_ACCENT_PRIMARY,
            width=100,
            height=36,
            corner_radius=0,
        )
        self.tab_original.pack(side="left", padx=(10, 0))

        self.tab_upscaled = ctk.CTkButton(
            self.workspace_header,
            text="Upscaled",
            font=("Inter", 12),
            fg_color="transparent",
            text_color=COLOR_TEXT_SECONDARY,
            width=100,
            height=36,
            corner_radius=0,
            hover_color=COLOR_BG_HOVER,
        )
        self.tab_upscaled.pack(side="left")

        # Preview Area
        self.preview_area = ctk.CTkFrame(self.workspace_column, fg_color="transparent")
        self.preview_area.pack(fill="both", expand=True)

        self.preview_canvas = tk.Canvas(
            self.preview_area,
            bg=resolve_color(COLOR_SURFACE_CONTAINER_LOWEST),
            highlightthickness=0,
        )
        self.preview_canvas.pack(fill="both", expand=True)

        # Initial state message
        self.preview_canvas.create_text(
            300, 200,
            text="Upload an image to start upscaling",
            fill=resolve_color(COLOR_TEXT_MUTED),
            font=("Inter", 12),
            tags="placeholder"
        )

        # Progress bar (integrated at bottom of workspace)
        self.progress_bar = ctk.CTkProgressBar(
            self.workspace_column,
            height=4,
            corner_radius=0,
            progress_color=COLOR_ACCENT_PRIMARY,
        )
        self.progress_bar.pack(fill="x", side="bottom")
        self.progress_bar.set(0)

    def _browse_file(self, event: tk.Event | None = None) -> None:
        """Open file browser to select an image."""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            self._load_image(Path(file_path))

    def _load_image(self, image_path: Path) -> None:
        """Load and display an image with thumbnail optimization.

        Args:
            image_path: Path to the image file.
        """
        try:
            self.current_image_path = image_path
            
            # Load full image for processing
            self.original_image = Image.open(image_path)
            
            # CREATE THUMBNAIL for preview
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            if canvas_width < 10: canvas_width = 600
            if canvas_height < 10: canvas_height = 400
            
            thumb = self.original_image.copy()
            thumb.thumbnail((canvas_width, canvas_height))
            self.preview_image = ImageTk.PhotoImage(thumb)
            
            # Cache the thumbnail
            from src.constants import CACHE_DIR
            thumb_path = CACHE_DIR / f"{image_path.stem}_thumb.png"
            thumb.save(thumb_path, quality=85, optimize=True)

            # Show preview
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                canvas_width // 2, canvas_height // 2, image=self.preview_image, anchor="center"
            )

            # Enable buttons
            self.process_button.configure(state="normal")
            self.save_button.configure(state="disabled")

            self.app.set_status(f"Loaded: {image_path.name}")

        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            self.app.show_toast(f"Failed to load image: {e}", is_error=True)

    def _process_image(self) -> None:
        """Process the current image to upscale it."""
        if not self.current_image_path:
            return

        self.process_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.app.set_status("Upscaling image...")

        # Get settings from UI
        scale = int(self.scale_slider.get())
        use_gpu = self.gpu_switch.get() == 1

        # Generate output path in cache
        from src.constants import CACHE_DIR
        output_path = CACHE_DIR / f"{self.current_image_path.stem}_upscaled_{scale}x.png"

        # Create queue entry BEFORE processing
        job = ProcessingQueue(
            input_path=str(self.current_image_path),
            output_path=str(output_path),
            operation=ProcessingOperation.BG_REMOVAL,  # Reusing existing operation type
            status=ProcessingStatus.PENDING,
        )
        job_id = self.db.add_processing_queue(job)

        def progress_callback(progress: float) -> None:
            """Update progress during processing."""
            self.progress_bar.set(progress)

        def completion_callback(result: Path) -> None:
            """Handle processing completion."""
            self.upscaled_image_path = result
            self.progress_bar.set(1)
            self.process_button.configure(state="normal")
            self.save_button.configure(state="normal")
            self.app.set_status(f"Upscaling complete.")

            # Update job status to DONE
            self.db.update_processing_status(job_id, ProcessingStatus.DONE)

            # Load and show upscaled image
            self._show_upscaled(result)

        def error_callback(error: Exception) -> None:
            """Handle processing error."""
            logger.error(f"Upscaling failed: {error}")
            self.progress_bar.set(0)
            self.process_button.configure(state="normal")
            self.app.show_toast(f"Upscaling failed: {error}", is_error=True)

            # Update job status to ERROR
            self.db.update_processing_status(
                job_id, ProcessingStatus.ERROR, error_message=str(error)
            )

        # Update job status to PROCESSING
        self.db.update_processing_status(job_id, ProcessingStatus.PROCESSING)

        # Start async processing
        self.realesrgan_processor.upscale_image_async(
            self.current_image_path,
            output_path,
            scale=scale,
            progress_callback=progress_callback,
            completion_callback=completion_callback,
            error_callback=error_callback,
        )

    def _show_upscaled(self, upscaled_path: Path) -> None:
        """Show the upscaled image."""
        try:
            upscaled_image = Image.open(upscaled_path)
            
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Create thumbnail for preview
            upscaled_image.thumbnail((canvas_width, canvas_height))
            self.preview_image = ImageTk.PhotoImage(upscaled_image)
            
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                canvas_width // 2, canvas_height // 2, image=self.preview_image, anchor="center"
            )
            
            # Add label
            self.preview_canvas.create_text(
                10, 10, text="UPSCALED", fill=resolve_color(COLOR_ACCENT_PRIMARY), anchor="nw", font=("Inter", 10, "bold")
            )

        except Exception as e:
            logger.error(f"Failed to show upscaled image: {e}")

    def _save_image(self) -> None:
        """Save the upscaled image to a user-selected location."""
        if not self.upscaled_image_path:
            return

        file_path = filedialog.asksaveasfilename(
            title="Save image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
        )

        if file_path:
            try:
                import shutil
                shutil.copy(self.upscaled_image_path, file_path)
                self.app.set_status(f"Saved to {file_path}")
                self.app.show_toast("Image saved successfully")
            except Exception as e:
                logger.error(f"Failed to save image: {e}")
                self.app.show_toast(f"Failed to save image: {e}", is_error=True)

    def _clear_image(self) -> None:
        """Clear the current image and reset UI."""
        self.current_image_path = None
        self.upscaled_image_path = None
        
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(
            300, 200,
            text="Upload an image to start upscaling",
            fill=resolve_color(COLOR_TEXT_MUTED),
            font=("Inter", 12),
            tags="placeholder"
        )

        self.process_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.app.set_status("Ready")
