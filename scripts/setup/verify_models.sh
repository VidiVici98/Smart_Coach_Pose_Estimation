#!/bin/bash
# Script to download and verify all required model files for Smart Coach pipeline
# This ensures models persist in codespace and aren't deleted between sessions

set -e  # Exit on error

MODELS_DIR="data/models"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$REPO_ROOT"

echo "=================================================="
echo "Smart Coach Model Setup & Verification"
echo "=================================================="
echo ""

# Create models directory if it doesn't exist
mkdir -p "$MODELS_DIR"

# Function to check file size and existence
check_model() {
    local model_name="$1"
    local model_path="$2"
    local min_size_mb="$3"
    local max_size_mb="$4"
    
    if [ -f "$model_path" ]; then
        local size_mb=$(du -m "$model_path" | cut -f1)
        if [ "$size_mb" -ge "$min_size_mb" ] && [ "$size_mb" -le "$max_size_mb" ]; then
            echo "✓ $model_name: ${size_mb}MB (valid)"
            return 0
        else
            echo "✗ $model_name: ${size_mb}MB (expected ${min_size_mb}-${max_size_mb}MB)"
            return 1
        fi
    else
        echo "✗ $model_name: NOT FOUND"
        return 1
    fi
}

echo "Checking existing models..."
echo ""

# Check each model
models_ok=true

check_model "YOLOv8 Pose" "$MODELS_DIR/yolov8m-pose.pt" 40 60 || models_ok=false
check_model "YOLOv8 Face" "$MODELS_DIR/yolov8n-face.pt" 5 10 || models_ok=false
check_model "Face Landmarker" "$MODELS_DIR/face_landmarker.task" 3 30 || models_ok=false
check_model "Hand Landmarker" "$MODELS_DIR/hand_landmarker.task" 3 30 || models_ok=false

echo ""

if [ "$models_ok" = true ]; then
    echo "=================================================="
    echo "✓ All models present and valid!"
    echo "=================================================="
    echo ""
    echo "Pipeline ready to run:"
    echo "  python scripts/processing/run_pipeline.py"
    exit 0
else
    echo "=================================================="
    echo "⚠ Some models are missing or invalid"
    echo "=================================================="
    echo ""
    echo "To download missing models, run:"
    echo "  python scripts/tools/download_models.py"
    echo ""
    echo "Or see HAND_MODEL_SETUP.md for manual installation"
    exit 1
fi
