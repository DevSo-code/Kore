# Kore

**One app. Every tool. Zero ads.**

Kore is a local-first, offline-capable desktop utility suite built in Python. It consolidates everyday power-user tools (image manipulation, video downloading, file conversion) into a single, tabbed GUI with no ads, no data collection, and no internet dependency for core features.

## Features

### Image Studio
- AI-powered background removal using `rembg`
- Drag-and-drop support for images
- PNG, JPG, WEBP format support
- Side-by-side before/after preview
- GPU acceleration support (optional)

### Video Grab
- Download videos from YouTube, Vimeo, X, and 1000+ sites using `yt-dlp`
- Format and quality selection (4K, 1080p, 720p, audio-only)
- Real-time progress display with speed and ETA
- Automatic format conversion to MP4

### Spotify Downloader
- Download Spotify tracks and playlists using `spotdl`
- Multiple audio formats (MP3, M4A, OPUS)
- YouTube audio provider for better coverage
- Real-time download progress
- Download history tracking

### Settings
- Persistent configuration via SQLite
- Customizable output directory
- GPU acceleration toggle
- Theme selection (dark/light)

## Installation (Interactive Installer)

Kore comes with a fully automated, dark-themed visual installer that handles virtual environment setup, python package installation, AI model caching (`u2net.onnx`), local database seeding, and desktop launcher shortcut creation.

### Windows

1. Clone the repository and navigate to the directory.
2. Double-click or run `install.bat` in your terminal:
   ```cmd
   install.bat
   ```
   *If Python is not installed, the script will automatically download and set it up for you.*

### Linux (Ubuntu, Debian, Fedora, Arch, CachyOS, etc.)

1. Clone the repository and navigate to the directory.
2. Run the launcher script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   *The launcher will detect your system package manager (apt, dnf, pacman, etc.) and automatically install dependencies like `tkinter` and `venv` before launching the visual wizard.*

## Running the Application
Once installed, you can launch the application:
- via the **Desktop Shortcut** or **Application Launcher** created during setup.
- or by running:
  - **Windows**: `venv\Scripts\python.exe src\main.py`
  - **Linux**: `venv/bin/python src/main.py`


## Building for Distribution

### Windows (PyInstaller)

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller build/kore.spec
```

3. The executable will be in `dist/Kore.exe`

### Linux (AppImage)

1. Install `appimage-builder`:
```bash
sudo apt install appimage-builder
```

2. Build the AppImage:
```bash
appimage-builder build/appimage-builder.yml
```

## Project Structure

```
kore/
├── src/
│   ├── main.py              # Entry point
│   ├── constants.py         # Paths, colors, defaults
│   ├── ui/                  # GUI components
│   │   ├── app.py           # Main window
│   │   ├── theme.py         # CustomTkinter theme
│   │   └── tabs/            # Tab implementations
│   ├── core/                # Business logic
│   ├── models/              # Pydantic schemas
│   ├── services/            # External lib wrappers
│   ├── db/                  # SQLite repository
│   └── utils/               # Shared helpers
├── build/                   # Build configurations
├── Documentation/           # Design docs
└── requirements.txt         # Python dependencies
```

## Technology Stack

- **GUI Framework**: CustomTkinter
- **Image Processing**: rembg (ONNX Runtime)
- **Video Download**: yt-dlp
- **Spotify Download**: spotdl
- **Audio Processing**: FFmpeg
- **Database**: SQLite
- **Configuration**: Pydantic
- **Language**: Python 3.11+

## Development

### Code Style

- Ruff for linting and formatting
- Type hints with mypy/pyright
- Google-style docstrings

### Running Tests

```bash
# Run linting
ruff check src/

# Run type checking
mypy src/
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting pull requests.

## Roadmap

See [Documentation/ROADMAP.md](Documentation/ROADMAP.md) for upcoming features and phases.

## Support

For issues and questions, please open a GitHub issue.
