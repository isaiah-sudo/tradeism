"""
Automatic updater for Day Trading Simulator.
Checks GitHub releases, downloads update assets, and applies updates seamlessly.
"""

import os
import sys
import json
import time
import shutil
import tempfile
import threading
import subprocess
import webbrowser
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Tuple, Callable

from version import __version__, GITHUB_REPO, APP_NAME


def parse_version(ver_str: str) -> Tuple[int, ...]:
    """Parse version string like 'v1.1.0' or '1.2.3' into a numeric tuple for comparison."""
    if not ver_str:
        return (0, 0, 0)
    cleaned = ver_str.strip().lstrip("vV")
    parts = []
    for piece in cleaned.split("."):
        numeric = ""
        for char in piece:
            if char.isdigit():
                numeric += char
            else:
                break
        parts.append(int(numeric) if numeric else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def check_for_update(current_version: str = __version__, repo: str = GITHUB_REPO, timeout: int = 8) -> Dict[str, Any]:
    """
    Queries GitHub API for the latest release and checks if a newer version is available.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {
        "User-Agent": f"DayTradeSim-Updater/{current_version}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                return {"update_available": False, "error": f"HTTP {response.status}"}
            raw = response.read().decode("utf-8")
            data = json.loads(raw)

        latest_tag = data.get("tag_name", "").strip()
        current_v = parse_version(current_version)
        latest_v = parse_version(latest_tag)

        update_available = latest_v > current_v

        # Categorize available release assets
        assets = data.get("assets", [])
        installer_asset = None
        portable_asset = None

        for asset in assets:
            name = asset.get("name", "").lower()
            if "setup" in name and name.endswith(".exe"):
                installer_asset = asset
            elif name.endswith(".exe") and "setup" not in name:
                portable_asset = asset

        # Decide preferred asset
        # If running as installed (has unins000.exe or installer available), prefer installer
        selected_asset = installer_asset or portable_asset or (assets[0] if assets else None)

        return {
            "update_available": update_available,
            "current_version": current_version,
            "latest_version": latest_tag.lstrip("vV") if latest_tag else current_version,
            "tag_name": latest_tag,
            "release_name": data.get("name") or latest_tag,
            "release_notes": data.get("body") or "No release notes provided.",
            "release_url": data.get("html_url") or f"https://github.com/{repo}/releases/latest",
            "installer_asset": installer_asset,
            "portable_asset": portable_asset,
            "selected_asset": selected_asset,
            "published_at": data.get("published_at", "")
        }
    except urllib.error.HTTPError as e:
        return {"update_available": False, "error": f"GitHub API error: {e.code} {e.reason}"}
    except urllib.error.URLError as e:
        return {"update_available": False, "error": f"Connection error: {e.reason}"}
    except Exception as e:
        return {"update_available": False, "error": str(e)}


def download_file(
    url: str,
    dest_path: str,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    cancel_event: Optional[threading.Event] = None
) -> bool:
    """
    Downloads a file with chunked streaming and progress reporting.
    """
    headers = {"User-Agent": f"DayTradeSim-Updater/{__version__}"}
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 65536  # 64 KB

            with open(dest_path, "wb") as f:
                while True:
                    if cancel_event and cancel_event.is_set():
                        return False
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)
        return True
    except Exception as e:
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                pass
        raise e


def build_update_script(
    downloaded_file: str,
    target_exe: str,
    parent_pid: int,
    is_installer: bool = True
) -> str:
    """
    Constructs the helper Windows batch script content to apply update and restart the app.
    Unsets PyInstaller temporary environment variables (_MEIPASS2, etc.) to prevent DLL load errors.
    """
    downloaded_file = os.path.abspath(downloaded_file)
    target_exe = os.path.abspath(target_exe)
    target_dir = os.path.dirname(target_exe)

    if is_installer:
        return f"""@echo off
setlocal
:: 1. Clear PyInstaller and Python environment variables so the relaunched application unpacks freshly
set _MEIPASS2=
set _MEIPASS=
set PYTHONHOME=
set PYTHONPATH=
set TCL_LIBRARY=
set TK_LIBRARY=
set PYI_SPLASH_IPC=

:: 2. Wait for parent application process (PID {parent_pid}) to completely terminate and release file locks
set RETRIES=0
:wait_parent
tasklist /FI "PID eq {parent_pid}" 2>nul | findstr /C:"{parent_pid}" >nul
if %ERRORLEVEL% equ 0 (
    set /a RETRIES+=1
    if %RETRIES% leq 30 (
        timeout /t 1 /nobreak >nul
        goto wait_parent
    )
)
timeout /t 2 /nobreak >nul

:: 3. Execute Inno Setup installer silently and WAIT until completion
start /wait "" "{downloaded_file}" /SILENT /SP- /SUPPRESSMSGBOXES /NORESTART

:: 4. Small pause to ensure file handles and temporary directories are released
timeout /t 1 /nobreak >nul

:: 5. Launch newly installed application with clean environment
if exist "{target_exe}" (
    start "" /D "{target_dir}" "{target_exe}"
)

:: 6. Self delete runner batch file
(goto) 2>nul & del "%~f0"
"""
    else:
        return f"""@echo off
setlocal
:: 1. Clear PyInstaller and Python environment variables so the relaunched application unpacks freshly
set _MEIPASS2=
set _MEIPASS=
set PYTHONHOME=
set PYTHONPATH=
set TCL_LIBRARY=
set TK_LIBRARY=
set PYI_SPLASH_IPC=

:: 2. Wait for parent application process (PID {parent_pid}) to completely terminate and release file locks
set RETRIES=0
:wait_parent
tasklist /FI "PID eq {parent_pid}" 2>nul | findstr /C:"{parent_pid}" >nul
if %ERRORLEVEL% equ 0 (
    set /a RETRIES+=1
    if %RETRIES% leq 30 (
        timeout /t 1 /nobreak >nul
        goto wait_parent
    )
)
timeout /t 2 /nobreak >nul

:: 3. Overwrite current executable with updated file (with retry loop for transient locks)
set COPY_RETRIES=0
:copy_loop
copy /y "{downloaded_file}" "{target_exe}" >nul
if %ERRORLEVEL% neq 0 (
    set /a COPY_RETRIES+=1
    if %COPY_RETRIES% leq 15 (
        timeout /t 1 /nobreak >nul
        goto copy_loop
    )
)
del /f /q "{downloaded_file}" >nul

:: 4. Launch updated application with clean environment
if exist "{target_exe}" (
    start "" /D "{target_dir}" "{target_exe}"
)

:: 5. Self delete runner batch file
(goto) 2>nul & del "%~f0"
"""


def apply_update_and_restart(downloaded_file: str, is_installer: bool = True) -> None:
    """
    Applies the downloaded update and relaunches the application.
    Executes a detached helper batch script so DayTradeSim can terminate cleanly.
    """
    current_exe = sys.executable
    is_frozen = getattr(sys, "frozen", False)
    current_pid = os.getpid()
    temp_dir = tempfile.gettempdir()
    runner_bat = os.path.join(temp_dir, "daytradesim_update_runner.bat")

    if is_frozen or not is_installer:
        target_exe = current_exe
    else:
        # If running from python source in development mode
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Day Trading Simulator\DayTradeSim.exe"),
            os.path.expandvars(r"%ProgramFiles%\Day Trading Simulator\DayTradeSim.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Day Trading Simulator\DayTradeSim.exe"),
        ]
        target_exe = next((cand for cand in candidates if os.path.exists(cand)), candidates[0])

    bat_content = build_update_script(
        downloaded_file=downloaded_file,
        target_exe=target_exe,
        parent_pid=current_pid,
        is_installer=is_installer
    )

    with open(runner_bat, "w", encoding="utf-8") as f:
        f.write(bat_content)

    # Clean PyInstaller environment variables in child process
    clean_env = os.environ.copy()
    for key in [
        "_MEIPASS2",
        "_MEIPASS",
        "PYTHONPATH",
        "PYTHONHOME",
        "TCL_LIBRARY",
        "TK_LIBRARY",
        "PYI_SPLASH_IPC",
    ]:
        clean_env.pop(key, None)

    # Spawn runner script detached with no console window
    CREATE_NO_WINDOW = 0x08000000
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    subprocess.Popen(
        ["cmd.exe", "/c", runner_bat],
        creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP,
        env=clean_env,
        close_fds=True
    )

    # Exit immediately
    sys.exit(0)


class UpdateDialog(tk.Toplevel):
    """
    Dark-themed modern Update Dialog showing version details,
    release notes, interactive progress bar, and one-click auto-install.
    """
    THEME_BG = "#0e1117"
    CARD_BG = "#161a25"
    BORDER_COLOR = "#2a2e39"
    GREEN = "#00e676"
    BLUE = "#2962ff"
    TEXT_MUTED = "#848e9c"

    def __init__(self, parent, update_info: Dict[str, Any]):
        super().__init__(parent)
        self.update_info = update_info
        self.cancel_event = threading.Event()
        self.is_downloading = False

        self.title(f"⚡ Update Available • v{self.update_info.get('latest_version', '')}")
        self.geometry("560x520")
        self.minsize(520, 460)
        self.resizable(True, True)
        self.configure(bg=self.THEME_BG)
        self.transient(parent)
        self.grab_set()

        self._center_window(parent)
        self._build_ui()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width() or 860
        ph = parent.winfo_height() or 580
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        self.geometry(f"+{px + (pw - 560)//2}+{py + (ph - 520)//2}")

    def _build_ui(self):
        # 1. Action Buttons - PACKED TO BOTTOM FIRST so they are NEVER cut off
        btn_f = tk.Frame(self, bg=self.THEME_BG)
        btn_f.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=(10, 18))

        self.btn_update = tk.Button(
            btn_f,
            text="⚡ Update Now (Auto-Install)",
            font=("Segoe UI", 10, "bold"),
            bg="#00c853",
            fg="#ffffff",
            activebackground="#00e676",
            activeforeground="#000000",
            relief=tk.FLAT,
            padx=16,
            pady=7,
            cursor="hand2",
            command=self._start_download
        )
        self.btn_update.pack(side=tk.LEFT)

        btn_view = tk.Button(
            btn_f,
            text="🌐 Release Page",
            font=("Segoe UI", 9),
            bg="#1e222d",
            fg="#848e9c",
            activebackground="#2a2e39",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self._open_release_url
        )
        btn_view.pack(side=tk.LEFT, padx=8)

        self.btn_cancel = tk.Button(
            btn_f,
            text="Later",
            font=("Segoe UI", 9),
            bg="#1e222d",
            fg="#848e9c",
            activebackground="#2a2e39",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=7,
            cursor="hand2",
            command=self._on_close
        )
        self.btn_cancel.pack(side=tk.RIGHT)

        # 2. Download / Progress container - PACKED TO BOTTOM ABOVE BUTTONS
        self.prog_f = tk.Frame(self, bg=self.THEME_BG)
        self.prog_f.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=(4, 6))

        self.lbl_status = tk.Label(
            self.prog_f,
            text="Click 'Update Now' to automatically download and install.",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.THEME_BG
        )
        self.lbl_status.pack(anchor="w", pady=(0, 4))

        # Progress bar
        style = ttk.Style(self)
        style.configure("Update.Horizontal.TProgressbar", thickness=8, troughcolor="#161a25", background="#00e676")
        self.progress_bar = ttk.Progressbar(
            self.prog_f,
            style="Update.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X)

        # 3. Header banner - PACKED TO TOP
        hdr = tk.Frame(self, bg=self.THEME_BG)
        hdr.pack(side=tk.TOP, fill=tk.X, padx=24, pady=(16, 6))

        badge = tk.Label(
            hdr,
            text="🚀 NEW UPDATE READY",
            font=("Segoe UI", 9, "bold"),
            fg="#00e676",
            bg="#162e21",
            padx=8,
            pady=3
        )
        badge.pack(anchor="w")

        v_curr = self.update_info.get("current_version", __version__)
        v_latest = self.update_info.get("latest_version", "")
        title_lbl = tk.Label(
            hdr,
            text=f"Day Trading Simulator v{v_latest}",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg=self.THEME_BG
        )
        title_lbl.pack(anchor="w", pady=(4, 2))

        sub_lbl = tk.Label(
            hdr,
            text=f"Current installed version: v{v_curr}  ➜  Latest release: v{v_latest}",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.THEME_BG
        )
        sub_lbl.pack(anchor="w")

        # 4. Release Notes Card - FILLS REMAINING EXPANDABLE SPACE IN THE MIDDLE
        card = tk.Frame(self, bg=self.CARD_BG, bd=1, relief=tk.SOLID)
        card.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=24, pady=(4, 8))

        tk.Label(
            card,
            text="WHAT'S NEW IN THIS RELEASE:",
            font=("Segoe UI", 8, "bold"),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        ).pack(anchor="w", padx=12, pady=(8, 4))

        # Text area with scrollbar
        text_f = tk.Frame(card, bg=self.CARD_BG)
        text_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        scrollbar = tk.Scrollbar(text_f)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.txt_notes = tk.Text(
            text_f,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#0e1117",
            fg="#c5c8d1",
            bd=0,
            height=6,
            padx=8,
            pady=8,
            yscrollcommand=scrollbar.set
        )
        self.txt_notes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.txt_notes.yview)

        notes_content = self.update_info.get("release_notes", "").strip() or "General improvements and bug fixes."
        self.txt_notes.insert(tk.END, notes_content)
        self.txt_notes.config(state=tk.DISABLED)

    def _open_release_url(self):
        url = self.update_info.get("release_url", f"https://github.com/{GITHUB_REPO}/releases/latest")
        webbrowser.open(url)

    def _start_download(self):
        if self.is_downloading:
            return

        selected_asset = self.update_info.get("selected_asset")
        if not selected_asset:
            messagebox.showinfo(
                "Manual Download Required",
                "No automatic binary asset found for this release.\nOpening release page in browser..."
            )
            self._open_release_url()
            return

        is_frozen = getattr(sys, "frozen", False)
        # If running from raw python source, notify user
        if not is_frozen:
            answer = messagebox.askyesno(
                "Running in Developer Mode",
                "You are currently running Day Trading Simulator from Python source code.\n\n"
                "Would you like to download and run the updated Windows Installer anyway?"
            )
            if not answer:
                return

        download_url = selected_asset.get("browser_download_url")
        asset_name = selected_asset.get("name", "DayTradeSim-Update.exe")
        is_installer = ("setup" in asset_name.lower())

        temp_dir = tempfile.gettempdir()
        dest_path = os.path.join(temp_dir, asset_name)
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                dest_path = os.path.join(temp_dir, f"update_{int(time.time())}_{asset_name}")

        self.is_downloading = True
        self.btn_update.config(state=tk.DISABLED, bg="#2a2e39", text="⏳ Downloading...")
        self.btn_cancel.config(text="Cancel Download")
        self.lbl_status.config(text="Connecting to GitHub release CDN...", fg="#00e676")

        def worker():
            start_time = time.time()

            def on_progress(downloaded, total):
                if total > 0:
                    pct = int((downloaded / total) * 100)
                    dl_mb = downloaded / (1024 * 1024)
                    tot_mb = total / (1024 * 1024)
                    elapsed = max(0.1, time.time() - start_time)
                    speed_mbps = (downloaded / (1024 * 1024)) / elapsed
                    msg = f"Downloading update: {dl_mb:.1f} MB / {tot_mb:.1f} MB ({pct}%) • {speed_mbps:.1f} MB/s"
                else:
                    dl_mb = downloaded / (1024 * 1024)
                    pct = 0
                    msg = f"Downloading update: {dl_mb:.1f} MB"

                self.after(0, lambda: self._update_progress_ui(pct, msg))

            try:
                success = download_file(
                    download_url,
                    dest_path,
                    progress_callback=on_progress,
                    cancel_event=self.cancel_event
                )
                if not success:
                    self.after(0, lambda: self._on_download_cancelled())
                    return
                self.after(0, lambda: self._on_download_complete(dest_path, is_installer))
            except Exception as e:
                self.after(0, lambda: self._on_download_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _update_progress_ui(self, pct: int, msg: str):
        self.progress_bar["value"] = pct
        self.lbl_status.config(text=msg, fg="#00e676")

    def _on_download_complete(self, file_path: str, is_installer: bool):
        self.progress_bar["value"] = 100
        self.lbl_status.config(text="✅ Download complete! Applying update and restarting...", fg="#00e676")
        self.btn_update.config(text="Restarting...")
        self.btn_cancel.config(state=tk.DISABLED)

        # Brief delay so user sees 100% completion before restart
        self.after(1000, lambda: apply_update_and_restart(file_path, is_installer))

    def _on_download_cancelled(self):
        self.is_downloading = False
        self.progress_bar["value"] = 0
        self.lbl_status.config(text="Download cancelled.", fg=self.TEXT_MUTED)
        self.btn_update.config(state=tk.NORMAL, bg="#00c853", text="⚡ Update Now (Auto-Install)")
        self.btn_cancel.config(text="Later")

    def _on_download_error(self, err_msg: str):
        self.is_downloading = False
        self.progress_bar["value"] = 0
        self.lbl_status.config(text="⚠️ Download failed.", fg="#f23645")
        self.btn_update.config(state=tk.NORMAL, bg="#00c853", text="⚡ Retry Update")
        self.btn_cancel.config(text="Later")
        messagebox.showerror(
            "Download Error",
            f"Failed to download update:\n{err_msg}\n\nYou can update manually from the GitHub release page."
        )

    def _on_close(self):
        if self.is_downloading:
            if messagebox.askyesno("Cancel Download", "An update download is currently in progress. Cancel it?"):
                self.cancel_event.set()
                self.destroy()
        else:
            self.destroy()
