# Troubleshooting Guide

This guide helps resolve common issues when setting up and running the Smart Coach pipeline.

## Table of Contents
1. [Setup Issues](#setup-issues)
2. [Dependency Issues](#dependency-issues)
3. [Model Download Issues](#model-download-issues)
4. [Pipeline Runtime Errors](#pipeline-runtime-errors)
5. [Performance Issues](#performance-issues)
6. [Mobile Device Considerations](#mobile-device-considerations)

---

## Setup Issues

### Virtual Environment Not Found

**Problem:** `bash: mediapipe_env/bin/activate: No such file or directory`

**Solution:**
```bash
# Create the virtual environment first
python3 -m venv mediapipe_env

# Then activate it
source mediapipe_env/bin/activate  # Linux/Mac
# OR
mediapipe_env\Scripts\activate  # Windows
```

### Python Version Too Old

**Problem:** `Python 3.8 detected but 3.10+ required`

**Solution:**
```bash
# Check available Python versions
python3 --version
python3.10 --version
python3.11 --version

# Use a specific version
python3.10 -m venv mediapipe_env
```

On some systems, install newer Python:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv

# macOS with Homebrew
brew install python@3.10
```

---

## Dependency Issues

### "No module named 'torch'"

**Problem:** PyTorch not installed

**Solution:**
```bash
# Make sure virtual environment is activated
source mediapipe_env/bin/activate

# Install from requirements
pip install -r requirements.txt

# Or install manually
pip install torch torchvision
```

### "No module named 'cv2'"

**Problem:** OpenCV not installed

**Solution:**
```bash
pip install opencv-python
```

### "No module named 'mediapipe'"

**Problem:** MediaPipe not installed

**Solution:**
```bash
pip install mediapipe
```

### Conflicting Package Versions

**Problem:** `ERROR: pip's dependency resolver does not currently take into account all the packages that are installed`

**Solution:**
```bash
# Start fresh with a new virtual environment
deactivate  # if currently in one
rm -rf mediapipe_env
python3 -m venv mediapipe_env
source mediapipe_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### ImportError with MediaPipe Tasks API

**Problem:** `ImportError: cannot import name 'Image' from 'mediapipe.tasks.python.vision'`

**Solution:** This is a known issue. The pipeline has been updated to work around this. Make sure you have the latest code:
```bash
git pull origin main
```

---

## Model Download Issues

### Models Not Downloading

**Problem:** `download_models.py` fails or gets stuck

**Solution:**

**Option 1: Check network connection**
```bash
# Test if you can reach model sources
curl -I https://storage.googleapis.com/mediapipe-models/
curl -I https://github.com/ultralytics/assets/
```

**Option 2: Manual download**
```bash
cd data/models

# MediaPipe Hand Landmarker
wget https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

# YOLOv8 models (using ultralytics in Python)
python -c "from ultralytics import YOLO; YOLO('yolov8m-pose.pt')"
cp ~/.cache/ultralytics/yolov8m-pose.pt .

python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
cp ~/.cache/ultralytics/yolov8n.pt ./yolov8n-face.pt
```

**Option 3: Download on another device**
Download the files on a computer with better internet, then transfer via USB, cloud storage, or file sharing.

### Model Files Corrupted

**Problem:** Models downloaded but pipeline crashes with "model loading" errors

**Solution:**
```bash
# Check file sizes
ls -lh data/models/

# Expected sizes (approximately):
# yolov8m-pose.pt: ~52 MB
# yolov8n-face.pt: ~6 MB
# hand_landmarker.task: ~27 MB

# If sizes are wrong, delete and re-download
rm data/models/[corrupted-file]
python scripts/tools/download_models.py
```

---

## Pipeline Runtime Errors

### "Input video not found"

**Problem:** `FileNotFoundError: data/input/test_video.mp4`

**Solution:**
```bash
# Option 1: Add your own video
cp your_video.mp4 data/input/test_video.mp4

# Option 2: Generate test video
python scripts/tools/create_test_video.py

# Option 3: Edit the pipeline to use a different path
# In scripts/processing/run_pipeline.py, change:
# VIDEO_PATH = "data/input/your_video.mp4"
```

### "CUDA not available" or GPU Warnings

**Problem:** Pipeline shows CUDA/GPU warnings

**Solution:** This is **not an error**. The pipeline works fine on CPU, just slower.

To use GPU (optional):
1. Install NVIDIA drivers
2. Install CUDA toolkit (11.8 or 12.1)
3. Install PyTorch with CUDA:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

### "NNPACK warning"

**Problem:** `[W119] NNPACK.cpp Could not initialize NNPACK! Reason: Unsupported hardware.`

**Solution:** This is a **harmless warning**. The pipeline suppresses it by default. If you still see it:
```python
# Already handled in run_pipeline.py
os.environ["PYTORCH_NO_NNPACK"] = "1"
```

### Memory Error / Out of Memory

**Problem:** Pipeline crashes with `MemoryError` or `killed`

**Solution:**

**Option 1: Process shorter video**
```bash
# Use a video editing tool to extract first 10 seconds
ffmpeg -i your_video.mp4 -t 10 data/input/test_video.mp4
```

**Option 2: Lower resolution**
```bash
# Resize video to 720p
ffmpeg -i your_video.mp4 -vf scale=1280:720 data/input/test_video.mp4
```

**Option 3: Use lighter models**
Edit `scripts/processing/run_pipeline.py`:
```python
POSE_MODEL_PATH = "data/models/yolov8n-pose.pt"  # instead of yolov8m
```

### No Detections in Output

**Problem:** Pipeline runs but CSV has no pose/hand data

**Solution:**

1. **Check video content:**
   - Video must show a person clearly
   - Person should be mostly in frame
   - Lighting should be adequate

2. **Lower confidence threshold:**
   Edit `scripts/processing/run_pipeline.py`:
   ```python
   CONF_THRES = 0.1  # Lower from 0.2
   ```

3. **Check output video:**
   - View `data/output/output_full.mp4`
   - Look for skeleton overlays
   - If no overlays, detection is failing

---

## Performance Issues

### Pipeline is Very Slow

**Problem:** Processing takes hours for a short video

**Causes and Solutions:**

1. **CPU vs GPU:** CPU is 3-4x slower
   - Solution: Use GPU (see GPU setup above)

2. **Large video file:** High resolution or long duration
   - Solution: Resize or trim video (see Memory Error section)

3. **Heavy models:** Using large YOLOv8 models
   - Solution: Use lighter models (yolov8n instead of yolov8m)

**Expected Performance:**
- **CPU:** ~2-5 FPS (frames per second)
- **GPU:** ~10-15 FPS

For a 30-second video at 30 fps (900 frames):
- **CPU:** 3-7 minutes
- **GPU:** 1-2 minutes

### Mask R-CNN is the Bottleneck

**Problem:** Mask R-CNN (body segmentation) takes 80% of processing time

**Solution:** The pipeline documentation mentions caching strategies:
```python
# Cache Mask R-CNN inference every N frames instead of every frame
# This is a planned optimization - see ROADMAP.md
```

For now, you can:
1. Accept slower processing (it's accurate)
2. Use GPU acceleration (4x faster)
3. Wait for caching feature (planned enhancement)

---

## Mobile Device Considerations

### Limited Storage Space

**Problem:** Model files + dependencies take ~500 MB

**Solutions:**
1. Use external storage or cloud workspace
2. Use lighter models (saves ~50 MB)
3. Delete models after setup if space critical (keep in cloud backup)

### Limited RAM

**Problem:** Pipeline crashes or device freezes

**Solutions:**
1. Close all other apps
2. Process very short videos (5-10 seconds)
3. Use lower resolution videos
4. Consider cloud processing (Google Colab, Kaggle)

### Touch Keyboard Issues

**Problem:** Typing commands on mobile is difficult

**Solutions:**
1. Use Termux or similar terminal app with hardware keyboard support
2. Prepare commands in a notes app, copy/paste
3. Create shell scripts for common tasks:
   ```bash
   # Create run.sh
   echo '#!/bin/bash' > run.sh
   echo 'source mediapipe_env/bin/activate' >> run.sh
   echo 'python scripts/processing/run_pipeline.py' >> run.sh
   chmod +x run.sh
   
   # Then just run:
   ./run.sh
   ```

### No Hardware Acceleration

**Problem:** Mobile device has no CUDA/GPU support

**Solution:** CPU-only is fine for testing. For production:
1. Process videos on a desktop/server
2. Use cloud computing (AWS, GCP, Colab)
3. Accept slower processing times

---

## Getting More Help

If your issue isn't covered here:

1. **Check documentation:**
   - [SETUP.md](SETUP.md) - Setup guide
   - [README.md](README.md) - Project overview
   - [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) - Usage details

2. **Run verification:**
   ```bash
   python scripts/tools/verify_setup.py
   ```

3. **Check logs:**
   - Look for error messages in terminal output
   - Check `data/output/pipeline.log` if it exists

4. **Open an issue on GitHub:**
   Include:
   - Python version (`python --version`)
   - OS and version
   - Full error message
   - Steps to reproduce
   - Output of `verify_setup.py`

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Virtual env not found | `python3 -m venv mediapipe_env` |
| Dependencies not installed | `pip install -r requirements.txt` |
| Models not found | `python scripts/tools/download_models.py` |
| Input video missing | `cp your_video.mp4 data/input/test_video.mp4` |
| Out of memory | Use shorter/smaller video |
| Too slow | Use GPU or lighter models |
| No detections | Lower `CONF_THRES`, check video quality |

---

## Prevention Tips

1. **Always activate virtual environment** before running commands
2. **Verify setup** before running pipeline: `python scripts/tools/verify_setup.py`
3. **Test with short videos first** (5-10 seconds)
4. **Keep backups** of working model files
5. **Document your changes** if you modify pipeline settings
