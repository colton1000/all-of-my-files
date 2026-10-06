import sys
import time

try:
    import keyboard
    import pyautogui
except ImportError as exc:
    print(f"Missing required dependency: {exc.name}", file=sys.stderr)
    print("Install it with: python -m pip install keyboard pyautogui", file=sys.stderr)
    raise SystemExit(1) from exc


CLICK_INTERVAL_SECONDS = 0.01
POLL_INTERVAL_SECONDS = 0.2


def main() -> None:
    """Run a simple auto-clicker controlled by keyboard shortcuts."""
    clicking = False

    print("Press 1 to START auto-clicking")
    print("Press 2 to STOP auto-clicking")
    print("Press Ctrl+C to exit the program")

    try:
        while True:
            if keyboard.is_pressed("1"):
                if not clicking:
                    print("Auto-clicking started")
                    clicking = True
                time.sleep(POLL_INTERVAL_SECONDS)

            if keyboard.is_pressed("2"):
                if clicking:
                    print("Auto-clicking stopped")
                    clicking = False
                time.sleep(POLL_INTERVAL_SECONDS)

            if clicking:
                pyautogui.click()
                time.sleep(CLICK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nAuto-clicker stopped.")


if __name__ == "__main__":
    main()
