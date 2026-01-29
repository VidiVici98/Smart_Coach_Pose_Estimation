#!/bin/bash
# Quick codespace setup verification and status check
# Run this to check if everything is ready to use

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=================================================="
echo "Smart Coach - Codespace Status Check"
echo "=================================================="
echo ""

# Check if in codespace
if [ -n "$CODESPACES" ] || [ -n "$SMART_COACH_CODESPACE" ]; then
    echo -e "${GREEN}✓${NC} Running in GitHub Codespace"
else
    echo -e "${YELLOW}⚠${NC} Not detected as codespace"
fi

echo ""
echo "1. Checking Python..."
if command -v python &> /dev/null || command -v python3 &> /dev/null; then
    PYTHON_CMD=$(command -v python3 || command -v python)
    VERSION=$($PYTHON_CMD --version 2>&1)
    echo -e "${GREEN}✓${NC} Python installed: $VERSION"
else
    echo -e "${RED}✗${NC} Python not found!"
    exit 1
fi

echo ""
echo "2. Checking dependencies..."
ERROR=0

check_package() {
    if $PYTHON_CMD -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 not installed"
        ERROR=1
    fi
}

check_package "torch"
check_package "cv2"
check_package "mediapipe"
check_package "ultralytics"
check_package "pandas"

if [ $ERROR -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}⚠${NC} Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

echo ""
echo "3. Checking models..."
MODEL_ERROR=0

check_model() {
    if [ -f "$1" ]; then
        SIZE=$(du -h "$1" | cut -f1)
        echo -e "${GREEN}✓${NC} $2: $SIZE"
    else
        echo -e "${RED}✗${NC} $2 not found"
        MODEL_ERROR=1
    fi
}

check_model "data/models/yolov8m-pose.pt" "YOLOv8 Pose"
check_model "data/models/yolov8n-face.pt" "YOLOv8 Face"
check_model "data/models/hand_landmarker.task" "Hand Landmarker"
if [ -f "data/models/face_landmarker.task" ]; then
    check_model "data/models/face_landmarker.task" "Face Landmarker (optional)"
fi

if [ $MODEL_ERROR -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}⚠${NC} Missing models. Downloading..."
    python scripts/tools/download_models.py
fi

echo ""
echo "4. Checking test video..."
if [ -f "data/input/test_video.mp4" ]; then
    SIZE=$(du -h "data/input/test_video.mp4" | cut -f1)
    echo -e "${GREEN}✓${NC} Test video found: $SIZE"
else
    echo -e "${YELLOW}⚠${NC} No test video found"
    echo "  You can:"
    echo "  - Create one: python scripts/tools/create_test_video.py"
    echo "  - Upload your own to: data/input/test_video.mp4"
fi

echo ""
echo "5. Checking output directory..."
if [ -d "data/output" ]; then
    echo -e "${GREEN}✓${NC} Output directory ready"
else
    mkdir -p data/output
    echo -e "${GREEN}✓${NC} Output directory created"
fi

echo ""
echo "6. Checking LOW_MEMORY_MODE configuration..."
# Check if running in codespace
if [ -n "$CODESPACES" ] || [ -n "$SMART_COACH_CODESPACE" ]; then
    if [ -z "$LOW_MEMORY_MODE" ] || [ "$LOW_MEMORY_MODE" != "false" ]; then
        echo -e "${GREEN}✓${NC} LOW_MEMORY_MODE will be enabled (codespace detected)"
        echo "  Mask R-CNN body segmentation will be disabled to save ~2GB RAM"
    else
        echo -e "${YELLOW}⚠${NC} LOW_MEMORY_MODE disabled (LOW_MEMORY_MODE=false)"
        echo "  All features enabled (requires 4-core/16GB codespace)"
    fi
else
    echo -e "${BLUE}ℹ${NC} Not in codespace - LOW_MEMORY_MODE will be OFF by default"
    echo "  Set LOW_MEMORY_MODE=true to enable memory saving mode"
fi

echo ""
echo "=================================================="
echo "Status Summary"
echo "=================================================="

if [ $ERROR -eq 0 ] && [ $MODEL_ERROR -eq 0 ]; then
    echo -e "${GREEN}✓ All systems ready!${NC}"
    echo ""
    echo "Run the pipeline with:"
    echo -e "${BLUE}  python scripts/processing/run_pipeline.py${NC}"
    echo ""
    echo "Output will be in:"
    echo "  - data/output/output_full.mp4 (annotated video)"
    echo "  - data/output/analytics.csv (metrics)"
else
    echo -e "${YELLOW}⚠ Setup incomplete${NC}"
    echo ""
    echo "Fix issues above, then run:"
    echo "  python scripts/tools/verify_setup.py"
fi

echo ""
echo "For help, see:"
echo "  - docs/guides/START_HERE_CODESPACE.md"
echo "  - docs/guides/CODESPACE_RECOVERY.md"
echo ""
