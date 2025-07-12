#!/bin/bash
export DISPLAY=:0

# Start the X server and openbox session in the background
xinit /usr/bin/openbox-session -- :0 &

# Wait for X server to start
sleep 5

export DISPLAY=:0
xrandr --output HDMI-2 --mode 1920x1080
xrandr --output HDMI-2 --dpms off

# Start Chromium in kiosk mode
chromium-browser --kiosk --start-fullscreen --no-first-run --disable --disable-infobars http://localhost:8501 &

cd /home/gavinblair/apps/family-dashboard
source env/bin/activate
python press_shift_every_minute.py &

