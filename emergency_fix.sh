#!/bin/bash
# Emergency fix script - downloads models and runs pipeline

set -e

echo "========================================"
echo "SMART COACH EMERGENCY FIX"
echo "========================================"
echo ""

# Install packages if needed
echo "[1/3] Ensuring packages installed..."
pip install -q -r requirements.txt
echo "✓ Packages ready"
echo ""

# Download models using Python
echo "[2/3] Downloading YOLO models..."
python3 << 'PYEOF'
from ultralytics import YOLO
import shutil
from pathlib import Path

print("  Downloading yolov8m-pose...")
pose = YOLO('yolov8m-pose.pt')

print("  Downloading yolov8n (for face)...")
face = YOLO('yolov8n.pt')

# Copy to models directory
cache = Path.home() / ".cache" / "ultralytics"
models = Path("data/models")
models.mkdir(parents=True, exist_ok=True)

for f in cache.rglob("yolov8m-pose.pt"):
    dest = models / "yolov8m-pose.pt"
    if not dest.exists():
        shutil.copy(f, dest)
        print(f"  ✓ Copied {dest.name}")
    break

for f in cache.rglob("yolov8n.pt"):
    dest = models / "yolov8n-face.pt"
    if not dest.exists():
        shutil.copy(f, dest)
        print(f"  ✓ Copied {dest.name}")
    break

print("✓ Models ready")
PYEOF

echo ""

# Verify models exist
echo "Verifying models..."
ls -lh data/models/*.pt data/models/*.task
echo ""

# Run pipeline
echo "[3/3] Running pipeline..."
echo "This will take a few minutes..."
echo ""
python3 scripts/processing/run_pipeline.py

echo ""
echo "========================================"
echo "✓ COMPLETE!"
echo "========================================"
echo ""
echo "Output files:"
echo "  - data/output/output_full.mp4"
echo "  - data/output/analytics.csv"
echo ""
