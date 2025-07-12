import os

# Set the display to :0
os.environ["DISPLAY"] = ":0"

import pyautogui
import time

while True:
    pyautogui.press('shift')
    time.sleep(60)  # Wait for 60 seconds (1 minute)
