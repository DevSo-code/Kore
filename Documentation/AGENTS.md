# AGENTS.md — AI Agent Roles

## Agent 1: "UI Architect" (Frontend Specialist)
**Responsibility**: Everything the user sees and interacts with.
- Builds CustomTkinter tab layout, navigation, and component hierarchy
- Implements drag-and-drop zones, image preview canvas, and progress indicators
- Manages application state (which tab is active, current file being processed)
- Ensures responsive layout at min window size 900×600px
- **Code ownership**: `src/ui/`, `src/theme.py`, `src/main.py` entry point

## Agent 2: "Core Engineer" (Backend & Logic Specialist)
**Responsibility**: All business logic, processing pipelines, and external library integration.
- Wraps `rembg` with async executor and GPU detection
- Integrates `yt-dlp` with format parsing, progress hooks, and download management
- Handles file I/O, temporary directory cleanup, and error recovery
- Implements SQLite schema access layer and Pydantic settings models
- **Code ownership**: `src/core/`, `src/models/`, `src/services/`

## Agent 3: "Build Master" (DevOps & Distribution Specialist)
**Responsibility**: Packaging, environment reproducibility, and release engineering.
- Configures PyInstaller/Nuitka spec files for Windows `.exe`
- Writes `PKGBUILD` and AppImage recipes for Linux
- Manages `requirements.txt`, asset inclusion (ONNX models, FFmpeg), and code signing
- Sets up GitHub Actions for cross-platform builds on tag push
- **Code ownership**: `build/`, `.github/workflows/`, `scripts/`, `Makefile`