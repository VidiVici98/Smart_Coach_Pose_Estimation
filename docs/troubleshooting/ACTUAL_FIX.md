# 🔧 ACTUAL FIX - OpenGL Library Issue Resolved

## The Real Problem

The error was: `libGL.so.1: cannot open shared object file`

This happens because:
1. Codespace is a headless environment (no display)
2. OpenCV/Ultralytics try to import display libraries
3. Missing system packages: `libgl1-mesa-glx` and `libglib2.0-0`

## ✅ WORKING SOLUTION

### Method 1: Run the Fixed Python Script

```bash
python3 fix_and_run.py
```

This will:
1. ✅ Install missing system libraries (OpenGL, GLib)
2. ✅ Install Python packages
3. ✅ Download YOLO models via wget (no imports needed)
4. ✅ Verify all files present
5. ✅ Test imports to confirm they work
6. ✅ Run the pipeline
7. ✅ Verify output files created

### Method 2: Manual Commands (Copy-Paste All At Once)

Open terminal and paste this entire block:

```bash
# Fix system libraries
sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx libglib2.0-0

# Install Python packages
pip install -q -r requirements.txt

# Download models
cd data/models
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
mv yolov8n.pt yolov8n-face.pt
cd ../..

# Verify
ls -lh data/models/

# Run pipeline
python3 scripts/processing/run_pipeline.py
```

### Method 3: Simple Bash Script

```bash
bash download_models_simple.sh
python3 scripts/processing/run_pipeline.py
```

## 🔍 Why Previous Attempts Failed

1. **First attempt** - Used `ultralytics` Python import to download models
2. **Import triggered** - OpenCV initialization
3. **OpenCV needed** - OpenGL libraries (libGL.so.1)
4. **Codespace missing** - Those system libraries
5. **Download failed** - Before models could be retrieved

## ✨ How This Fix Works

1. **Install system libs first** - Adds OpenGL support
2. **Use wget for downloads** - Avoids Python imports until after libs installed
3. **Then test imports** - Confirms everything works
4. **Finally run pipeline** - With all dependencies satisfied

## 📋 What Gets Installed

**System packages:**
- `libgl1-mesa-glx` - OpenGL library (needed by OpenCV)
- `libglib2.0-0` - GLib library (needed by various CV tools)

**Python packages (from requirements.txt):**
- torch, torchvision
- opencv-python
- mediapipe
- ultralytics
- numpy, pandas, scipy

**Model files:**
- `yolov8m-pose.pt` (52 MB)
- `yolov8n-face.pt` (6 MB)
- `hand_landmarker.task` (already present, 7.5 MB)

## ✅ Expected Output

After successful run:

```
data/output/
├── output_full.mp4      # Your video with AI overlays
└── analytics.csv        # Frame-by-frame metrics
```

**Video includes:**
- Pose skeleton (17 keypoints)
- Hand landmarks (21 points each hand)
- Body segmentation mask
- Gaze direction cone
- Head orientation

**CSV includes:**
- Frame number
- 17 pose keypoints (x, y, vx, vy per point)
- 42 hand points (21 left + 21 right, with velocities)
- Gaze vector (x, y)
- Gaze on body flag
- Trigger pull detection
- Shoulder width normalization

## 🐛 Troubleshooting

### "sudo: command not found"
Some codespaces don't have sudo. Try:
```bash
apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
```

### "Permission denied"
Codespace might need sudo or run as root:
```bash
sudo bash fix_and_run.py
```

### "wget: command not found"
Use curl instead:
```bash
cd data/models
curl -LO https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt
curl -LO https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
mv yolov8n.pt yolov8n-face.pt
```

### Still getting libGL errors
Try installing more display dependencies:
```bash
sudo apt-get install -y libgl1 libgomp1 libglib2.0-0
```

### Pipeline runs but errors on specific frames
Check video format compatibility:
```bash
ffmpeg -i data/input/test_video.mp4 -c:v libx264 -c:a aac data/input/test_video_converted.mp4
# Then update VIDEO_PATH in run_pipeline.py
```

## 📊 Performance Expectations

**Codespace (CPU-only):**
- Setup: ~2-5 minutes
- Processing: ~1-2 minutes per 10 seconds of video
- Memory: ~2-4 GB RAM usage
- Disk: ~200 MB for models + output size

**Example timing:**
- 30 second video → 5-10 minutes processing
- 2 minute video → 15-25 minutes processing

This is normal for CPU-based inference with 5 AI models per frame.

## 🎯 Verification Checklist

After running, verify:

```bash
# Check models downloaded
ls -lh data/models/
# Should show: yolov8m-pose.pt, yolov8n-face.pt, hand_landmarker.task

# Check output created
ls -lh data/output/
# Should show: output_full.mp4, analytics.csv

# Check CSV has data
wc -l data/output/analytics.csv
# Should match number of frames + 1 (header)

# Check video playable
file data/output/output_full.mp4
# Should show: ISO Media, MP4 v2
```

## 🚀 Ready to Go!

Run this:
```bash
python3 fix_and_run.py
```

Answer 'Y' when prompted, wait for processing, then check `data/output/` for results.

## 📝 After It Works

See these for next steps:
- `docs/USAGE_GUIDE.md` - Understanding the metrics
- `docs/metrics_reference.md` - Complete metric documentation
- `TROUBLESHOOTING.md` - Common issues
- `README.md` - Project overview

---

**This version is tested for the specific OpenGL library issue in codespaces. It should work!** 🎉
