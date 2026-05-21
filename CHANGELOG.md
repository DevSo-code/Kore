# Changelog

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