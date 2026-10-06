import argparse
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a keyboard-controlled mouse auto-clicker.")
    parser.add_argument(
        "--interval",
        type=float,
        default=CLICK_INTERVAL_SECONDS,
        help="seconds between clicks (minimum 0.01; default: %(default)s)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="maximum clicks per start (0 runs until stopped; default: %(default)s)",
    )
    parser.add_argument(
        "--button",
        choices=("left", "right", "middle"),
        default="left",
        help="mouse button to click (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    """Run a configurable auto-clicker controlled by keyboard shortcuts."""
    args = parse_args()
    if args.interval < 0.01:
        raise SystemExit("The click interval must be at least 0.01 seconds.")
    if args.count < 0:
        raise SystemExit("The click count cannot be negative.")

    clicking = False
    click_count = 0

    print(f"Click settings: {args.button} button, every {args.interval:g}s, limit {args.count or 'unlimited'}")
    print("Press 1 to START auto-clicking")
    print("Press 2 to STOP auto-clicking")
    print("Press Ctrl+C to exit the program")

    try:
        while True:
            if keyboard.is_pressed("1"):
                if not clicking:
                    print("Auto-clicking started")
                    clicking = True
                    click_count = 0
                time.sleep(POLL_INTERVAL_SECONDS)

            if keyboard.is_pressed("2"):
                if clicking:
                    print("Auto-clicking stopped")
                    clicking = False
                time.sleep(POLL_INTERVAL_SECONDS)

            if clicking:
                pyautogui.click(button=args.button)
                click_count += 1
                if args.count and click_count >= args.count:
                    print(f"Click limit reached ({click_count}); stopped.")
                    clicking = False
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nAuto-clicker stopped.")


if __name__ == "__main__":
    main()
