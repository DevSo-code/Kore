# ROADMAP.md — Build Phases

## Phase 1: MVP (Days 1–2)
**Goal**: A working, installable app with 3 core tools.

- [x] Project scaffold with CustomTkinter shell and tab router
- [x] Image Studio: drag-drop → rembg → save PNG (CPU path)
- [x] Video Grab: URL input → yt-dlp → resolution picker → download
- [x] Spotify Downloader: URL input → spotdl → format picker → download
- [x] SQLite settings persistence (theme, output folder)
- [ ] PyInstaller spec for Windows `.exe` (smoke test build)
- [x] Dark theme applied to all components

**Success Criteria**: A teammate can install the `.exe` or run the Python source and process one image + one video + one Spotify track without crashes.

---

## Phase 2: Polish & Auth (Days 3–5)
**Goal**: Production-ready stability and user trust.

- [ ] GPU acceleration path for rembg with auto-detection
- [ ] Download history panel with "re-download" support
- [ ] In-app update checker (GitHub releases API)
- [ ] Linux AppImage + PKGBUILD packaging
- [ ] Comprehensive error handling and user toasts
- [ ] Keyboard shortcuts (Ctrl+1 for Image, Ctrl+2 for Video, Ctrl+S for Save)

**Success Criteria**: App feels "store-ready." No unhandled exceptions. Builds pass CI.

---

## Phase 3: Scaling & Ecosystem (Weeks 2–4)
**Goal**: Transform from utility into an extensible platform.

- [ ] Plugin architecture: load third-party Python modules as new tabs
- [ ] Batch processing queue (multiple images/videos in parallel)
- [ ] Additional modules: image upscaler (Real-ESRGAN), metadata editor, format converter
- [ ] Cloud sync option (optional WebDAV / S3 backup of settings)
- [ ] macOS universal binary support
- [ ] Auto-updater with delta patches

**Success Criteria**: Community can write a plugin that adds a new tab without modifying core code.