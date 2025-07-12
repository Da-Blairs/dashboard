import os
# Set the display to :0
os.environ["DISPLAY"] = ":0"

import pyautogui
import time

pyautogui.FAILSAFE = False
time.sleep(2)
      
# Get screen dimensions
screen_width, screen_height = pyautogui.size()
         
# Press Ctrl+R to refresh
pyautogui.hotkey('ctrl', 'r')
            
# Move mouse to bottom-right corner
pyautogui.moveTo(screen_width - 1, screen_height - 1, duration=0.25)
