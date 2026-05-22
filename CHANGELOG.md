# Changelog

## [2.1.0] - 2026-05-22

### Added
- **Real-ESRGAN Image Upscaling Module**: Complete AI-powered image upscaling functionality
  - 4× to 8× super-resolution upscaling using Real-ESRGAN deep learning model
  - Adjustable scale factor slider (2×, 4×, 6×, 8×)
  - GPU acceleration toggle with automatic CPU fallback
  - Drag-and-drop image upload zone
  - Real-time progress tracking during upscaling
  - Automatic model weights download on first use
  - Image preview canvas with before/after comparison
  - Save upscaled images to custom locations
  - Database integration for processing queue tracking
  - Thread-safe async processing to avoid UI blocking

### Changed
- **Tab Navigation**: Added "Upscale" tab to sidebar navigation with ✨ icon
- **Tab Enum**: Added `REALESRGAN` to `Tab` enum in settings model
- **App Loading**: Updated app.py to load RealESRGANTab component

### Technical Details
- **Dependencies**: Added py-real-esrgan>=2.0.0, torch>=2.0.0, torchvision>=0.15.0, numpy>=1.24.0
- **Model**: RealESRGAN_x4plus.pth (downloaded automatically by py-real-esrgan)
- **Python 3.14 Compatibility**: Uses py-real-esrgan package instead of basicsr/realesrgan for better Python 3.14 support
- **Thread Safety**: All upscaling operations run in background threads with UI callbacks
- **Error Handling**: Comprehensive error handling with toast notifications

### Documentation Updates
- Created TICKET-0005 documenting Real-ESRGAN implementation
- Updated requirements.txt with new dependencies
- Updated setup_gui.py to download RealESRGAN model during installation (67 MB)
- Installation now downloads both u2net.onnx (176 MB) and RealESRGAN_x4plus.pth (67 MB) upfront

---

## [2.0.0] - 2026-05-21

### Added
- **Spotify Downloader Module**: Complete Spotify track and playlist download functionality
  - Single track download from Spotify URLs
  - Playlist download support
  - Search by text query (e.g., "Artist - Song Name")
  - Multiple audio formats (MP3, M4A, OPUS)
  - Real-time download progress tracking
  - Download history with quick access to output folder
  - Full metadata embedding (artist, album, cover art, lyrics)

### Changed
- **Architecture Improvements**:
  - Standardized on subprocess CLI approach for spotDL (removed mixed API usage)
  - Replaced stdout parsing with directory scanning for better reliability
  - Increased timeout for playlist downloads (30 minutes)
  - Increased timeout for single track downloads (10 minutes)
  - Renamed `format` parameter to `audio_format` to avoid shadowing built-in

- **Error Handling & Validation**:
  - Added ffmpeg dependency validation at startup
  - Added yt-dlp dependency validation with version check
  - Improved error messages to avoid exposing internals to users
  - Fixed subprocess encoding for Unicode support (UTF-8 with error replacement)
  - Fixed yt-dlp version check to handle missing `__version__` attribute

- **GUI Thread Safety**:
  - Implemented thread-safe UI updates using `app.after()` for all callbacks
  - Fixed Tkinter widget destruction errors when switching tabs
  - Added widget existence checks before UI updates

- **Settings & Theme**:
  - Fixed theme enum conversion error in settings tab
  - Fixed dark/light mode switching with proper enum handling

### Fixed
- Fixed CTkSegmentedButton parameter errors in Spotify tab
- Fixed Spotdl initialization errors by removing unsupported parameters
- Fixed "spotify client already initialized" error by creating new instances
- Fixed spotdl CLI argument names (`--audio-provider` → `--audio`, `--output-dir` → `--output`)
- Fixed audio_providers parameter error (removed unsupported parameter)
- Fixed error message display for failed downloads
- Fixed theme enum access causing "'str' object has no attribute 'value'" error

### Removed
- Removed unused `_spotdl_instance` variable
- Removed Python API imports (Spotdl, Song types) - now using pure subprocess CLI
- Removed `get_track_info()` method (no longer needed with subprocess approach)

### Documentation Updates
- Updated README.md with Spotify Downloader feature documentation
- Added System Requirements section documenting FFmpeg dependency
- Updated Technology Stack to include spotdl and FFmpeg
- Updated TECH_STACK.md with spotdl and ffmpeg in Core Processing Libraries
- Updated DESIGN.md layout diagram to include Spotify tab
- Updated ROADMAP.md to mark Spotify Downloader as completed in Phase 1
- Updated requirements.txt with spotdl>=4.4.0

### Technical Details
- **Dependencies**: Added spotdl>=4.4.0, requires FFmpeg system dependency
- **Audio Provider**: Uses YouTube provider instead of YouTube Music for better coverage
- **Thread Safety**: All UI callbacks now use `app.after()` for thread-safe execution
- **File Detection**: Uses directory scanning instead of stdout parsing for downloaded files
- **Encoding**: Subprocess calls use UTF-8 encoding with error replacement for Unicode support