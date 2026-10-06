import pyautogui
import keyboard
import time

clicking = False

print("Press 1 to START auto-clicking")
print("Press 2 to STOP auto-clicking")
print("Press Ctrl+C to exit the program")

while True:
    if keyboard.is_pressed("1"):
        if not clicking:
            print("Auto-clicking started")
            clicking = True
        time.sleep(0.2)  # prevents double-trigger

    if keyboard.is_pressed("2"):
        if clicking:
            print("Auto-clicking stopped")
            clicking = False
        time.sleep(0.2)

    if clicking:
        pyautogui.click()
        time.sleep(0.01)  # speed of clicking