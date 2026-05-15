# TECH_STACK.md — Technology Stack

## Runtime & Language
- **Python 3.11+** — Modern syntax, better error messages, stable asyncio

## GUI Framework (Choose One)

### Primary Recommendation: CustomTkinter
- **Why**: Native look-and-feel, mature ecosystem, easy PyInstaller bundling, true offline operation
- **Key deps**: `customtkinter`, `Pillow` (for image previews), `tkinterdnd2` (drag-and-drop)

### Alternative: Flet
- **Why**: If you want a more web-like component model with built-in reactive state
- **Trade-off**: Heavier binary, requires Flutter runtime embedding

## Core Processing Libraries

| Module | Library | Purpose |
|--------|---------|---------|
| Image BG Removal | `rembg[gpu]` | ONNX Runtime inference for background removal |
| Video Download | `yt-dlp` | Media extraction, metadata, format selection |
| Image I/O | `Pillow` | Preview generation, format conversion, thumbnail |
| Async Tasks | `asyncio` + `threading` | Keep UI responsive during heavy inference/download |

## Local Data & State
- **SQLite** (`sqlite3` stdlib) — Settings, download history, simple queue
- **Pydantic** — Settings validation and typed configuration models
- **Platformdirs** — Cross-platform config/cache/output path resolution

## Build & Distribution

| Platform | Tool | Output |
|----------|------|--------|
| Linux (Arch/CachyOS) | `appimage-builder` or `PKGBUILD` | `.AppImage` or Pacman package |
| Windows | `PyInstaller` or `Nuitka` | Single `.exe` |
| macOS (Future) | `PyInstaller` + `create-dmg` | `.app` bundle |

## Environment & Packaging
- **Virtual env**: `venv` or `uv` (ultrafast Python package manager)
- **Lockfile**: `uv pip compile` or `requirements.txt` pinned versions
- **Asset bundling**: Include ONNX model files and FFmpeg binary in build spec

## Dev Tools
- **Ruff** — Linting & formatting (replaces flake8/black)
- **Pyright / Pylance** — Type checking (strict mode)
- **Pre-commit** — Git hooks for code quality