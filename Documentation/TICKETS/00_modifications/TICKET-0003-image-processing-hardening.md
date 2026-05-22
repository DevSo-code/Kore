- **Area**: Core
- **Functionality**: Hardening image background removal pipeline (PIL + concurrency + resource limits)
- **Status**: Open

## Why
Review of `src/core/image_processor.py` identified several production risks when processing images:

1. **Shared ONNX session across concurrent threads**
   - `remove_background_async()` spawns a new thread per task, but all tasks reuse `self.session`.
   - There is no lock/serialization around `remove(... session=self.session ...)`.
   - This can lead to intermittent GPU/ORT failures and unstable behavior.

2. **PIL file handle lifecycle**
   - `Image.open(input_path)` is not wrapped in a context manager.
   - On Windows, this can cause delayed file handle release.

3. **No maximum image size / pixel-count guard**
   - Large images can cause excessive RAM/VRAM usage and freezes/crashes.

4. **Callbacks invoked from worker threads**
   - `progress_callback`, `completion_callback`, and `error_callback` are called directly from the worker thread.
   - If UI code touches widgets inside these callbacks, this can violate GUI thread rules.

## Code references
- `src/core/image_processor.py`
  - `remove_background_async()` (spawns threads)
  - `remove_background()` (calls `remove(... session=self.session ...)`)
  - `input_image = Image.open(input_path)` (no context manager)
  - `progress_callback(...)` / `completion_callback(...)` / `error_callback(e)` (called on worker thread)
  - `providers=["CUDAExecutionProvider", "CPUExecutionProvider"]` (GPU provider use)

## Acceptance criteria
- **Thread safety**
  - Concurrent calls to background removal cannot execute ONNX inference simultaneously using the shared session (e.g., lock/queue/worker pool).
  - If multiple async tasks are started, behavior is deterministic and no intermittent ORT/GPU errors occur.

- **Proper PIL handling**
  - Input image loading closes handles deterministically (`with Image.open(...) as input_image:`).

- **Resource limiting**
  - Processing rejects or safely downscales images above a configured pixel-count threshold (e.g., `MAX_PIXELS`).
  - The app logs a clear error when the limit is exceeded.

- **Callback safety**
  - Either:
    - callbacks are documented/validated as thread-safe, **or**
    - callbacks are routed to the UI thread (via queue/dispatcher) when used by UI components.

## Notes
- Preferred long-term architecture for GPU stability: **single AI worker / task queue** for inference.
- Consider adding a cancellation mechanism later; this ticket focuses on correctness and stability.

