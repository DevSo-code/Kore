# TICKET-0005: Real-ESRGAN Image Upscaling Tab

## Area
UI / Core

## Functionality
Image upscaling using Real-ESRGAN deep learning model (4× super-resolution)

## Status
Done

## Why
Add AI-powered image upscaling capability to the Kore application, allowing users to enhance image resolution by up to 8× using state-of-the-art deep learning model Real-ESRGAN.

## Code references
- `src/models/settings.py`: Added `REALESRGAN` to `Tab` enum
- `src/core/realesrgan_processor.py`: New module for Real-ESRGAN processing logic using py-real-esrgan
- `src/ui/tabs/realesrgan_tab.py`: New UI tab for image upscaling
- `src/ui/app.py`: Added Real-ESRGAN tab to navigation and tab loading
- `requirements.txt`: Added Real-ESRGAN dependencies (py-real-esrgan, torch, torchvision, numpy)

## Acceptance criteria
- [x] New tab added to navigation sidebar with "Upscale" label and ✨ icon
- [x] Tab includes drag-and-drop image upload zone
- [x] Tab includes scale factor slider (2× to 8×)
- [x] Tab includes GPU acceleration toggle
- [x] Tab includes image preview canvas
- [x] Tab includes progress bar for upscaling operations
- [x] Tab includes "Upscale 4×" and "Save As" buttons
- [x] Real-ESRGAN processor downloads model weights automatically on first use
- [x] Processor supports both GPU and CPU execution
- [x] Async processing with progress callbacks
- [x] Database integration for processing queue tracking
- [x] Dependencies added to requirements.txt
- [x] Error handling and user feedback via toast notifications

## Notes
- Model weights are downloaded automatically by py-real-esrgan on first use
- Model weights are also downloaded during installation (setup_gui.py) to cache them upfront
- Uses py-real-esrgan package for Python 3.14 compatibility (instead of basicsr + realesrgan)
- GPU acceleration defaults to enabled, falls back to CPU if CUDA unavailable
- Processing is threaded to avoid blocking UI
- Follows existing tab pattern (similar to image_tab.py for background removal)
- Switched from basicsr/realesrgan to py-real-esrgan due to Python 3.14 compatibility issues
- Installation GUI updated to download both u2net.onnx (176 MB) and RealESRGAN_x4plus.pth (67 MB) during setup
