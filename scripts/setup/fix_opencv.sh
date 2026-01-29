#!/bin/bash
# Direct fix - reinstall opencv as headless version

echo "================================================================"
echo "FIXING OpenCV - Installing headless version (no display needed)"
echo "================================================================"
echo ""

# Uninstall regular opencv and install headless version
pip uninstall -y opencv-python opencv-contrib-python 2>/dev/null
pip install -q opencv-python-headless

echo "✓ OpenCV headless installed"
echo ""

# Verify models are present
echo "Checking models..."
ls -lh data/models/*.pt data/models/*.task

echo ""
echo "================================================================"
echo "Ready to run! Execute:"
echo "  python3 scripts/processing/run_pipeline.py"
echo "================================================================"
