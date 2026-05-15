# SPEC.md — Kore MVP Specification

## Product Overview

**Kore** is a local-first, offline-capable desktop utility suite built in Python. It consolidates everyday power-user tools (image manipulation, video downloading, file conversion) into a single, tabbed GUI with no ads, no data collection, and no internet dependency for core features.

---

## MVP Scope (24–48h Build Target)

### In Scope

| Module | Feature | Library |
|--------|---------|---------|
| Image | Background removal (local AI) | `rembg` + ONNX |
| Image | Drag-and-drop input, PNG/WebP output | `tkinterdnd2` / Flet |
| Video | URL download (YouTube, etc.) | `yt-dlp` |
| Video | Format/resolution selector (720p, 1080p, 4K, MP3) | `yt-dlp` |
| Video | Progress bar with ETA | `yt-dlp` hooks |
| UI | Dark-mode tabbed shell | `CustomTkinter` or `Flet` |
| UI | Output folder picker | `tkinter.filedialog` |
| UI | Notification on task complete | OS toast / in-app banner |

### Out of Scope (MVP)

- Batch image processing
- Playlist management UI
- Video trimming / editing
- User accounts or cloud sync
- Auto-update mechanism

---

## User Flow

### Flow 1 — Background Removal

```
Launch App
  └── Click "Image" tab
        └── Drag image OR click "Browse"
              └── Preview shown (before)
                    └── Click "Remove Background"
                          └── Progress spinner
                                └── After-preview shown
                                      └── "Save As" → PNG/WebP exported
```

### Flow 2 — Video Download

```
Launch App
  └── Click "Video" tab
        └── Paste URL into input field
              └── Click "Fetch Info" (optional: loads title + thumbnail)
                    └── Select Format (mp4 / webm) + Quality (best / 1080p / 720p / audio-only)
                          └── Click "Download"
                                └── Progress bar + speed/ETA live display
                                      └── "Open Folder" button appears on completion
```

---

## Functional Requirements

### FR-01 Image Module
- Accept PNG, JPG, JPEG, WEBP inputs
- Run `rembg` locally (no API call)
- Model auto-downloads on first use (`u2net` default)
- Output as transparent PNG or white-bg WEBP
- Display side-by-side before/after preview

### FR-02 Video Module
- Accept any URL `yt-dlp` supports
- Parse available formats via `yt-dlp --dump-json`
- Map UI quality options to `yt-dlp` format strings
- Download to user-selected output directory
- Stream stdout to progress bar widget

### FR-03 UI Shell
- App launches to last-used tab
- Settings persist via `config.json` in user config dir
- All tasks run in background threads (UI never freezes)
- Error states shown inline (red banner, not modal popup)

---

## Non-Functional Requirements

- **Startup time:** < 4 seconds cold start
- **Memory:** < 300 MB idle, < 1.2 GB during AI inference
- **Packaging:** Single executable on Windows (PyInstaller), AppImage on Linux
- **Offline:** Core features work with zero internet (after model download)
- **GPU:** Optional CUDA/ROCm acceleration via `onnxruntime-gpu`

---

## Acceptance Criteria (MVP Done When)

- [ ] Background removal works on a 4K image in < 15 seconds (CPU)
- [ ] Video download completes a 1080p file with accurate progress display
- [ ] App runs from `.exe` / AppImage with no Python installation required
- [ ] No crash on invalid URL or unsupported image format
- [ ] Dark mode renders correctly on Windows 11 and Arch Linux
