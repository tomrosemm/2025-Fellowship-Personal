#!/bin/bash

# Prompt for sudo password once
read -s -p "Enter sudo password: " PASSWORD

echo

# Keep sudo alive while script runs
( while true; do echo "$PASSWORD" | sudo -S -v; sleep 60; done ) &
SUDO_PID=$!

# Your setup commands
echo "$PASSWORD" | sudo -S apt update -y
echo "$PASSWORD" | sudo -S apt upgrade -y
echo "$PASSWORD" | sudo -S apt install -y git htop curl unzip wget dos2unix

# Only install virtualbox-guest-utils if running inside VirtualBox
if grep -q "VirtualBox" /sys/class/dmi/id/product_name 2>/dev/null; then
    echo "$PASSWORD" | sudo -S apt install -y virtualbox-guest-utils
fi

echo "$PASSWORD" | sudo -S apt autoremove -y
echo "$PASSWORD" | sudo -S apt clean

# Kill the background sudo keeper and clear credentials
kill $SUDO_PID
echo "$PASSWORD" | sudo -S -K

echo "Setup complete."
