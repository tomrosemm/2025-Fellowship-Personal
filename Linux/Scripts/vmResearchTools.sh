#!/bin/bash

SOFTWARE_DIR="/home/$USER/Software"
mkdir -p "$SOFTWARE_DIR"

# Prompt for sudo password once
read -s -p "Enter sudo password: " PASSWORD
echo

# Reminder to run prerequisites script
echo "===================================================================="
echo "Please ensure you have run vmPrerecsInstall.sh before continuing."
echo "===================================================================="
read -p "Press Enter to continue..."

# Keep sudo alive while script runs
( while true; do echo "$PASSWORD" | sudo -S -v; sleep 60; done ) &
SUDO_PID=$!


# Run the main installation commands as root
echo "$PASSWORD" | sudo -S bash -c '
SOFTWARE_DIR=/home/'"$USER"'/Software

# Install latest stable SUMO
echo "Installing latest stable SUMO..."
mkdir -p "$SOFTWARE_DIR/sumo-latest"
add-apt-repository ppa:sumo/stable -y
apt update
apt install -y sumo sumo-tools sumo-doc

# Install SUMO 1.22.0 (from official release)
echo "Installing SUMO 1.22.0..."
mkdir -p "$SOFTWARE_DIR/sumo-1.22.0"
cd "$SOFTWARE_DIR/sumo-1.22.0"
wget https://github.com/eclipse-sumo/sumo/releases/download/v1_22_0/sumo-src-1.22.0.tar.gz
tar xzf sumo-src-1.22.0.tar.gz
cd sumo-1.22.0
mkdir build && cd build
cmake ..
make -j$(nproc)
make install
cd ~

# Install latest stable Mininet
echo "Installing latest stable Mininet..."
mkdir -p "$SOFTWARE_DIR/mininet"
cd "$SOFTWARE_DIR/mininet"
git clone https://github.com/mininet/mininet.git
cd mininet
util/install.sh -a
cd ~

# Install OMNeT++ 6.0
echo "Installing latest stable OMNeT++..."
mkdir -p "$SOFTWARE_DIR/omnetpp"
cd "$SOFTWARE_DIR/omnetpp"
wget https://github.com/omnetpp/omnetpp/releases/download/omnetpp-6.0/omnetpp-6.0-linux-x86_64.tgz
tar xzf omnetpp-6.0-linux-x86_64.tgz
rm omnetpp-6.0-linux-x86_64.tgz
cd omnetpp-6.0
. setenv
./configure
make -j$(nproc)
cd ~

# Ensure Node.js (LTS) is installed before Hardhat, Truffle, Ganache
if ! command -v node >/dev/null 2>&1; then
    echo "Node.js not found. Installing Node.js LTS..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
    apt install -y nodejs
else
    echo "Node.js already installed: $(node --version)"
fi

# Install latest stable Hardhat (Node.js required)
echo "Installing latest stable Hardhat..."
npm install -g hardhat

# Install Truffle and Ganache
echo "Installing latest stable Truffle and Ganache..."
npm install -g truffle ganache

# Install latest stable Veins (requires OMNeT++ and SUMO)
echo "Installing latest stable Veins..."
mkdir -p "$SOFTWARE_DIR/veins"
cd "$SOFTWARE_DIR/veins"
git clone https://github.com/sommer/veins.git
cd veins
cd ~

# Install latest stable ZoKrates
echo "Installing latest stable ZoKrates..."
curl -LSfs get.zokrat.es | sh
cd ~

# If this is your first time installing ZoKrates, add it to PATH
ZOKRATES_BIN="$HOME/zokrates"
if ! grep -q 'export PATH="$HOME/zokrates:$PATH"' ~/.bashrc; then
    echo 'export PATH="$HOME/zokrates:$PATH"' >> ~/.bashrc
    export PATH="$HOME/zokrates:$PATH"
    echo "Added ZoKrates to PATH in ~/.bashrc"
fi

# At the end of the root block, fix ownership:
chown -R '"$USER:$USER"' "$SOFTWARE_DIR"
'

# Kill the background sudo keeper and clear credentials
kill $SUDO_PID
echo "$PASSWORD" | sudo -S -K

echo "Research Tools Installed."