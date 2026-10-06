"""Randomly press WASD keys with a small always-on-top control panel."""

import random
import time
import tkinter as tk
from threading import Event

import keyboard
from pynput.keyboard import Controller


KEYS = ("w", "a", "s", "d")
HOTKEY = "1+2+3"


def main() -> None:
    root = tk.Tk()
    root.title("WASD Key Helper")
    root.configure(bg="#111827")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.geometry("260x210+14+14")

    running = Event()
    controller = Controller()
    current_key: str | None = None
    release_at = 0.0
    next_press_at = 0.0

    title = tk.Label(
        root,
        text="WASD Key Helper",
        font=("Segoe UI", 13, "bold"),
        fg="#eef4ff",
        bg="#111827",
    )
    title.pack(anchor="w", padx=14, pady=(13, 2))
    status = tk.Label(root, text="Stopped", font=("Segoe UI", 18, "bold"), fg="#91a0b8", bg="#111827")
    status.pack(pady=(7, 1))
    help_text = tk.Label(root, text=f"Global hotkey: {HOTKEY}", font=("Segoe UI", 9), fg="#9fb0c7", bg="#111827")
    help_text.pack()

    speed_label = tk.Label(root, text="Delay between keys: 0.30 s", font=("Segoe UI", 9), fg="#c8d5e8", bg="#111827")
    speed_label.pack(pady=(9, 0))
    speed_slider = tk.Scale(
        root,
        from_=0.05,
        to=1.0,
        resolution=0.01,
        orient="horizontal",
        length=220,
        bg="#111827",
        fg="#eef4ff",
        troughcolor="#28364b",
        highlightthickness=0,
        command=lambda value: speed_label.config(text=f"Delay between keys: {float(value):.2f} s"),
    )
    speed_slider.set(0.3)
    speed_slider.pack()

    controls = tk.Frame(root, bg="#111827")
    controls.pack(fill="x", padx=14, pady=(8, 12))
    toggle_button = tk.Button(controls, text="Start", command=lambda: toggle_running(), width=10)
    toggle_button.pack(side="left")
    tk.Button(controls, text="Close", command=lambda: close(), width=10).pack(side="right")

    def toggle_running() -> None:
        if running.is_set():
            running.clear()
        else:
            running.set()

    hotkey_handle = keyboard.add_hotkey(HOTKEY, toggle_running)

    def tick() -> None:
        nonlocal current_key, release_at, next_press_at
        now = time.monotonic()
        if not running.is_set():
            if current_key is not None:
                controller.release(current_key)
                current_key = None
            status.config(text="Stopped", fg="#91a0b8")
            toggle_button.config(text="Start")
            root.after(20, tick)
            return

        if current_key is not None and now >= release_at:
            controller.release(current_key)
            current_key = None
            next_press_at = now + float(speed_slider.get())
        if current_key is None and now >= next_press_at:
            current_key = random.choice(KEYS)
            controller.press(current_key)
            release_at = now + float(speed_slider.get())
            status.config(text=f"Pressing {current_key.upper()}", fg="#74e0b0")
        toggle_button.config(text="Stop")
        root.after(20, tick)

    def close() -> None:
        running.clear()
        if current_key is not None:
            controller.release(current_key)
        keyboard.remove_hotkey(hotkey_handle)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    root.after(0, tick)
    root.mainloop()


if __name__ == "__main__":
    main()
