import pyautogui
import time

print("Move your mouse to the desired position. Press Ctrl+C to exit.")
try:
    while True:
        # Get the current mouse position.
        x, y = pyautogui.position()
        print(f"X: {x}   Y: {y}", end="\r")  # The '\r' overwrites the same line.
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nDone.")