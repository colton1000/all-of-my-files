import random
import time
import threading
import tkinter as tk
from pynput.keyboard import Controller
import keyboard  # for global hotkey

keyboard_controller = Controller()

keys = ['w', 'a', 's', 'd']

# Shared state
running = False  # toggled by hotkey


# --- Overlay Window Setup ---
def create_overlay():
    root = tk.Tk()
    root.title("Key Overlay")

    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.7)
    root.geometry("+10+10")

    key_label = tk.Label(root, text="Stopped", font=("Arial", 20), fg="white", bg="black")
    key_label.pack()

    slider_label = tk.Label(root, text="Speed (seconds):", font=("Arial", 10), fg="white", bg="black")
    slider_label.pack()

    speed_slider = tk.Scale(
        root,
        from_=0.05,
        to=1.0,
        resolution=0.01,
        orient="horizontal",
        length=150,
        bg="black",
        fg="white",
        highlightthickness=0
    )
    speed_slider.set(0.3)
    speed_slider.pack()

    return root, key_label, speed_slider


# --- Key Press Thread ---
def key_press_loop(key_label, speed_slider):
    global running

    while True:
        if running:
            key = random.choice(keys)
            key_label.config(text=f"Pressed: {key.upper()}")

            press_time = speed_slider.get()

            keyboard_controller.press(key)
            time.sleep(press_time)
            keyboard_controller.release(key)

            time.sleep(press_time)
        else:
            key_label.config(text="Stopped")
            time.sleep(0.1)


# --- Hotkey Toggle ---
def toggle_running():
    global running
    running = not running


# --- Main Program ---
def main():
    root, key_label, speed_slider = create_overlay()

    # Start key pressing thread
    t = threading.Thread(target=key_press_loop, args=(key_label, speed_slider), daemon=True)
    t.start()

    # Register global hotkey: 1 + 2 + 3
    keyboard.add_hotkey("1+2+3", toggle_running)

    root.mainloop()


if __name__ == "__main__":
    main()