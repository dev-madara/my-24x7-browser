FROM ubuntu:22.04

# Basics
RUN apt update && apt install -y \
    sudo wget curl xfce4 xfce4-goodies \
    novnc websockify x11vnc xvfb \
    chromium-browser nodejs npm git \
    && apt clean
    
# Set password for VNC
RUN mkdir ~/.vnc && \
    x11vnc -storepasswd "csvp@2025" ~/.vnc/passwd

# Workspace directory
WORKDIR /workspace

COPY . /workspace
