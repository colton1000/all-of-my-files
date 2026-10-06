"""Compact desktop overlay for CPU, memory, disk, GPU, and network usage."""

from __future__ import annotations

import sys
import time
import tkinter as tk
from pathlib import Path

import psutil

try:
    import GPUtil
except ImportError:
    GPUtil = None


WIDTH = 286
HEIGHT = 222
REFRESH_MS = 1000


def usage_color(percent: float) -> str:
    if percent < 50:
        return "#5bd69b"
    if percent < 80:
        return "#f4c95d"
    return "#ff737f"


def get_gpu_usage() -> float | None:
    if GPUtil is None:
        return None
    try:
        gpus = GPUtil.getGPUs()
    except (OSError, RuntimeError) as exc:
        print(f"GPU usage is unavailable: {exc}", file=sys.stderr)
        return None
    return gpus[0].load * 100 if gpus else None


def draw_bar(canvas: tk.Canvas, x: int, y: int, width: int, height: int, percent: float) -> None:
    value = max(0, min(100, percent))
    canvas.create_rectangle(x, y, x + width, y + height, fill="#263448", outline="")
    canvas.create_rectangle(
        x,
        y,
        x + int(width * value / 100),
        y + height,
        fill=usage_color(value),
        outline="",
    )


def format_rate(bytes_per_second: float) -> str:
    units = ("B/s", "KB/s", "MB/s", "GB/s")
    rate = max(0, bytes_per_second)
    for unit in units:
        if rate < 1024 or unit == units[-1]:
            return f"{rate:.0f} {unit}" if unit == "B/s" else f"{rate:.1f} {unit}"
        rate /= 1024
    return f"{rate:.1f} GB/s"


def main() -> None:
    root = tk.Tk()
    root.title("System Overlay")
    root.geometry(f"{WIDTH}x{HEIGHT}+14+14")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.overrideredirect(True)

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#0b1220", highlightthickness=0)
    canvas.pack()

    previous_net = psutil.net_io_counters()
    previous_time = time.monotonic()
    drag_origin: tuple[int, int] | None = None

    def close_overlay(_event: tk.Event | None = None) -> None:
        root.destroy()

    def begin_drag(event: tk.Event) -> None:
        nonlocal drag_origin
        if event.y <= 30:
            drag_origin = (event.x_root - root.winfo_x(), event.y_root - root.winfo_y())
        if event.x >= WIDTH - 30 and event.y <= 30:
            close_overlay()

    def drag(event: tk.Event) -> None:
        if drag_origin is not None:
            x = event.x_root - drag_origin[0]
            y = event.y_root - drag_origin[1]
            root.geometry(f"+{x}+{y}")

    def end_drag(_event: tk.Event) -> None:
        nonlocal drag_origin
        drag_origin = None

    canvas.bind("<ButtonPress-1>", begin_drag)
    canvas.bind("<B1-Motion>", drag)
    canvas.bind("<ButtonRelease-1>", end_drag)
    root.bind("<Escape>", close_overlay)

    def update() -> None:
        nonlocal previous_net, previous_time
        now = time.monotonic()
        elapsed = max(now - previous_time, 0.001)
        network = psutil.net_io_counters()
        download_rate = (network.bytes_recv - previous_net.bytes_recv) / elapsed
        upload_rate = (network.bytes_sent - previous_net.bytes_sent) / elapsed
        previous_net, previous_time = network, now

        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(Path.home()))
        gpu = get_gpu_usage()

        canvas.delete("all")
        canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#0b1220", outline="")
        canvas.create_text(14, 16, anchor="w", fill="#e7efff", font=("Segoe UI", 11, "bold"), text="SYSTEM MONITOR")
        canvas.create_text(WIDTH - 14, 16, anchor="e", fill="#8495ae", font=("Segoe UI", 9), text="×  ·  Esc")

        stats = [
            ("CPU", cpu, ""),
            ("RAM", memory.percent, f"{memory.used / (1024**3):.1f}/{memory.total / (1024**3):.1f} GB"),
            ("DISK", disk.percent, f"{disk.used / (1024**3):.0f}/{disk.total / (1024**3):.0f} GB"),
            ("GPU", gpu, ""),
        ]
        y = 42
        for label, percent, detail in stats:
            value = f"{percent:.0f}%" if percent is not None else "N/A"
            canvas.create_text(14, y, anchor="w", fill="#c8d4e8", font=("Segoe UI", 9, "bold"), text=label)
            canvas.create_text(WIDTH - 14, y, anchor="e", fill="#c8d4e8", font=("Segoe UI", 9), text=f"{value}  {detail}".rstrip())
            if percent is not None:
                draw_bar(canvas, 14, y + 8, WIDTH - 28, 6, percent)
            y += 37

        network_text = f"↓ {format_rate(download_rate)}    ↑ {format_rate(upload_rate)}"
        canvas.create_text(14, HEIGHT - 13, anchor="w", fill="#94a7c1", font=("Segoe UI", 9), text=f"NETWORK   {network_text}")
        root.after(REFRESH_MS, update)

    psutil.cpu_percent(interval=None)
    update()
    root.mainloop()


if __name__ == "__main__":
    main()
