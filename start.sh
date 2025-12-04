#!/bin/bash
export DISPLAY=:1
Xvfb :1 -screen 0 1920x1080x16 &
mkdir -p ~/.vnc
x11vnc -storepasswd "csvp@2025" ~/.vnc/passwd
x11vnc -display :1 -usepw -forever -shared &
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &
xfce4-session &
chromium-browser --no-sandbox --disable-gpu &
python3 videodata.py &
tail -f /dev/null
