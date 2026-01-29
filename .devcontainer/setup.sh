#!/bin/bash
# Devcontainer setup script for Smart Coach Pose Estimation
# Runs automatically when codespace is created

set -e

echo "=================================================="
echo "Smart Coach Pose Estimation - Codespace Setup"
echo "=================================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in a codespace
if [ -n "$CODESPACES" ] || [ -n "$SMART_COACH_CODESPACE" ]; then
    print_status "Running in GitHub Codespace"
    IN_CODESPACE=true
else
    print_warning "Not detected as codespace, continuing anyway..."
    IN_CODESPACE=false
fi

# Update pip to latest version
echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet
print_status "Pip upgraded"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
echo "This may take a few minutes..."

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    print_status "Dependencies installed from requirements.txt"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Install dev requirements if available
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt --quiet 2>/dev/null || true
    print_status "Dev dependencies installed (optional)"
fi

# Create necessary directories
echo ""
echo "Setting up directory structure..."
mkdir -p data/models
mkdir -p data/input
mkdir -p data/output
print_status "Directories created"

# Download models with lightweight option for codespace
echo ""
echo "=================================================="
echo "Model Download"
echo "=================================================="
echo ""
print_warning "Using LIGHTWEIGHT models for codespace efficiency"
echo "  - Smaller file sizes (faster download)"
echo "  - Lower memory usage"
echo "  - Slightly reduced accuracy (acceptable for most use cases)"
echo ""

# Set environment variable for lightweight models
export USE_LIGHTWEIGHT_MODELS=true

if [ -f "scripts/tools/download_models.py" ]; then
    echo "Downloading models..."
    python scripts/tools/download_models.py || {
        print_error "Model download failed!"
        print_warning "You can download models later by running:"
        print_warning "  python scripts/tools/download_models.py"
    }
else
    print_warning "Model download script not found"
    print_warning "You may need to download models manually"
fi

# Check model status
echo ""
echo "Checking model files..."
if [ -f "data/models/yolov8m-pose.pt" ]; then
    size=$(du -h data/models/yolov8m-pose.pt | cut -f1)
    print_status "YOLOv8 Pose model: $size"
else
    print_warning "YOLOv8 Pose model not found"
fi

if [ -f "data/models/yolov8n-face.pt" ]; then
    size=$(du -h data/models/yolov8n-face.pt | cut -f1)
    print_status "YOLOv8 Face model: $size"
else
    print_warning "YOLOv8 Face model not found"
fi

if [ -f "data/models/hand_landmarker.task" ]; then
    size=$(du -h data/models/hand_landmarker.task | cut -f1)
    print_status "Hand Landmarker model: $size"
else
    print_warning "Hand Landmarker model not found"
fi

if [ -f "data/models/face_landmarker.task" ]; then
    size=$(du -h data/models/face_landmarker.task | cut -f1)
    print_status "Face Landmarker model: $size"
else
    print_warning "Face Landmarker model not found (optional)"
fi

# Create a test video if none exists
echo ""
if [ ! -f "data/input/test_video.mp4" ]; then
    print_warning "No test video found"
    if [ -f "scripts/tools/create_test_video.py" ]; then
        echo "Creating a test video..."
        python scripts/tools/create_test_video.py 2>/dev/null || {
            print_warning "Could not create test video"
            print_warning "You can add your own video to data/input/test_video.mp4"
        }
    fi
else
    size=$(du -h data/input/test_video.mp4 | cut -f1)
    print_status "Test video found: $size"
fi

# Print resource information
echo ""
echo "=================================================="
echo "Codespace Configuration"
echo "=================================================="
echo ""

# Check available resources
if command -v free &> /dev/null; then
    total_mem=$(free -h | awk '/^Mem:/ {print $2}')
    print_status "Available memory: $total_mem"
fi

if [ -n "$CODESPACE_VSCODE_FOLDER" ]; then
    print_status "Workspace: $CODESPACE_VSCODE_FOLDER"
fi

# Display next steps
echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
print_status "Codespace is ready for use"
echo ""
echo "Next steps:"
echo "  1. Check setup status:"
echo "     python scripts/tools/verify_setup.py"
echo ""
echo "  2. Add a video to process (if not using test video):"
echo "     Upload to data/input/test_video.mp4"
echo ""
echo "  3. Run the pipeline:"
echo "     python scripts/processing/run_pipeline.py"
echo ""
echo "  4. View results in:"
echo "     - data/output/output_full.mp4 (annotated video)"
echo "     - data/output/analytics.csv (metrics)"
echo ""
print_warning "Note: LOW_MEMORY_MODE is enabled by default for codespace"
print_warning "This disables Mask R-CNN to save memory (~2GB)"
echo ""
echo "For more information, see:"
echo "  - docs/guides/START_HERE_CODESPACE.md"
echo "  - README.md"
echo ""
