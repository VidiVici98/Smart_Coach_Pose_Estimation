#!/bin/bash
#
# Smart Coach - One-Click Android/Mobile Runner
# 
# This script provides a simplified way to run the pipeline on Android devices
# using Termux or similar terminal apps.
#
# Usage on Android (Termux):
#   1. Install Termux from F-Droid
#   2. Run: pkg install git python
#   3. Clone repo: git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
#   4. Run this script: bash mobile_runner.sh
#

set -e  # Exit on error

echo "=================================================="
echo "  Smart Coach Pose Estimation - Mobile Runner"
echo "=================================================="
echo ""

# Detect platform
if [[ "$OSTYPE" == "linux-android"* ]]; then
    PLATFORM="termux"
    echo "✓ Platform: Termux (Android)"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
    echo "✓ Platform: Linux"
else
    PLATFORM="unknown"
    echo "⚠ Platform: $OSTYPE (may not be fully supported)"
fi

echo ""
echo "This script will:"
echo "  1. Check Python installation"
echo "  2. Install lightweight dependencies"
echo "  3. Process FIRST 10 FRAMES of test video"
echo "  4. Extract sample frames for validation"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Step 1: Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 not found!"
    if [ "$PLATFORM" == "termux" ]; then
        echo "  Install with: pkg install python"
    fi
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ $PYTHON_VERSION"

echo ""
echo "Step 2: Installing lightweight dependencies..."
echo "  (This may take 5-10 minutes on mobile)"

# Install only essential packages for mobile
pip3 install --quiet --user numpy opencv-python-headless Pillow || {
    echo "✗ Installation failed. Check internet connection."
    exit 1
}
echo "✓ Core packages installed"

echo ""
echo "Step 3: Extracting sample frames..."

# Create a simple Python script to extract frames
python3 << 'PYTHON_SCRIPT'
import cv2
import os
import sys

# Configuration
VIDEO_PATH = "data/input/test_video.mp4"
OUTPUT_DIR = "data/output/mobile_frames"
MAX_FRAMES = 10

# Check if video exists
if not os.path.exists(VIDEO_PATH):
    print(f"✗ Video not found: {VIDEO_PATH}")
    print("  Please place a video at data/input/test_video.mp4")
    sys.exit(1)

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Open video
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"✗ Could not open video: {VIDEO_PATH}")
    sys.exit(1)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"✓ Video opened: {total_frames} frames @ {fps:.1f} FPS")

# Extract frames
print(f"\nExtracting first {MAX_FRAMES} frames...")
for i in range(min(MAX_FRAMES, total_frames)):
    ret, frame = cap.read()
    if not ret:
        break
    
    # Save frame as JPEG (smaller than PNG)
    output_path = os.path.join(OUTPUT_DIR, f"frame_{i:03d}.jpg")
    cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"  Saved frame {i+1}/{MAX_FRAMES}")

cap.release()

print(f"\n✓ Frames saved to: {OUTPUT_DIR}")
print(f"  View with: ls -lh {OUTPUT_DIR}")
print(f"\nNote: Full pose estimation requires heavy ML models (PyTorch, YOLO)")
print(f"      not supported on Android. Use GitHub Codespaces for full pipeline.")
PYTHON_SCRIPT

echo ""
echo "=================================================="
echo "  Mobile Processing Complete!"
echo "=================================================="
echo ""
echo "What was done:"
echo "  ✓ Extracted first 10 frames from test video"
echo "  ✓ Saved as JPEGs in data/output/mobile_frames/"
echo ""
echo "Next steps:"
echo "  • View extracted frames"
echo "  • For FULL pipeline with pose estimation:"
echo "    → Use GitHub Codespaces (free, browser-based)"
echo "    → See docs/SETUP_AND_TROUBLESHOOTING.md"
echo ""
echo "GitHub Codespaces Quick Start:"
echo "  1. Go to repo on GitHub (on your phone browser)"
echo "  2. Tap Code → Codespaces → Create codespace"
echo "  3. Wait for environment to load (1-2 minutes)"
echo "  4. Run: python scripts/processing/run_pipeline.py"
echo "  5. Download results from data/output/"
echo ""
echo "Happy coaching! 🎯"
