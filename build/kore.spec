# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Kore application.

Build command:
    pyinstaller build/kore.spec
"""

import sys
from pathlib import Path

# Get the project root
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"

block_cipher = None

a = Analysis(
    [str(SRC_DIR / "main.py")],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        # Add any data files here if needed
        # (str(SRC_DIR / "assets"), "assets"),
    ],
    hiddenimports=[
        "customtkinter",
        "PIL",
        "PIL._tkinter_finder",
        "rembg",
        "yt_dlp",
        "pydantic",
        "pydantic_settings",
        "platformdirs",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "pytest",
        "setuptools",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Kore",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT_DIR / "build" / "icon.ico") if (ROOT_DIR / "build" / "icon.ico").exists() else None,
)
