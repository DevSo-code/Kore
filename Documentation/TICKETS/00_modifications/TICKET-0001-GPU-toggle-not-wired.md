# TICKET-0001-GPU-toggle-not-wired

- **Area**: Core / UI integration
- **Functionality**: GPU acceleration toggle from Settings
- **Status**: Review Needed

## Why
`SettingsTab` stores `gpu_acceleration`, but `ImageTab` instantiates `ImageProcessor(use_gpu=True)` with a hard-coded value, so the setting likely has no effect.

## Code references
- `src/ui/tabs/settings_tab.py`
  - saves `self.settings.gpu_acceleration`
- `src/ui/tabs/image_tab.py`
  - `self.image_processor = ImageProcessor(use_gpu=True)` (hard-coded)
- `src/core/image_processor.py`
  - uses `use_gpu and _check_gpu_available()`

## Acceptance criteria
- Changing GPU toggle in Settings affects `ImageProcessor` usage for subsequent image processing.
- If GPU is enabled but providers are unavailable, the app gracefully falls back to CPU.

## Notes
Prefer wiring `ImageProcessor(use_gpu=self.app.settings.gpu_acceleration)` and recreating/reconfiguring the processor when the setting changes.

