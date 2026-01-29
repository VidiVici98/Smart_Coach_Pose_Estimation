#!/bin/bash
set -x

echo "=== Attempting to install libGL library ==="

# Try direct package installation without update
sudo apt-get install --no-install-recommends -y libgl1 2>&1 || \
sudo apt install --no-install-recommends -y libgl1 2>&1 || \
sudo apt-get install --no-install-recommends -y libgl1-mesa-glx 2>&1 || \
{
    echo "APT failed, trying manual download..."
    cd /tmp
    wget http://ftp.us.debian.org/debian/pool/main/libg/libglvnd/libgl1_1.3.2-1_amd64.deb
    sudo dpkg -i libgl1_1.3.2-1_amd64.deb || sudo apt --fix-broken install -y
}

echo ""
echo "=== Testing Python import ==="
python3 -c "import cv2; print('✓ cv2 works!')" && \
echo "=== Running pipeline ===" && \
python3 scripts/processing/run_pipeline.py
