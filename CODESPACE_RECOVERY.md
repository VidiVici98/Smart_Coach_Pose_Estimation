# CODESPACE RECOVERY GUIDE

## Current Status (Post-Reorganization)

After investigating the repository in the codespace environment, here's what we found:

### ✅ What's Working:
1. **Repository structure** - All files in place after reorganization
2. **Test video** - `data/input/test_video.mp4` exists (file present)
3. **MediaPipe hand model** - `hand_landmarker.task` downloaded (7.5 MB)
4. **Output directory** - `data/output/` exists and ready

### ❌ What's Missing:
1. **YOLO models** - Two critical model files are missing:
   - `data/models/yolov8m-pose.pt` (YOLOv8 Pose Model)
   - `data/models/yolov8n-face.pt` (YOLOv8 Face Model)
2. **Python packages** - Need to verify installation status

### 🔍 Root Cause:
The YOLO models are not checked into git (correct - they're large binary files). They need to be downloaded fresh in the codespace environment.

## Quick Fix Instructions

### Option 1: Automated Fix (Recommended)
Run the diagnostic script I just created:

```bash
python3 check_status.py
```

This will show you exactly what's missing. Then:

```bash
# Install any missing packages
pip install -r requirements.txt

# Download the YOLO models
python3 scripts/tools/download_models.py
```

### Option 2: Manual YOLO Model Download
If the download script has issues, download manually:

```python
# In a Python shell or script:
from ultralytics import YOLO

# This downloads and caches the models
pose_model = YOLO('yolov8m-pose.pt')
face_model = YOLO('yolov8n.pt')  # Used as face model placeholder

# Then copy to data/models/
import shutil
from pathlib import Path

cache_dir = Path.home() / ".cache" / "ultralytics"
models_dir = Path("data/models")

# Find and copy pose model
for f in cache_dir.rglob("yolov8m-pose.pt"):
    shutil.copy(f, models_dir / "yolov8m-pose.pt")
    print(f"Copied pose model: {f}")
    break

# Find and copy face model (actually yolov8n.pt)
for f in cache_dir.rglob("yolov8n.pt"):
    shutil.copy(f, models_dir / "yolov8n-face.pt")
    print(f"Copied face model: {f}")
    break
```

### Option 3: Direct wget (If ultralytics fails)
```bash
cd data/models

# Download YOLOv8m Pose (~52MB)
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt

# Download YOLOv8n (~6MB - used as face model placeholder)
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
mv yolov8n.pt yolov8n-face.pt
```

## Verify Everything is Ready

After downloading models, verify:

```bash
# Quick check
ls -lh data/models/

# Should show:
#   yolov8m-pose.pt (~52 MB)
#   yolov8n-face.pt (~6 MB)
#   hand_landmarker.task (~7.5 MB)

# Comprehensive check
python3 scripts/tools/verify_setup.py
```

## Run the Pipeline

Once all models are present:

```bash
python3 scripts/processing/run_pipeline.py
```

Expected output:
- Processing messages for each frame
- Creates: `data/output/output_full.mp4` (annotated video)
- Creates: `data/output/analytics.csv` (frame-by-frame metrics)

## Troubleshooting

### If you see "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### If you see "FileNotFoundError" for models
- Recheck `data/models/` directory
- Ensure all 3 model files exist with correct names

### If processing is very slow
- This is normal in codespaces (CPU-only)
- YOLOv8, MediaPipe, and Mask R-CNN are computationally intensive
- A short test video may take several minutes

### If you see NNPACK warnings
- These are suppressed in the script and non-fatal
- Can be ignored - CPU inference will proceed normally

## Key Files Created for Your Convenience

I've created helper scripts in the repo root:

1. **check_status.py** - Quick diagnostic (no external dependencies needed)
2. **diagnose_and_fix.py** - Comprehensive diagnostic with auto-fix attempts  
3. **quick_check.sh** - Bash version of quick checks

Run any of these to see current status.

## Important Notes

### The "Face Model" Caveat
Per the project docs, `yolov8n-face.pt` is actually just `yolov8n.pt` (a generic object detector), **not** a true face-specific model. This is documented in the copilot instructions as a known limitation. For production use, you'd need a proper face detection model.

### Virtual Environment
The repo has `mediapipe_env/` but packages need to be installed. In codespaces, you may be using the system Python or codespace's default environment. Either way, ensure packages are installed:

```bash
# Check what Python you're using
which python3
python3 -m pip list | grep -E "torch|mediapipe|ultralytics"

# Install if needed
python3 -m pip install -r requirements.txt
```

## Next Steps After Pipeline Runs

1. Check output video: `data/output/output_full.mp4`
2. Review metrics: `data/output/analytics.csv`
3. See [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) for metric interpretation

## Summary

The reorganization didn't break anything structural - you just need to re-download the YOLO models in the new codespace environment. Use the download script or manual methods above, then you're good to go!
