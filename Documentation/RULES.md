# RULES.md / .cursorrules — Coding Standards

## Language & Type Safety
- **Python 3.11+** only. No backwards compatibility for older versions.
- **Type hints everywhere**: Use `from __future__ import annotations` and strict `mypy` / `pyright` compliance.
- **No `Any` types allowed**. Use `object`, generics, or Protocols instead.
- **Pydantic models** for all configuration, settings, and external data parsing.

## Architecture
- **Modular design**: Each tab is an isolated package under `src/ui/tabs/` with its own controller.
- **Separation of concerns**: UI layer must never call `yt-dlp` or `rembg` directly. Route through `src/services/`.
- **Thread safety**: All blocking I/O and inference runs in `threading.Thread` or `asyncio.to_thread`. Never block the main GUI thread.
- **Single responsibility**: One class per file unless they are tightly coupled inner classes.

## Code Style
- **Ruff** for linting and import sorting (`isort` rules).
- **Line length**: 88 characters (Black default).
- **Docstrings**: Google style for every public module, class, and method.
- **Constants**: UPPER_SNAKE_CASE in `src/constants.py`.
- **No print statements**: Use `logging` module with structured loggers.

## Error Handling
- **Never swallow exceptions**. Every try-block must log or surface the error via the UI toast system.
- **Graceful degradation**: If GPU fails, auto-fallback to CPU with user notification.
- **User-facing errors**: Must be human-readable, not stack traces.

## Dependencies
- **Minimize external packages**: Prefer stdlib. Only add deps if they save &gt;100 lines of code.
- **Pin versions**: All deps locked in `requirements.txt` with `==` notation.
- **Optional deps**: GPU support via `rembg[gpu]` is optional; app must launch without it.

## File Organization
src/
├── main.py              # Entry point only
├── constants.py         # Paths, colors, defaults
├── ui/                  # All GUI code
│   ├── app.py           # Root window controller
│   ├── theme.py         # Color tokens & fonts
│   └── tabs/            # Per-tab packages
├── core/                # Business logic
│   ├── image_processor.py
│   └── video_downloader.py
├── models/              # Pydantic schemas
├── services/            # External lib wrappers
├── db/                  # SQLite repository layer
└── utils/               # Shared helpers