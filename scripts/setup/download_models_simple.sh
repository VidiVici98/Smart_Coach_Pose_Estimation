#!/bin/bash
# Simple wget-based model download (avoids OpenGL import issues)

set -e

echo "======================================================================"
echo "DOWNLOADING YOLO MODELS (wget method - no OpenGL needed)"
echo "======================================================================"
echo ""

cd /workspaces/Smart_Coach_Pose_Estimation

# Create models directory
mkdir -p data/models
cd data/models

echo "[1/2] Downloading YOLOv8m Pose Model (~52 MB)..."
if [ -f "yolov8m-pose.pt" ]; then
    echo "  ✓ Already exists, skipping"
else
    wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt
    echo "  ✓ Downloaded yolov8m-pose.pt"
fi

echo ""
echo "[2/2] Downloading YOLOv8n Face Model (~6 MB)..."
if [ -f "yolov8n-face.pt" ]; then
    echo "  ✓ Already exists, skipping"
else
    wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
    mv yolov8n.pt yolov8n-face.pt
    echo "  ✓ Downloaded yolov8n-face.pt"
fi

echo ""
echo "======================================================================"
echo "VERIFICATION"
echo "======================================================================"
cd /workspaces/Smart_Coach_Pose_Estimation
ls -lh data/models/

echo ""
echo "✓ Models downloaded successfully!"
echo ""
echo "Next: Run the pipeline with:"
echo "  python3 scripts/processing/run_pipeline.py"
