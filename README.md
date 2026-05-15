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

### Settings
- Persistent configuration via SQLite
- Customizable output directory
- GPU acceleration toggle
- Theme selection (dark/light)

## Installation

### Prerequisites
- Python 3.11 or higher (tested on 3.14)
- pip package manager
- tkinter (system package)

#### System Dependencies

**Arch Linux / CachyOS:**
```bash
sudo pacman -S tk
```

**Ubuntu/Debian:**
```bash
sudo apt install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kore.git
cd kore
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python src/main.py
```

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
