#!/bin/bash

# Prompt for sudo password once
read -s -p "Enter sudo password: " PASSWORD
echo

# Keep sudo alive while script runs
( while true; do echo "$PASSWORD" | sudo -S -v; sleep 60; done ) &
SUDO_PID=$!

echo "$PASSWORD" | sudo -S apt update -y
echo "$PASSWORD" | sudo -S apt upgrade -y

# Install prerequisites for research tools
echo "$PASSWORD" | sudo -S apt install -y \
    build-essential cmake python3 python3-pip python3-venv \
    libxerces-c-dev libfox-1.6-dev libgdal-dev libproj-dev \
    libgl2ps-dev libopenscenegraph-dev libeigen3-dev \
    qtbase5-dev qttools5-dev qttools5-dev-tools \
    libboost-all-dev libsqlite3-dev libpng-dev \
    libxml2-dev default-jre default-jdk openjdk-11-jdk \
    libssl-dev pkg-config software-properties-common

echo "$PASSWORD" | sudo -S apt autoremove -y
echo "$PASSWORD" | sudo -S apt clean

# Kill the background sudo keeper and clear credentials
kill $SUDO_PID
echo "$PASSWORD" | sudo -S -K

echo "Prerequisite installation complete."
