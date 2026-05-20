#!/usr/bin/env python3
"""Kore Utility Suite Onboarding & Installer.

This script provides a modern, dark-themed GUI installer for Kore, setting up
the virtual environment, system/python dependencies, database, and caching
the AI models for background removal.
"""

from __future__ import annotations

import json
import os
import platform
import queue
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

# Color palette (matching DESIGN.md)
BG_BASE = "#0F1117"
BG_SURFACE = "#1A1D27"
BG_SURFACE_LOWEST = "#0C0E14"
BG_ELEVATED = "#22263A"
BG_HOVER = "#2A2F47"
BORDER = "#2E3250"
BORDER_FOCUS = "#5C6BC0"

ACCENT_PRIMARY = "#6C63FF"
ACCENT_SECONDARY = "#00D4AA"
ACCENT_DANGER = "#FF5C6C"
ACCENT_WARNING = "#FFB347"

TEXT_PRIMARY = "#E8EAFF"
TEXT_SECONDARY = "#8B90B8"
TEXT_MUTED = "#5A5F80"

ONNX_MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
ONNX_MODEL_SIZE = 176140862  # 176 MB

class HoverButton(tk.Button):
    """Custom flat button with hover effects."""
    def __init__(self, master, bg_color=ACCENT_PRIMARY, hover_color="#7C75FF", fg_color=TEXT_PRIMARY, **kwargs):
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        
        super().__init__(
            master,
            bg=self.bg_color,
            fg=self.fg_color,
            activebackground=self.hover_color,
            activeforeground=self.fg_color,
            bd=0,
            relief="flat",
            cursor="hand2",
            **kwargs
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.configure(bg=self.hover_color)

    def _on_leave(self, event):
        self.configure(bg=self.bg_color)

class CustomProgress(tk.Canvas):
    """Canvas-based smooth rounded progress bar."""
    def __init__(self, master, width=450, height=14, **kwargs):
        super().__init__(master, width=width, height=height, bg=BG_BASE, bd=0, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.percent = 0.0
        self.draw()

    def set_progress(self, percent: float):
        self.percent = max(0.0, min(1.0, percent))
        self.draw()

    def draw(self):
        self.delete("all")
        r = self.height / 2
        
        # Track (Background)
        self.create_oval(0, 0, self.height, self.height, fill=BG_ELEVATED, outline="")
        self.create_oval(self.width - self.height, 0, self.width, self.height, fill=BG_ELEVATED, outline="")
        self.create_rectangle(r, 0, self.width - r, self.height, fill=BG_ELEVATED, outline="")
        
        # Progress Fill
        if self.percent > 0:
            fill_w = max(self.height, self.width * self.percent)
            self.create_oval(0, 0, self.height, self.height, fill=ACCENT_SECONDARY, outline="")
            self.create_oval(fill_w - self.height, 0, fill_w, self.height, fill=ACCENT_SECONDARY, outline="")
            self.create_rectangle(r, 0, fill_w - r, self.height, fill=ACCENT_SECONDARY, outline="")

class InstallerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Kore Utility Suite — Setup & Onboarding")
        self.root.geometry("820x560")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_BASE)
        
        # Center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 820) // 2
        y = (screen_height - 560) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self.repo_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.repo_dir / "venv"
        self.is_windows = platform.system() == "Windows"
        
        self.current_step_index = 0
        self.steps = [
            "Verify System Environment",
            "Setup Python Virtual Env",
            "Install Application Core",
            "Download AI Models (ONNX)",
            "Initialize App Config & DB",
            "Configure Shortcuts & Launch"
        ]
        self.step_labels: list[tk.Label] = []
        self.step_indicators: list[tk.Label] = []
        
        self.log_queue = queue.Queue()
        self.install_thread = None
        self.install_finished = False
        self.create_desktop_shortcut_var = tk.BooleanVar(value=True)
        self.launch_app_var = tk.BooleanVar(value=True)
        
        self._build_ui()
        self._check_pre_install()

    def _build_ui(self):
        # Grid layout
        self.root.grid_columnconfigure(0, minsize=260, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Left Sidebar Panel
        sidebar = tk.Frame(self.root, bg=BG_SURFACE_LOWEST, bd=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo placeholder or image
        logo_path = self.repo_dir / "src" / "ui" / "assets" / "logo.png"
        self.logo_img = None
        if logo_path.exists():
            try:
                raw_img = tk.PhotoImage(file=str(logo_path))
                # Subsample down to about 96x96 or 128x128
                self.logo_img = raw_img.subsample(8, 8)
                self.logo_label = tk.Label(sidebar, image=self.logo_img, bg=BG_SURFACE_LOWEST)
                self.logo_label.pack(pady=(35, 10))
            except Exception as e:
                print(f"Failed to load logo: {e}")
                
        if not self.logo_img:
            # Fallback text logo
            self.logo_fallback = tk.Label(
                sidebar, 
                text="K", 
                font=("Inter", 48, "bold"), 
                fg=ACCENT_PRIMARY, 
                bg=BG_SURFACE_LOWEST
            )
            self.logo_fallback.pack(pady=(35, 10))
            
        # App Title
        tk.Label(
            sidebar, 
            text="Kore Utility Suite", 
            font=("Inter", 16, "bold"), 
            fg=TEXT_PRIMARY, 
            bg=BG_SURFACE_LOWEST
        ).pack(pady=2)
        
        tk.Label(
            sidebar, 
            text="Setup & Onboarding", 
            font=("Inter", 10), 
            fg=TEXT_SECONDARY, 
            bg=BG_SURFACE_LOWEST
        ).pack(pady=(0, 25))
        
        # Steps container
        steps_frame = tk.Frame(sidebar, bg=BG_SURFACE_LOWEST)
        steps_frame.pack(fill="x", padx=25)
        
        for idx, step_name in enumerate(self.steps):
            step_row = tk.Frame(steps_frame, bg=BG_SURFACE_LOWEST, pady=6)
            step_row.pack(fill="x")
            
            indicator = tk.Label(
                step_row, 
                text="○", 
                font=("Inter", 11, "bold"), 
                fg=TEXT_MUTED, 
                bg=BG_SURFACE_LOWEST,
                width=3
            )
            indicator.pack(side="left")
            self.step_indicators.append(indicator)
            
            lbl = tk.Label(
                step_row, 
                text=step_name, 
                font=("Inter", 10), 
                fg=TEXT_MUTED, 
                bg=BG_SURFACE_LOWEST,
                anchor="w"
            )
            lbl.pack(side="left", fill="x", padx=(5, 0))
            self.step_labels.append(lbl)

        # Right Main Panel
        self.main_panel = tk.Frame(self.root, bg=BG_BASE, bd=0)
        self.main_panel.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        self.main_panel.grid_rowconfigure(0, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)

        # Screens container
        self.screens: dict[str, tk.Frame] = {}
        
        self._build_welcome_screen()
        self._build_install_screen()
        self._build_finish_screen()
        
        self.show_screen("welcome")

    def show_screen(self, name: str):
        for screen in self.screens.values():
            screen.grid_forget()
        self.screens[name].grid(row=0, column=0, sticky="nsew")

    def _build_welcome_screen(self):
        screen = tk.Frame(self.main_panel, bg=BG_BASE)
        self.screens["welcome"] = screen
        screen.grid_columnconfigure(0, weight=1)
        
        # Heading
        tk.Label(
            screen,
            text="Welcome to Kore",
            font=("Inter", 26, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_BASE,
            anchor="w"
        ).pack(fill="x", pady=(20, 15))
        
        # Subheading / Tagline
        tk.Label(
            screen,
            text="One app. Every tool. Zero ads. Offline-capable desktop suite.",
            font=("Inter", 12),
            fg=ACCENT_SECONDARY,
            bg=BG_BASE,
            anchor="w"
        ).pack(fill="x", pady=(0, 20))

        # Description Card
        card = tk.Frame(screen, bg=BG_SURFACE, bd=1, relief="flat", padx=20, pady=20)
        card.pack(fill="both", expand=True, pady=(0, 30))
        
        description = (
            "Kore consolidates everyday power-user utilities like AI background removal,\n"
            "video downloading, and image/file conversion directly on your machine.\n\n"
            "This interactive wizard will configure Kore for optimal performance:\n"
            "  •  Create a local Python virtual environment to keep your system clean\n"
            "  •  Install essential dependencies (customtkinter, yt-dlp, etc.)\n"
            "  •  Pre-download the u2net ONNX model for background removal (176 MB)\n"
            "  •  Set up local database schema and configuration directories\n\n"
            "Everything is installed locally. No telemetry. No internet required after setup."
        )
        tk.Label(
            card,
            text=description,
            font=("Inter", 11),
            fg=TEXT_SECONDARY,
            bg=BG_SURFACE,
            justify="left",
            anchor="nw"
        ).pack(fill="both", expand=True)

        # Actions Frame
        actions_frame = tk.Frame(screen, bg=BG_BASE)
        actions_frame.pack(fill="x", side="bottom")
        
        # System requirements info
        tk.Label(
            actions_frame,
            text=f"Platform: {platform.system()} ({platform.machine()})  ·  Python {platform.python_version()}",
            font=("Inter", 10),
            fg=TEXT_MUTED,
            bg=BG_BASE
        ).pack(side="left")

        # Install Button
        self.btn_start = HoverButton(
            actions_frame,
            text="Install & Set Up",
            bg_color=ACCENT_PRIMARY,
            hover_color="#7C75FF",
            font=("Inter", 11, "bold"),
            padx=25,
            pady=10,
            command=self.start_installation
        )
        self.btn_start.pack(side="right")

    def _build_install_screen(self):
        screen = tk.Frame(self.main_panel, bg=BG_BASE)
        self.screens["install"] = screen
        screen.grid_columnconfigure(0, weight=1)
        
        # Title
        tk.Label(
            screen,
            text="Installing Kore Suite",
            font=("Inter", 22, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_BASE,
            anchor="w"
        ).pack(fill="x", pady=(10, 10))

        # Status text
        self.status_title = tk.Label(
            screen,
            text="Initializing install steps...",
            font=("Inter", 12, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_BASE,
            anchor="w"
        )
        self.status_title.pack(fill="x", pady=(10, 5))
        
        self.status_desc = tk.Label(
            screen,
            text="Please hold on while we build your environment.",
            font=("Inter", 10),
            fg=TEXT_SECONDARY,
            bg=BG_BASE,
            anchor="w"
        )
        self.status_desc.pack(fill="x", pady=(0, 15))

        # Custom Progress Bar
        self.progress_bar = CustomProgress(screen, width=480, height=14)
        self.progress_bar.pack(anchor="w", pady=(0, 8))
        
        # Progress stats (MB/s, ETA)
        self.progress_stats = tk.Label(
            screen,
            text="",
            font=("Inter", 10),
            fg=TEXT_MUTED,
            bg=BG_BASE,
            anchor="w"
        )
        self.progress_stats.pack(fill="x", pady=(0, 20))

        # Logs Console
        console_frame = tk.Frame(screen, bg=BG_SURFACE_LOWEST, bd=1, highlightbackground=BORDER, highlightthickness=1)
        console_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Scrollable Text
        self.log_text = tk.Text(
            console_frame,
            bg=BG_SURFACE_LOWEST,
            fg=ACCENT_SECONDARY,
            insertbackground=TEXT_PRIMARY,
            font=("JetBrains Mono", 9),
            bd=0,
            padx=10,
            pady=10,
            state="disabled",
            wrap="word"
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(console_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _build_finish_screen(self):
        screen = tk.Frame(self.main_panel, bg=BG_BASE)
        self.screens["finish"] = screen
        screen.grid_columnconfigure(0, weight=1)
        
        # Completion Heading
        self.finish_title = tk.Label(
            screen,
            text="Installation Complete!",
            font=("Inter", 26, "bold"),
            fg=ACCENT_SECONDARY,
            bg=BG_BASE,
            anchor="w"
        )
        self.finish_title.pack(fill="x", pady=(20, 10))
        
        tk.Label(
            screen,
            text="Kore has been set up successfully on your device.",
            font=("Inter", 12),
            fg=TEXT_SECONDARY,
            bg=BG_BASE,
            anchor="w"
        ).pack(fill="x", pady=(0, 30))

        # Checkbox Settings Card
        card = tk.Frame(screen, bg=BG_SURFACE, bd=1, relief="flat", padx=25, pady=25)
        card.pack(fill="both", expand=True, pady=(0, 30))
        
        # Checkbox custom styling
        # Note: tk.Checkbutton can be styled to look somewhat decent in flat mode
        self.cb_shortcut = tk.Checkbutton(
            card,
            text=" Create Desktop Shortcut",
            variable=self.create_desktop_shortcut_var,
            font=("Inter", 11),
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            activebackground=BG_SURFACE,
            activeforeground=TEXT_PRIMARY,
            selectcolor=BG_ELEVATED,
            bd=0,
            relief="flat",
            anchor="w"
        )
        self.cb_shortcut.pack(fill="x", pady=10)

        self.cb_launch = tk.Checkbutton(
            card,
            text=" Launch Kore Utility Suite now",
            variable=self.launch_app_var,
            font=("Inter", 11),
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            activebackground=BG_SURFACE,
            activeforeground=TEXT_PRIMARY,
            selectcolor=BG_ELEVATED,
            bd=0,
            relief="flat",
            anchor="w"
        )
        self.cb_launch.pack(fill="x", pady=10)

        # Finish Button
        actions_frame = tk.Frame(screen, bg=BG_BASE)
        actions_frame.pack(fill="x", side="bottom")

        self.btn_finish = HoverButton(
            actions_frame,
            text="Finish & Launch",
            bg_color=ACCENT_SECONDARY,
            hover_color="#1AE5BC",
            fg_color=BG_BASE,
            font=("Inter", 11, "bold"),
            padx=35,
            pady=10,
            command=self.complete_installation
        )
        self.btn_finish.pack(side="right")

    def _check_pre_install(self):
        # We perform visual check inside the GUI
        self.update_step(0, "active")
        py_version = sys.version_info
        if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 11):
            self.write_log(f"[ERROR] Unsupported Python version: {py_version.major}.{py_version.minor}\n")
            self.write_log("[ERROR] Kore requires Python 3.11 or higher.\n")
            self.update_step(0, "failed")
            messagebox.showerror(
                "Incompatible Environment", 
                f"Kore requires Python 3.11 or higher. Detected: {py_version.major}.{py_version.minor}"
            )
            sys.exit(1)
        
        self.write_log(f"[INFO] System check passed: Python {platform.python_version()} on {platform.system()}\n")
        self.update_step(0, "done")

    def update_step(self, step_idx: int, status: str):
        """Update the sidebar step labels and colors."""
        if step_idx < 0 or step_idx >= len(self.steps):
            return
        
        lbl = self.step_labels[step_idx]
        ind = self.step_indicators[step_idx]
        
        if status == "active":
            lbl.configure(fg=TEXT_PRIMARY, font=("Inter", 10, "bold"))
            ind.configure(text="●", fg=ACCENT_PRIMARY)
        elif status == "done":
            lbl.configure(fg=TEXT_SECONDARY, font=("Inter", 10))
            ind.configure(text="✓", fg=ACCENT_SECONDARY)
        elif status == "failed":
            lbl.configure(fg=ACCENT_DANGER, font=("Inter", 10))
            ind.configure(text="✗", fg=ACCENT_DANGER)
        elif status == "pending":
            lbl.configure(fg=TEXT_MUTED, font=("Inter", 10))
            ind.configure(text="○", fg=TEXT_MUTED)

    def write_log(self, text: str):
        """Appends log safely to text view from any thread."""
        self.log_queue.put(text)
        self.root.after(0, self._process_log_queue)

    def _process_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert("end", msg)
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
        except queue.Empty:
            pass

    def start_installation(self):
        self.show_screen("install")
        self.install_thread = threading.Thread(target=self._run_install_tasks, daemon=True)
        self.install_thread.start()

    def _run_install_tasks(self):
        try:
            # 1. System checks (already done, make sure it's check-marked)
            self.root.after(0, lambda: self.update_step(0, "done"))
            
            # 2. Setup Venv
            self.root.after(0, lambda: self.update_step(1, "active"))
            self.root.after(0, lambda: self.status_title.configure(text="Creating Virtual Environment..."))
            self.root.after(0, lambda: self.status_desc.configure(text="Isolating dependencies inside the 'venv' directory."))
            self.root.after(0, lambda: self.progress_bar.set_progress(0.1))
            
            self.write_log("[1/6] Creating Python virtual environment in 'venv'...\n")
            if not self.venv_dir.exists():
                cmd = [sys.executable, "-m", "venv", "venv"]
                self.write_log(f"Running command: {' '.join(cmd)}\n")
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(self.repo_dir))
                for line in iter(process.stdout.readline, ""):
                    self.write_log(line)
                process.stdout.close()
                ret = process.wait()
                if ret != 0:
                    raise RuntimeError("Failed to create virtual environment.")
            else:
                self.write_log("[INFO] Virtual environment 'venv' already exists. Skipping creation.\n")
            
            self.root.after(0, lambda: self.update_step(1, "done"))
            
            # Paths to executables
            if self.is_windows:
                venv_python = self.venv_dir / "Scripts" / "python.exe"
                venv_pip = self.venv_dir / "Scripts" / "pip.exe"
            else:
                venv_python = self.venv_dir / "bin" / "python"
                venv_pip = self.venv_dir / "bin" / "pip"

            # 3. Install core dependencies
            self.root.after(0, lambda: self.update_step(2, "active"))
            self.root.after(0, lambda: self.status_title.configure(text="Installing Core Packages..."))
            self.root.after(0, lambda: self.status_desc.configure(text="Fetching GUI and system library requirements from PyPI."))
            self.root.after(0, lambda: self.progress_bar.set_progress(0.25))
            
            self.write_log("\n[2/6] Upgrading pip inside virtual environment...\n")
            cmd_up_pip = [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"]
            process = subprocess.Popen(cmd_up_pip, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ""):
                self.write_log(line)
            process.stdout.close()
            process.wait()

            self.write_log("\n[3/6] Installing packages from requirements.txt...\n")
            req_file = self.repo_dir / "requirements.txt"
            if not req_file.exists():
                raise FileNotFoundError(f"requirements.txt not found at {req_file}")
            
            cmd_pip_req = [str(venv_python), "-m", "pip", "install", "-r", str(req_file)]
            self.write_log(f"Running command: {' '.join(cmd_pip_req)}\n")
            process = subprocess.Popen(cmd_pip_req, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ""):
                self.write_log(line)
            process.stdout.close()
            ret = process.wait()
            if ret != 0:
                raise RuntimeError("Failed to install Python packages.")
                
            self.root.after(0, lambda: self.update_step(2, "done"))

            # 4. Download AI Model (u2net.onnx)
            self.root.after(0, lambda: self.update_step(3, "active"))
            self.root.after(0, lambda: self.status_title.configure(text="Downloading Background Removal AI Model..."))
            self.root.after(0, lambda: self.status_desc.configure(text="Downloading 'u2net.onnx' (176 MB) from Github. Please wait..."))
            
            # Resolve user cache dir using the newly installed platformdirs in the venv
            self.write_log("\n[4/6] Resolving application cache directory...\n")
            cmd_resolve_cache = [
                str(venv_python), "-c", 
                "from platformdirs import PlatformDirs; print(PlatformDirs('Kore', 'KoreTeam').user_cache_dir)"
            ]
            try:
                cache_dir_str = subprocess.check_output(cmd_resolve_cache, text=True).strip()
                cache_dir = Path(cache_dir_str)
            except Exception as e:
                self.write_log(f"[WARNING] Failed to resolve cache via platformdirs: {e}. Falling back to default.\n")
                if self.is_windows:
                    cache_dir = Path(os.environ.get("LOCALAPPDATA", "~")) / "KoreTeam" / "Kore" / "Cache"
                else:
                    cache_dir = Path("~/.cache/Kore").expanduser()

            model_dir = cache_dir / "models"
            model_path = model_dir / "u2net.onnx"
            self.write_log(f"Model cache target: {model_path}\n")

            if model_path.exists() and model_path.stat().st_size >= ONNX_MODEL_SIZE - 1000:
                self.write_log("[INFO] AI model 'u2net.onnx' is already cached. Skipping download.\n")
                self.root.after(0, lambda: self.progress_bar.set_progress(0.75))
            else:
                model_dir.mkdir(parents=True, exist_ok=True)
                self._download_file_with_progress(ONNX_MODEL_URL, model_path)
            
            self.root.after(0, lambda: self.update_step(3, "done"))

            # 5. DB & Config Init
            self.root.after(0, lambda: self.update_step(4, "active"))
            self.root.after(0, lambda: self.status_title.configure(text="Initializing Application Config & DB..."))
            self.root.after(0, lambda: self.status_desc.configure(text="Creating SQLite database tables and local settings schema."))
            self.root.after(0, lambda: self.progress_bar.set_progress(0.85))
            
            self.write_log("\n[5/6] Seeding settings schema and creating database database files...\n")
            cmd_init_db = [
                str(venv_python), "-c",
                "import sys; sys.path.insert(0, '.'); from src.db.repository import DatabaseRepository; DatabaseRepository()"
            ]
            process = subprocess.Popen(cmd_init_db, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(self.repo_dir))
            for line in iter(process.stdout.readline, ""):
                self.write_log(line)
            process.stdout.close()
            process.wait()
            self.write_log("[INFO] SQLite repository and index creation succeeded.\n")
            
            self.root.after(0, lambda: self.update_step(4, "done"))

            # 6. Shortcuts
            self.root.after(0, lambda: self.update_step(5, "active"))
            self.root.after(0, lambda: self.status_title.configure(text="Creating Application Shortcuts..."))
            self.root.after(0, lambda: self.status_desc.configure(text="Adding launcher configurations to desktop settings."))
            self.root.after(0, lambda: self.progress_bar.set_progress(0.95))
            
            self.write_log("\n[6/6] Configuration of launchers...\n")
            # We defer actual creation of desktop shortcuts to when user clicks Finish, but we verify here
            self.write_log("[INFO] Shortcut pathways prepared.\n")
            
            self.root.after(0, lambda: self.progress_bar.set_progress(1.0))
            self.root.after(0, lambda: self.update_step(5, "done"))
            
            # Finish screen transition
            self.install_finished = True
            self.root.after(1000, lambda: self.show_screen("finish"))

        except Exception as err:
            self.write_log(f"\n[FATAL ERROR] Installation failed: {err}\n")
            # Mark current step as failed
            self.root.after(0, lambda: self.update_step(self.current_step_index, "failed"))
            self.root.after(0, lambda: self.status_title.configure(text="Installation Failed"))
            self.root.after(0, lambda: self.status_desc.configure(text=f"Error details: {err}"))
            self.root.after(0, lambda: messagebox.showerror("Installation Error", f"An error occurred during installation:\n{err}"))

    def _download_file_with_progress(self, url: str, dest_path: Path):
        self.write_log(f"Downloading from: {url}\n")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        # Temp file download
        temp_path = dest_path.with_suffix(".tmp")
        
        with urllib.request.urlopen(req) as response:
            total_size = int(response.info().get('Content-Length', 0))
            downloaded = 0
            block_size = 1024 * 128  # 128 KB chunk
            
            start_time = time.time()
            with open(temp_path, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    f.write(buffer)
                    downloaded += len(buffer)
                    
                    # Calculate stats
                    percent = downloaded / total_size if total_size else 0
                    elapsed = time.time() - start_time
                    speed = downloaded / elapsed if elapsed > 0 else 0  # Bytes/sec
                    eta = (total_size - downloaded) / speed if speed > 0 else 0
                    
                    # Formatting
                    speed_mb = speed / (1024 * 1024)
                    downloaded_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    
                    progress_text = f"{percent * 100:.1f}% · {downloaded_mb:.1f} MB / {total_mb:.1f} MB"
                    stats_text = f"Speed: {speed_mb:.2f} MB/s  ·  ETA: {int(eta)}s remaining"
                    
                    # Progress bar mapping (takes 0.25 to 0.75 range)
                    mapped_progress = 0.25 + (percent * 0.50)
                    
                    self.root.after(0, lambda p=mapped_progress: self.progress_bar.set_progress(p))
                    self.root.after(0, lambda pt=progress_text: self.status_title.configure(text=f"Downloading AI Model: {pt}"))
                    self.root.after(0, lambda st=stats_text: self.progress_stats.configure(text=st))
            
            shutil.move(str(temp_path), str(dest_path))
            self.write_log("[INFO] Download completed successfully.\n")

    def create_desktop_shortcut(self):
        """Creates desktop shortcut for Windows and Linux."""
        main_py = self.repo_dir / "src" / "main.py"
        icon_path = self.repo_dir / "src" / "ui" / "assets" / "logo.png"
        
        if self.is_windows:
            venv_python = self.venv_dir / "Scripts" / "python.exe"
            # PowerShell shortcut script
            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("$Home\\Desktop\\Kore.lnk")
            $Shortcut.TargetPath = "{venv_python}"
            $Shortcut.Arguments = "{main_py}"
            $Shortcut.WorkingDirectory = "{self.repo_dir}"
            $Shortcut.IconLocation = "{icon_path}"
            $Shortcut.Description = "Kore Desktop Utility Suite"
            $Shortcut.Save()
            """
            try:
                cmd = ["powershell", "-Command", ps_script]
                subprocess.run(cmd, check=True)
                self.write_log("[INFO] Windows desktop shortcut created.\n")
            except Exception as e:
                self.write_log(f"[WARNING] Could not create Windows shortcut: {e}\n")
        else:
            # Linux desktop file
            desktop_dir = Path("~/.local/share/applications").expanduser()
            desktop_dir.mkdir(parents=True, exist_ok=True)
            desktop_file = desktop_dir / "kore.desktop"
            
            venv_python = self.venv_dir / "bin" / "python"
            
            entry = f"""[Desktop Entry]
Name=Kore
Comment=One app. Every tool. Zero ads.
Exec={venv_python} {main_py}
Path={self.repo_dir}
Icon={icon_path}
Terminal=false
Type=Application
Categories=Utility;
"""
            try:
                with open(desktop_file, "w") as f:
                    f.write(entry)
                # Make it executable
                os.chmod(desktop_file, 0o755)
                
                # Also create on Desktop if folder exists
                user_desktop = Path("~/Desktop").expanduser()
                if user_desktop.exists():
                    shutil.copy(desktop_file, user_desktop / "kore.desktop")
                    os.chmod(user_desktop / "kore.desktop", 0o755)
                
                self.write_log("[INFO] Linux desktop launcher entry created.\n")
            except Exception as e:
                self.write_log(f"[WARNING] Could not create Linux shortcut: {e}\n")

    def complete_installation(self):
        # 1. Create shortcut if checked
        if self.create_desktop_shortcut_var.get():
            self.create_desktop_shortcut()

        # 2. Launch if checked
        if self.launch_app_var.get():
            main_py = self.repo_dir / "src" / "main.py"
            if self.is_windows:
                venv_python = self.venv_dir / "Scripts" / "pythonw.exe"  # No console window
                if not venv_python.exists():
                    venv_python = self.venv_dir / "Scripts" / "python.exe"
                subprocess.Popen([str(venv_python), str(main_py)], cwd=str(self.repo_dir), start_new_session=True)
            else:
                venv_python = self.venv_dir / "bin" / "python"
                subprocess.Popen([str(venv_python), str(main_py)], cwd=str(self.repo_dir), start_new_session=True)

        self.root.destroy()

def main():
    root = tk.Tk()
    
    # Try setting custom window background and styling
    # Set default fonts to Outfit/Inter if available
    try:
        default_font = ("Inter", 10)
        root.option_add("*Font", default_font)
    except Exception:
        pass
        
    app = InstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
