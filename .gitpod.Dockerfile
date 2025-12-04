FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y \
    sudo wget curl python3 python3-pip \
    xfce4 xfce4-goodies \
    novnc websockify x11vnc xvfb \
    chromium-browser git \
    && apt clean

WORKDIR /workspace
COPY . /workspace
RUN pip3 install flask cryptography
