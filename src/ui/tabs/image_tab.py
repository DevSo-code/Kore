"""Image Studio tab for background removal.

This module contains the UI and logic for the image background removal feature.
"""

from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image, ImageTk
from src.ui.theme import resolve_color

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
from src.core.image_processor import ImageProcessor
from src.db.repository import DatabaseRepository
from src.models.settings import ProcessingOperation, ProcessingQueue, ProcessingStatus

logger = logging.getLogger(__name__)


class ImageTab(ctk.CTkFrame):
    """Image Studio tab with drag-drop and background removal."""

    def __init__(self, parent: ctk.CTkFrame, app: ctk.CTk) -> None:
        """Initialize the Image tab.

        Args:
            parent: Parent widget.
            app: Main application instance.
        """
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.image_processor = ImageProcessor(use_gpu=True)
        self.db = DatabaseRepository()
        self.current_image_path: Path | None = None
        self.processed_image_path: Path | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the Image tab UI with bento layout."""
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
            text="Background Removal",
            font=("Inter", 18, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.title_label.pack(fill="x")

        self.subtitle_label = ctk.CTkLabel(
            self.title_group,
            text="Professional transparency extraction and subject isolation.",
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
            text="Remove Background",
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

        # Refinement Settings
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
            text="Refinement Settings",
            font=("Inter", 13, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.settings_title.pack(padx=15, pady=(15, 10), anchor="w")

        # Edge Smoothness Slider
        self.smoothness_frame = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.smoothness_frame.pack(fill="x", padx=15, pady=5)

        self.smoothness_label_group = ctk.CTkFrame(self.smoothness_frame, fg_color="transparent")
        self.smoothness_label_group.pack(fill="x")

        self.smoothness_label = ctk.CTkLabel(
            self.smoothness_label_group, text="Edge Smoothness", font=("Inter", 11), text_color=COLOR_TEXT_SECONDARY
        )
        self.smoothness_label.pack(side="left")

        self.smoothness_value = ctk.CTkLabel(
            self.smoothness_label_group, text="0.4px", font=("JetBrains Mono", 11), text_color=COLOR_ACCENT_PRIMARY
        )
        self.smoothness_value.pack(side="right")

        self.smoothness_slider = ctk.CTkSlider(
            self.smoothness_frame,
            from_=0,
            to=10,
            number_of_steps=100,
            height=16,
            button_color=COLOR_ACCENT_PRIMARY,
            button_hover_color=COLOR_ACCENT_PRIMARY,
            progress_color=COLOR_ACCENT_PRIMARY,
        )
        self.smoothness_slider.set(4)
        self.smoothness_slider.pack(fill="x", pady=(5, 0))
        self.smoothness_slider.configure(command=lambda v: self.smoothness_value.configure(text=f"{v:.1f}px"))

        # Alpha Matting Toggle
        self.alpha_frame = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.alpha_frame.pack(fill="x", padx=15, pady=10)

        self.alpha_label = ctk.CTkLabel(
            self.alpha_frame, text="Alpha Matting", font=("Inter", 11), text_color=COLOR_TEXT_SECONDARY
        )
        self.alpha_label.pack(side="left")

        self.alpha_switch = ctk.CTkSwitch(
            self.alpha_frame,
            text="",
            width=40,
            progress_color=COLOR_ACCENT_PRIMARY,
        )
        self.alpha_switch.pack(side="right")
        self.alpha_switch.select()

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

        self.tab_comparison = ctk.CTkButton(
            self.workspace_header,
            text="Comparison",
            font=("Inter", 12, "bold"),
            fg_color="transparent",
            text_color=COLOR_ACCENT_PRIMARY,
            width=100,
            height=36,
            corner_radius=0,
        )
        self.tab_comparison.pack(side="left", padx=(10, 0))

        self.tab_mask = ctk.CTkButton(
            self.workspace_header,
            text="Mask Overlay",
            font=("Inter", 12),
            fg_color="transparent",
            text_color=COLOR_TEXT_SECONDARY,
            width=100,
            height=36,
            corner_radius=0,
            hover_color=COLOR_BG_HOVER,
        )
        self.tab_mask.pack(side="left")

        # Zoom/Fullscreen controls
        self.workspace_controls = ctk.CTkFrame(self.workspace_header, fg_color="transparent")
        self.workspace_controls.pack(side="right", padx=10)

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
            text="Upload an image to start processing",
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
            
            # CREATE THUMBNAIL for preview (50KB instead of 5MB)
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
        """Process the current image to remove background."""
        if not self.current_image_path:
            return

        self.process_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.app.set_status("Removing background...")

        # Get settings from UI
        alpha_matting = self.alpha_switch.get() == 1
        smoothness = self.smoothness_slider.get()
        # Map smoothness (0-10) to erode size (0-20)
        erode_size = int(smoothness * 2)

        # Generate output path in cache
        from src.constants import CACHE_DIR
        output_path = CACHE_DIR / f"{self.current_image_path.stem}_processed.png"

        # Create queue entry BEFORE processing
        job = ProcessingQueue(
            input_path=str(self.current_image_path),
            output_path=str(output_path),
            operation=ProcessingOperation.BG_REMOVAL,
            status=ProcessingStatus.PENDING,
        )
        job_id = self.db.add_processing_queue(job)

        def progress_callback(progress: float) -> None:
            """Update progress during processing."""
            self.progress_bar.set(progress)

        def completion_callback(result: Path) -> None:
            """Handle processing completion."""
            self.processed_image_path = result
            self.progress_bar.set(1)
            self.process_button.configure(state="normal")
            self.save_button.configure(state="normal")
            self.app.set_status(f"Processing complete.")

            # Update job status to DONE
            self.db.update_processing_status(job_id, ProcessingStatus.DONE)

            # Load and show comparison
            self._show_comparison(result)

        def error_callback(error: Exception) -> None:
            """Handle processing error."""
            logger.error(f"Background removal failed: {error}")
            self.progress_bar.set(0)
            self.process_button.configure(state="normal")
            self.app.show_toast(f"Background removal failed: {error}", is_error=True)

            # Update job status to ERROR
            self.db.update_processing_status(
                job_id, ProcessingStatus.ERROR, error_message=str(error)
            )

        # Update job status to PROCESSING
        self.db.update_processing_status(job_id, ProcessingStatus.PROCESSING)

        # Start async processing
        self.image_processor.remove_background_async(
            self.current_image_path,
            output_path,
            alpha_matting=alpha_matting,
            alpha_matting_erode_size=erode_size,
            progress_callback=progress_callback,
            completion_callback=completion_callback,
            error_callback=error_callback,
        )

    def _show_comparison(self, processed_path: Path) -> None:
        """Show side-by-side comparison of original and processed images."""
        try:
            processed_image = Image.open(processed_path)
            
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Create a side-by-side image
            # For simplicity in Tkinter, we'll just show the processed one for now
            # but with a checkerboard background
            processed_image.thumbnail((canvas_width, canvas_height))
            self.preview_image = ImageTk.PhotoImage(processed_image)
            
            self.preview_canvas.delete("all")
            # Draw checkerboard pattern? (Hard in TK Canvas, maybe just a gray bg)
            self.preview_canvas.create_image(
                canvas_width // 2, canvas_height // 2, image=self.preview_image, anchor="center"
            )
            
            # Add label
            self.preview_canvas.create_text(
                10, 10, text="PROCESSED", fill=resolve_color(COLOR_ACCENT_PRIMARY), anchor="nw", font=("Inter", 10, "bold")
            )

        except Exception as e:
            logger.error(f"Failed to show comparison: {e}")

    def _save_image(self) -> None:
        """Save the processed image to a user-selected location."""
        if not self.processed_image_path:
            return

        file_path = filedialog.asksaveasfilename(
            title="Save image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )

        if file_path:
            try:
                import shutil
                shutil.copy(self.processed_image_path, file_path)
                self.app.set_status(f"Saved to {file_path}")
                self.app.show_toast("Image saved successfully")
            except Exception as e:
                logger.error(f"Failed to save image: {e}")
                self.app.show_toast(f"Failed to save image: {e}", is_error=True)

    def _clear_image(self) -> None:
        """Clear the current image and reset UI."""
        self.current_image_path = None
        self.processed_image_path = None
        
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(
            300, 200,
            text="Upload an image to start processing",
            fill=resolve_color(COLOR_TEXT_MUTED),
            font=("Inter", 12),
            tags="placeholder"
        )

        self.process_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.app.set_status("Ready")
