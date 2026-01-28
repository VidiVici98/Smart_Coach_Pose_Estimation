# Smart Coach Setup Guide

## Quick Start (For New Environment Setup)

This guide will help you set up the Smart Coach Pose Estimation pipeline from scratch, even if you've lost your local development environment.

### Prerequisites

- Python 3.10 or 3.11 (recommended)
- pip package manager
- At least 4GB RAM
- ~2GB disk space for models and dependencies

### Step 1: Clone Repository

```bash
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv mediapipe_env

# Activate it
# On Linux/Mac:
source mediapipe_env/bin/activate
# On Windows:
# mediapipe_env\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Optional: Install development tools
pip install -r requirements-dev.txt
```

**Note on PyTorch:** The requirements.txt includes PyTorch CPU version. For GPU support:
```bash
# For CUDA 11.8 (check your CUDA version first)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Step 4: Download Required Model Files

The pipeline requires three model files in the `data/models/` directory:

#### 4.1. YOLOv8 Pose Model
```bash
# Using Python (recommended - automatic download)
python -c "from ultralytics import YOLO; YOLO('yolov8m-pose.pt')"
# This downloads to ~/.ultralytics/

# Move to project directory
mkdir -p data/models
mv ~/.cache/ultralytics/yolov8m-pose.pt data/models/
```

#### 4.2. YOLOv8 Face Model
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n-face.pt')"
mv ~/.cache/ultralytics/yolov8n-face.pt data/models/
```

**Alternative for YOLOv8 models:**
```bash
# Direct download with wget/curl
cd data/models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m-pose.pt
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-face.pt
```

#### 4.3. MediaPipe Hand Landmarker
```bash
cd data/models
wget https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

### Step 5: Prepare Test Video

You need a test video in `data/input/test_video.mp4`. You can:

**Option A: Use your own video**
```bash
# Copy your video
cp /path/to/your/video.mp4 data/input/test_video.mp4
```

**Option B: Generate a simple test video**
```bash
# Use the provided script to create a test pattern
python scripts/tools/create_test_video.py
```

**Option C: Download a sample (if available)**
```bash
# Add your own test video source here
```

### Step 6: Verify Setup

Run the verification script to check everything is configured correctly:

```bash
python scripts/tools/verify_setup.py
```

Expected output:
```
✓ Python version: 3.10.x
✓ Virtual environment: mediapipe_env activated
✓ Required packages installed
✓ Model files found:
  - data/models/yolov8m-pose.pt
  - data/models/yolov8n-face.pt
  - data/models/hand_landmarker.task
✓ Input video found: data/input/test_video.mp4
✓ Output directories exist
✓ GPU available: [Yes/No]

Setup complete! Ready to run pipeline.
```

### Step 7: Run the Pipeline

```bash
# Make sure virtual environment is activated
source mediapipe_env/bin/activate

# Run the main pipeline
python scripts/processing/run_pipeline.py
```

This will:
- Read from: `data/input/test_video.mp4`
- Output video to: `data/output/output_full.mp4`
- Output metrics to: `data/output/analytics.csv`

### Step 8: Validate Output

```bash
# Check the CSV structure
python scripts/tools/validate_metrics.py data/output/analytics.csv

# View the output video
# On Linux with VLC:
vlc data/output/output_full.mp4
# Or use any video player
```

## Troubleshooting

### "No module named 'torch'"
```bash
# Make sure virtual environment is activated
source mediapipe_env/bin/activate
pip install -r requirements.txt
```

### "Model file not found"
```bash
# Re-run model download steps
# Check that files exist:
ls -lh data/models/
```

### "Input video not found"
```bash
# Create test video or copy your own
python scripts/tools/create_test_video.py
# OR
cp your_video.mp4 data/input/test_video.mp4
```

### "CUDA not available" (Optional)
CPU processing works fine but is slower. For GPU acceleration:
1. Install NVIDIA drivers
2. Install CUDA toolkit
3. Install PyTorch with CUDA support (see Step 3)

### Memory Issues
If you get memory errors:
1. Use a shorter/lower resolution test video
2. Close other applications
3. Consider using lighter models (yolov8n instead of yolov8m)

## Mobile/Lightweight Setup

If working on a mobile device or constrained environment:

1. **Use lighter models:**
   - `yolov8n-pose.pt` instead of `yolov8m-pose.pt`
   - Edit `scripts/processing/run_pipeline.py` line 40

2. **Process shorter clips:**
   - Test with 5-10 second videos first

3. **Skip optional dependencies:**
   - Only install what's in `requirements.txt`
   - Skip `requirements-dev.txt`

## Quick Reference

### File Structure
```
Smart_Coach_Pose_Estimation/
├── data/
│   ├── input/          # Place test videos here
│   │   └── test_video.mp4
│   ├── output/         # Pipeline outputs go here
│   │   ├── output_full.mp4
│   │   └── analytics.csv
│   └── models/         # Model weights (download these)
│       ├── yolov8m-pose.pt
│       ├── yolov8n-face.pt
│       └── hand_landmarker.task
├── scripts/
│   └── processing/
│       └── run_pipeline.py  # Main script to run
└── mediapipe_env/      # Virtual environment (create this)
```

### Essential Commands
```bash
# Activate environment
source mediapipe_env/bin/activate

# Run pipeline
python scripts/processing/run_pipeline.py

# Verify setup
python scripts/tools/verify_setup.py

# Validate output
python scripts/tools/validate_metrics.py data/output/analytics.csv
```

## Next Steps

After successful setup:
1. Review [README.md](README.md) for project overview
2. Read [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) for detailed usage
3. Explore [ROADMAP.md](ROADMAP.md) for future enhancements
4. See [ENHANCEMENTS_QUICKSTART.md](ENHANCEMENTS_QUICKSTART.md) for optimization tips

## Getting Help

If you encounter issues not covered here:
1. Check the [docs/](docs/) directory for detailed documentation
2. Review error messages carefully
3. Open an issue on GitHub with:
   - Your Python version
   - Error message
   - Steps to reproduce

## Summary

**Minimum to run:**
1. Python 3.10+ with pip
2. Virtual environment created and activated
3. Dependencies installed (`pip install -r requirements.txt`)
4. Three model files in `data/models/`
5. Test video in `data/input/test_video.mp4`

**Then:**
```bash
python scripts/processing/run_pipeline.py
```

That's it! The pipeline will process your video and generate annotated output plus CSV metrics.
