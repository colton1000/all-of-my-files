#!/usr/bin/env python3
"""Desktop Utility Hub: file organizer, local HTML server, auto clicker, and tools.

Designed for Windows, but most features also work on Linux/macOS.
No third-party packages are required.
"""
from __future__ import annotations

import http.server
import json
import os
import queue
import shutil
import socket
import socketserver
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser

if sys.platform.startswith("win"):
    import ctypes
    import ctypes.wintypes
else:
    ctypes = None
    ctypes_wintypes = None
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "Utility Hub"
OUTPUT_FOLDER = "Organized Files"
LOG_FOLDER = ".utility_hub_logs"

TYPE_GROUPS = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".heic", ".tif", ".tiff"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".webm", ".wmv", ".m4v"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".opus", ".wma"},
    "Documents": {".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md", ".epub"},
    "Spreadsheets": {".xls", ".xlsx", ".ods", ".csv", ".tsv"},
    "Presentations": {".ppt", ".pptx", ".odp"},
    "Archives": {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz"},
    "Programs": {".exe", ".msi", ".msix", ".appx", ".apk"},
    "Code and Web": {".py", ".js", ".ts", ".html", ".htm", ".css", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".sql"},
    "Fonts": {".ttf", ".otf", ".woff", ".woff2"},
    "3D Models": {".obj", ".fbx", ".stl", ".gltf", ".glb", ".blend"},
}


def type_group(extension: str) -> str:
    extension = extension.lower()
    for group, extensions in TYPE_GROUPS.items():
        if extension in extensions:
            return group
    return f"{extension[1:].upper()} Files" if extension else "Files Without Extension"


def unique_path(path: Path) -> Path:
    candidate = path
    number = 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem} ({number}){path.suffix}")
        number += 1
    return candidate


def standard_folders() -> list[Path]:
    home = Path.home()
    found: list[Path] = []
    for name in ("Documents", "Downloads", "Pictures"):
        for candidate in (home / name, home / "OneDrive" / name, home / "OneDrive - Personal" / name):
            if candidate.is_dir():
                resolved = candidate.resolve()
                if resolved not in found:
                    found.append(resolved)
                break
    return found


def open_in_file_manager(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return


class UtilityHub(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("820x620")
        self.minsize(700, 520)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.organizing = False
        self.server: ReusableTCPServer | None = None
        self.server_thread: threading.Thread | None = None
        self.server_url = ""
        self.auto_clicking = False
        self.click_stop = threading.Event()

        self._build_ui()
        self.after(75, self.process_events)

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("vista" if sys.platform.startswith("win") else "clam")
        except tk.TclError:
            pass
        style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 9, "bold"))
        style.configure("TButton", padding=(9, 6))

        header = ttk.Frame(self, padding=(18, 16, 18, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Utility Hub", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(header, text="Organize files, host an HTML project, auto-click, and open helpful folders.").pack(anchor="w", pady=(3, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=16, pady=10)
        self.organizer_tab = ttk.Frame(notebook, padding=16)
        self.server_tab = ttk.Frame(notebook, padding=16)
        self.clicker_tab = ttk.Frame(notebook, padding=16)
        self.tools_tab = ttk.Frame(notebook, padding=16)
        notebook.add(self.organizer_tab, text="File Organizer")
        notebook.add(self.server_tab, text="HTML Server")
        notebook.add(self.clicker_tab, text="Auto Clicker")
        notebook.add(self.tools_tab, text="More Tools")

        self._build_organizer()
        self._build_server()
        self._build_clicker()
        self._build_tools()

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w", padding=(8, 4)).pack(fill="x", side="bottom")

    def _build_organizer(self) -> None:
        ttk.Label(self.organizer_tab, text="Simple File Organizer", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(
            self.organizer_tab,
            text="Moves files into Organized Files folders based on file type. Existing files are never overwritten.",
            wraplength=650,
        ).pack(anchor="w", pady=(4, 12))

        row = ttk.Frame(self.organizer_tab)
        row.pack(fill="x")
        self.org_path_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        ttk.Entry(row, textvariable=self.org_path_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse...", command=self.choose_organizer_folder).pack(side="left", padx=(8, 0))

        options = ttk.Frame(self.organizer_tab)
        options.pack(fill="x", pady=10)
        self.include_subfolders_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text="Include subfolders", variable=self.include_subfolders_var).pack(side="left")

        buttons = ttk.Frame(self.organizer_tab)
        buttons.pack(fill="x", pady=(2, 14))
        self.organize_button = ttk.Button(buttons, text="Organize Selected Folder", command=self.start_selected_organize)
        self.organize_button.pack(side="left")
        ttk.Button(buttons, text="Organize Documents + Downloads + Pictures", command=self.start_standard_organize).pack(side="left", padx=8)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(self.organizer_tab, variable=self.progress_var, maximum=100)
        self.progress.pack(fill="x")
        self.percent_var = tk.StringVar(value="0% done")
        ttk.Label(self.organizer_tab, textvariable=self.percent_var, font=("Segoe UI", 11, "bold")).pack(anchor="center", pady=(5, 8))

        self.org_log = tk.Text(self.organizer_tab, height=10, state="disabled", wrap="word")
        self.org_log.pack(fill="both", expand=True)

    def _build_server(self) -> None:
        ttk.Label(self.server_tab, text="Open an HTML Project with HTTP", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(
            self.server_tab,
            text="Choose an HTML file. This starts a local server and opens it in your browser. Stop the server when finished.",
            wraplength=650,
        ).pack(anchor="w", pady=(4, 12))

        row = ttk.Frame(self.server_tab)
        row.pack(fill="x")
        self.html_path_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.html_path_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Choose HTML...", command=self.choose_html).pack(side="left", padx=(8, 0))

        port_row = ttk.Frame(self.server_tab)
        port_row.pack(fill="x", pady=12)
        ttk.Label(port_row, text="Port (0 = automatic):").pack(side="left")
        self.port_var = tk.StringVar(value="8000")
        ttk.Entry(port_row, textvariable=self.port_var, width=10).pack(side="left", padx=8)

        controls = ttk.Frame(self.server_tab)
        controls.pack(fill="x")
        self.server_start_button = ttk.Button(controls, text="Start and Open", command=self.start_server)
        self.server_start_button.pack(side="left")
        self.server_stop_button = ttk.Button(controls, text="Stop Server", command=self.stop_server, state="disabled")
        self.server_stop_button.pack(side="left", padx=8)
        ttk.Button(controls, text="Open Again", command=self.open_server_again).pack(side="left")
        ttk.Button(controls, text="Copy URL", command=self.copy_server_url).pack(side="left", padx=(8, 0))

        self.server_status_var = tk.StringVar(value="Server is stopped.")
        ttk.Label(self.server_tab, textvariable=self.server_status_var, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=18)
        ttk.Label(self.server_tab, text="Security note: this binds only to 127.0.0.1, so it is available on this computer only.", wraplength=650).pack(anchor="w")

    def _build_clicker(self) -> None:
        ttk.Label(self.clicker_tab, text="Auto Clicker", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(
            self.clicker_tab,
            text="After the countdown, clicks occur at the current mouse position. Move the pointer where you want it first.",
            wraplength=650,
        ).pack(anchor="w", pady=(4, 12))

        grid = ttk.Frame(self.clicker_tab)
        grid.pack(anchor="w")
        ttk.Label(grid, text="Click interval (seconds):").grid(row=0, column=0, sticky="w", pady=6)
        self.interval_var = tk.StringVar(value="0.10")
        ttk.Entry(grid, textvariable=self.interval_var, width=12).grid(row=0, column=1, padx=10)
        ttk.Label(grid, text="Number of clicks (0 = until stopped):").grid(row=1, column=0, sticky="w", pady=6)
        self.click_count_var = tk.StringVar(value="100")
        ttk.Entry(grid, textvariable=self.click_count_var, width=12).grid(row=1, column=1, padx=10)
        ttk.Label(grid, text="Start delay (seconds):").grid(row=2, column=0, sticky="w", pady=6)
        self.delay_var = tk.StringVar(value="3")
        ttk.Entry(grid, textvariable=self.delay_var, width=12).grid(row=2, column=1, padx=10)

        controls = ttk.Frame(self.clicker_tab)
        controls.pack(fill="x", pady=16)
        self.click_start_button = ttk.Button(controls, text="Start Auto Clicker", command=self.start_clicker)
        self.click_start_button.pack(side="left")
        self.click_stop_button = ttk.Button(controls, text="STOP", command=self.stop_clicker, state="disabled")
        self.click_stop_button.pack(side="left", padx=8)

        self.click_status_var = tk.StringVar(value="Stopped")
        ttk.Label(self.clicker_tab, textvariable=self.click_status_var, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(self.clicker_tab, text="Tip: keep this window visible so you can press STOP. Auto-clicking pauses when the mouse is moved to the top-left corner on Windows.", wraplength=650).pack(anchor="w", pady=12)

    def _build_tools(self) -> None:
        ttk.Label(self.tools_tab, text="More Tools", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 12))
        for text, command in (
            ("Open Downloads", lambda: self.open_known_folder("Downloads")),
            ("Open Documents", lambda: self.open_known_folder("Documents")),
            ("Open Pictures", lambda: self.open_known_folder("Pictures")),
            ("Open Current Script Folder", lambda: open_in_file_manager(Path(__file__).resolve().parent)),
            ("Create a New Project Folder", self.create_project_folder),
            ("Show Computer Information", self.show_computer_info),
        ):
            ttk.Button(self.tools_tab, text=text, command=command, width=34).pack(anchor="w", pady=5)

    def choose_organizer_folder(self) -> None:
        chosen = filedialog.askdirectory(title="Choose a folder to organize")
        if chosen:
            self.org_path_var.set(chosen)

    def set_progress(self, done: int, total: int, message: str = "") -> None:
        percent = 100 if total == 0 else round(done * 100 / total, 1)
        self.events.put(("progress", (percent, message)))

    def gather_files(self, root: Path, recursive: bool) -> list[Path]:
        output = root / OUTPUT_FOLDER
        logs = root / LOG_FOLDER
        iterator = root.rglob("*") if recursive else root.iterdir()
        result = []
        for path in iterator:
            try:
                resolved = path.resolve()
                if not path.is_file() or path.is_symlink() or resolved == Path(__file__).resolve():
                    continue
                if output == resolved or output in resolved.parents or logs in resolved.parents:
                    continue
                result.append(resolved)
            except (OSError, PermissionError):
                continue
        return result

    def organize_worker(self, roots: list[Path], recursive: bool) -> None:
        try:
            all_jobs: list[tuple[Path, Path]] = []
            for root in roots:
                for source in self.gather_files(root, recursive):
                    destination_dir = root / OUTPUT_FOLDER / type_group(source.suffix)
                    all_jobs.append((source, destination_dir))

            total = len(all_jobs)
            moved: list[dict[str, str]] = []
            errors: list[str] = []
            self.set_progress(0, total, f"Found {total} file(s).")

            for index, (source, destination_dir) in enumerate(all_jobs, 1):
                try:
                    destination_dir.mkdir(parents=True, exist_ok=True)
                    destination = unique_path(destination_dir / source.name)
                    shutil.move(str(source), str(destination))
                    moved.append({"source": str(source), "destination": str(destination)})
                    message = f"Moved: {source.name} -> {destination_dir.name}"
                except Exception as exc:
                    errors.append(f"{source}: {exc}")
                    message = f"Could not move: {source.name}"
                self.set_progress(index, total, message)

            if moved:
                log_root = roots[0] / LOG_FOLDER
                log_root.mkdir(parents=True, exist_ok=True)
                log_path = log_root / f"organize_{datetime.now():%Y%m%d_%H%M%S}.json"
                log_path.write_text(json.dumps({"moves": moved}, indent=2), encoding="utf-8")
            self.events.put(("organization_done", (len(moved), errors, total)))
        except Exception as exc:
            self.events.put(("error", f"Organizer error: {exc}"))
            self.events.put(("organization_done", (0, [str(exc)], 0)))

    def begin_organize(self, roots: list[Path], recursive: bool) -> None:
        if self.organizing:
            return
        if not roots:
            messagebox.showerror(APP_TITLE, "No usable folders were found.")
            return
        if not messagebox.askyesno(APP_TITLE, "Move files into Organized Files folders?\n\nExisting files will not be overwritten."):
            return
        self.organizing = True
        self.organize_button.configure(state="disabled")
        self.progress_var.set(0)
        self.percent_var.set("0% done")
        self.write_log("Starting organizer...\n", clear=True)
        threading.Thread(target=self.organize_worker, args=(roots, recursive), daemon=True).start()

    def start_selected_organize(self) -> None:
        path = Path(self.org_path_var.get()).expanduser()
        if not path.is_dir():
            messagebox.showerror(APP_TITLE, "Please choose a valid folder.")
            return
        self.begin_organize([path.resolve()], self.include_subfolders_var.get())

    def start_standard_organize(self) -> None:
        self.begin_organize(standard_folders(), False)

    def write_log(self, text: str, clear: bool = False) -> None:
        self.org_log.configure(state="normal")
        if clear:
            self.org_log.delete("1.0", "end")
        self.org_log.insert("end", text + ("\n" if not text.endswith("\n") else ""))
        self.org_log.see("end")
        self.org_log.configure(state="disabled")

    def choose_html(self) -> None:
        chosen = filedialog.askopenfilename(title="Choose an HTML file", filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")])
        if chosen:
            self.html_path_var.set(chosen)

    def start_server(self) -> None:
        if self.server:
            messagebox.showinfo(APP_TITLE, "The local server is already running.")
            return
        html_file = Path(self.html_path_var.get()).expanduser()
        if not html_file.is_file() or html_file.suffix.lower() not in {".html", ".htm"}:
            messagebox.showerror(APP_TITLE, "Choose a valid .html or .htm file.")
            return
        try:
            port = int(self.port_var.get().strip())
            if not 0 <= port <= 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror(APP_TITLE, "Port must be a number from 0 through 65535.")
            return

        directory = html_file.parent.resolve()
        handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(directory), **kwargs)
        try:
            self.server = ReusableTCPServer(("127.0.0.1", port), handler)
        except OSError as exc:
            self.server = None
            messagebox.showerror(APP_TITLE, f"Could not start the server. Try port 0.\n\n{exc}")
            return

        actual_port = self.server.server_address[1]
        filename = html_file.name.replace(" ", "%20")
        self.server_url = f"http://127.0.0.1:{actual_port}/{filename}"
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        self.server_status_var.set(f"Running: {self.server_url}")
        self.server_start_button.configure(state="disabled")
        self.server_stop_button.configure(state="normal")
        self.status_var.set("Local HTML server running")
        webbrowser.open(self.server_url)

    def stop_server(self) -> None:
        server = self.server
        if not server:
            return
        self.server = None
        threading.Thread(target=self._shutdown_server, args=(server,), daemon=True).start()
        self.server_status_var.set("Server is stopped.")
        self.server_start_button.configure(state="normal")
        self.server_stop_button.configure(state="disabled")
        self.status_var.set("Ready")

    @staticmethod
    def _shutdown_server(server: ReusableTCPServer) -> None:
        server.shutdown()
        server.server_close()

    def open_server_again(self) -> None:
        if self.server and self.server_url:
            webbrowser.open(self.server_url)
        else:
            messagebox.showinfo(APP_TITLE, "Start the server first.")

    def copy_server_url(self) -> None:
        if not self.server or not self.server_url:
            messagebox.showinfo(APP_TITLE, "Start the server before copying its URL.")
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(self.server_url)
            self.update_idletasks()
        except tk.TclError as exc:
            messagebox.showerror(APP_TITLE, f"Could not copy the server URL.\n\n{exc}")
            return
        self.status_var.set("Server URL copied to clipboard")

    def start_clicker(self) -> None:
        if self.auto_clicking:
            return
        try:
            interval = float(self.interval_var.get())
            count = int(self.click_count_var.get())
            delay = float(self.delay_var.get())
            if interval < 0.01 or count < 0 or delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(APP_TITLE, "Use an interval of at least 0.01, a nonnegative click count, and a nonnegative delay.")
            return
        if not sys.platform.startswith("win") or ctypes is None:
            messagebox.showerror(APP_TITLE, "The built-in no-install auto clicker currently supports Windows only.")
            return

        self.auto_clicking = True
        self.click_stop.clear()
        self.click_start_button.configure(state="disabled")
        self.click_stop_button.configure(state="normal")
        threading.Thread(target=self.click_worker, args=(interval, count, delay), daemon=True).start()

    def click_worker(self, interval: float, count: int, delay: float) -> None:
        end = time.monotonic() + delay
        while time.monotonic() < end and not self.click_stop.is_set():
            remaining = max(0, end - time.monotonic())
            self.events.put(("click_status", f"Starting in {remaining:.1f} seconds..."))
            time.sleep(0.05)

        clicked = 0
        assert ctypes is not None
        while not self.click_stop.is_set() and (count == 0 or clicked < count):
            point = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
            if point.x <= 1 and point.y <= 1:
                break
            ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
            clicked += 1
            self.events.put(("click_status", f"Running: {clicked} click(s). Press STOP to end."))
            self.click_stop.wait(interval)
        self.events.put(("click_done", clicked))

    def stop_clicker(self) -> None:
        self.click_stop.set()
        self.click_status_var.set("Stopping...")

    def open_known_folder(self, name: str) -> None:
        home = Path.home()
        for candidate in (home / name, home / "OneDrive" / name, home / "OneDrive - Personal" / name):
            if candidate.is_dir():
                open_in_file_manager(candidate)
                return
        messagebox.showerror(APP_TITLE, f"Could not find the {name} folder.")

    def create_project_folder(self) -> None:
        parent = filedialog.askdirectory(title="Choose where to create the project folder")
        if not parent:
            return
        name = "New Project"
        target = unique_path(Path(parent) / name)
        target.mkdir()
        for child in ("assets", "images", "scripts", "styles"):
            (target / child).mkdir()
        (target / "index.html").write_text("<!doctype html>\n<html><head><meta charset='utf-8'><title>New Project</title></head><body><h1>New Project</h1></body></html>\n", encoding="utf-8")
        open_in_file_manager(target)

    def show_computer_info(self) -> None:
        drive = Path.home().anchor or "/"
        total, used, free = shutil.disk_usage(drive)
        info = (
            f"Python: {sys.version.split()[0]}\n"
            f"Platform: {sys.platform}\n"
            f"Computer name: {socket.gethostname()}\n"
            f"Home folder: {Path.home()}\n"
            f"Free space: {free / (1024 ** 3):.1f} GB of {total / (1024 ** 3):.1f} GB"
        )
        messagebox.showinfo("Computer Information", info)

    def process_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "progress":
                    percent, message = payload  # type: ignore[misc]
                    self.progress_var.set(percent)
                    self.percent_var.set(f"{percent:g}% done")
                    self.status_var.set(str(message))
                    if message:
                        self.write_log(str(message))
                elif event == "organization_done":
                    moved, errors, total = payload  # type: ignore[misc]
                    self.organizing = False
                    self.organize_button.configure(state="normal")
                    if total == 0:
                        self.progress_var.set(100)
                        self.percent_var.set("100% done")
                    summary = f"Finished. Organized {moved} of {total} file(s)."
                    if errors:
                        summary += f" {len(errors)} error(s) occurred."
                    self.write_log(summary)
                    self.status_var.set(summary)
                    messagebox.showinfo(APP_TITLE, summary)
                elif event == "error":
                    messagebox.showerror(APP_TITLE, str(payload))
                elif event == "click_status":
                    self.click_status_var.set(str(payload))
                elif event == "click_done":
                    self.auto_clicking = False
                    self.click_start_button.configure(state="normal")
                    self.click_stop_button.configure(state="disabled")
                    self.click_status_var.set(f"Stopped after {payload} click(s).")
        except queue.Empty:
            pass
        self.after(75, self.process_events)

    def on_close(self) -> None:
        self.click_stop.set()
        if self.server:
            server = self.server
            self.server = None
            server.shutdown()
            server.server_close()
        self.destroy()


if __name__ == "__main__":
    UtilityHub().mainloop()
