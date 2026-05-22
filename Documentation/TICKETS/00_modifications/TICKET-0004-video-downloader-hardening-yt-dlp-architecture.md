- **Area**: Core / UI integration
- **Functionality**: Hardening video downloader architecture (yt-dlp correctness + production risks)
- **Status**: Open

## Why
A code review of the current video downloader implementation identified that the overall architecture is strong and production-oriented, but there are several correctness and robustness risks that should be addressed before wider usage.

## Code references
- `src/core/video_downloader.py` (main target; review notes reference its yt-dlp integration)
- Potential related UI worker/callback code (same risk pattern as other modules):
  - `src/ui/tabs/video_tab.py`

## What you did very well (keep)
- Using **yt-dlp Python API** instead of subprocess (clean, stable integration)
- Caching system (`_info_cache`, `_cache_timestamp`, `_cache_ttl`)
- Progress hook integration (`progress_hooks`)
- Format parsing and resolution selection logic
- Async separation and typed callbacks
- Separation of concerns / configurable format selection

## Main problems & risks
1. **CRITICAL BUG — Returned file path can be wrong**
   - Current logic returns `filename = ydl.prepare_filename(info)`.
   - If `merge_output_format="mp4"` is used, yt-dlp may download temporary files, merge them, and delete originals.
   - In that case, `prepare_filename(info)` may point to the *pre-merge* filename, not the final output.
   - Symptom: UI shows “download complete” but file path doesn’t exist.

   **Fix direction**: use the final post-processed filename from `info.get("_filename")` / postprocessor output (or query the actual output path produced by yt-dlp).

2. **Filename sanitization risk**
   - Using `%(title)s.%(ext)s` can fail on Windows due to characters like `/:?` and extremely long names.

   **Fix direction**:
   - truncate the title (e.g. `%(title).200s.%(ext)s`)
   - consider `restrictfilenames=True`

3. **Cache is not thread-safe**
   - If the downloader runs metadata/cache reads/writes from multiple threads, dictionaries (`_info_cache`, `_cache_timestamp`) can race.

   **Fix direction**: protect cache mutations/reads with a lock (`threading.Lock`).

4. **GUI thread violation (callback threading)**
   - Callbacks used by the UI may currently run inside worker threads.
   - If callbacks touch UI widgets directly, it can break Tkinter/customtkinter/Qt.

   **Fix direction**: route UI updates through UI thread dispatcher/queue.

5. **Fragile resolution parsing**
   - If code assumes `resolution[:-1]` maps cleanly to `720p/1080p`, yt-dlp variants (e.g. height missing, audio-only) can cause parsing errors.

   **Fix direction**: store/compare actual numeric height from format fields.

6. **Cache memory growth risk**
   - Cache entries may never be evicted unless re-requested.

   **Fix direction**: periodic cleanup based on `_cache_ttl` and/or max-size.

7. **Missing download cancellation**
   - Current async model may not allow stopping an in-progress download.

8. **Thread-per-download scalability risk**
   - Spawning one thread per download can degrade performance (many parallel downloads => many threads).

   **Fix direction**: use a centralized queue / `ThreadPoolExecutor` or a worker model.

9. **Missing FFmpeg validation**
   - yt-dlp merging depends on FFmpeg.

   **Fix direction**: validate FFmpeg availability at startup and surface a clear user error.

10. **Additional production hardening gaps** (lower priority)
   - dependency/rate limiting/retry behavior during actual downloads
   - cookie/auth support
   - proxy / bandwidth / user-agent controls
   - quieter logs only in production; keep verbose logging in debug
   - playlist handling (if desired)
   - file integrity validation after merge/download

## Acceptance criteria
- **Correct final output path**
  - After a successful download with `merge_output_format="mp4"`, the function returns a path that exists on disk.

- **Robust filenames on Windows**
  - No invalid filename errors; long titles are truncated; special characters are handled.

- **Thread-safe caching**
  - No race conditions / dictionary mutation exceptions when multiple downloads are active.

- **UI callback safety**
  - UI updates happen on the UI thread only (no direct widget updates from downloader worker threads).

- **Resolution parsing resilience**
  - No crashes on audio-only formats or formats without expected `resolution` fields.

## Notes
- Biggest hidden risk to address first: **`prepare_filename()` vs final post-processed output** when merging to mp4.
- Keep the overall architecture; focus on correctness + concurrency + UI-thread correctness.

