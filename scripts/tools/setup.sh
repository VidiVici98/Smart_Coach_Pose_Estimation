#!/bin/bash
# One-command setup script for Smart Coach Pose Estimation
# This automates the entire setup process

set -e  # Exit on error

echo "============================================================"
echo "Smart Coach Pose Estimation - Automated Setup"
echo "============================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"

cd "$REPO_ROOT"
echo "Repository root: $REPO_ROOT"
echo ""

# Step 1: Check Python version
echo "Step 1/6: Checking Python version..."
PYTHON_CMD=""
for cmd in python3.11 python3.10 python3; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_CMD=$cmd
            echo "  ✓ Found $cmd (version $VERSION)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "  ✗ Python 3.10+ not found. Please install Python 3.10 or newer."
    exit 1
fi
echo ""

# Step 2: Create virtual environment
echo "Step 2/6: Creating virtual environment..."
if [ -d "mediapipe_env" ]; then
    echo "  ⚠ mediapipe_env already exists. Skipping creation."
else
    $PYTHON_CMD -m venv mediapipe_env
    echo "  ✓ Virtual environment created"
fi
echo ""

# Step 3: Activate and upgrade pip
echo "Step 3/6: Activating virtual environment and upgrading pip..."
source mediapipe_env/bin/activate
pip install --upgrade pip setuptools wheel -q
echo "  ✓ Pip upgraded"
echo ""

# Step 4: Install dependencies
echo "Step 4/6: Installing dependencies..."
echo "  This may take several minutes..."
pip install -r requirements.txt -q
if [ $? -eq 0 ]; then
    echo "  ✓ Dependencies installed"
else
    echo "  ✗ Dependency installation failed. Check error messages above."
    exit 1
fi
echo ""

# Step 5: Download models
echo "Step 5/6: Downloading model files..."
python scripts/tools/download_models.py
if [ $? -eq 0 ]; then
    echo "  ✓ Models downloaded"
else
    echo "  ⚠ Model download encountered issues. You may need to download manually."
    echo "    See SETUP.md for manual download instructions."
fi
echo ""

# Step 6: Verify setup
echo "Step 6/6: Verifying setup..."
python scripts/tools/verify_setup.py
VERIFY_EXIT=$?
echo ""

# Final instructions
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""

if [ $VERIFY_EXIT -eq 0 ]; then
    echo "✓ All components installed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Add a test video:"
    echo "     cp your_video.mp4 data/input/test_video.mp4"
    echo "     OR"
    echo "     python scripts/tools/create_test_video.py"
    echo ""
    echo "  2. Run the pipeline:"
    echo "     python scripts/processing/run_pipeline.py"
    echo ""
else
    echo "⚠ Setup completed with warnings. Review output above."
    echo ""
    echo "Common fixes:"
    echo "  - Missing test video: cp your_video.mp4 data/input/test_video.mp4"
    echo "  - Model download failed: See SETUP.md for manual instructions"
    echo ""
fi

echo "Documentation:"
echo "  - SETUP.md - Detailed setup instructions"
echo "  - TROUBLESHOOTING.md - Common issues and solutions"
echo "  - README.md - Project overview"
echo ""

echo "To activate the environment in the future:"
echo "  source mediapipe_env/bin/activate"
echo ""
echo "============================================================"
