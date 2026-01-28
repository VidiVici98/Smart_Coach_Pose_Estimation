#!/bin/bash
# Quick diagnostic script for Smart Coach

echo "=================================="
echo "Smart Coach Quick Diagnostics"
echo "=================================="
echo ""

# Check Python
echo "[1] Python version:"
python3 --version
echo ""

# Check packages
echo "[2] Checking packages..."
python3 -c "
import sys
packages = ['torch', 'cv2', 'numpy', 'mediapipe', 'ultralytics']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✓ {pkg}')
    except ImportError:
        print(f'  ✗ {pkg} - MISSING')
"
echo ""

# Check models
echo "[3] Model files:"
ls -lh data/models/*.pt data/models/*.task 2>/dev/null || echo "  ✗ No model files found"
echo ""

# Check test video
echo "[4] Test video:"
if [ -f "data/input/test_video.mp4" ]; then
    ls -lh data/input/test_video.mp4
else
    echo "  ✗ Test video not found"
fi
echo ""

echo "=================================="
echo "To fix issues:"
echo "  1. Install packages: pip install -r requirements.txt"
echo "  2. Download models: python3 scripts/tools/download_models.py"
echo "=================================="
