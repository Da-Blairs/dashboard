import os

# Set the display to :0
os.environ["DISPLAY"] = ":0"

import pyautogui
import time
time.sleep(2)
pyautogui.hotkey('ctrl', 'r')
