# 🚀 QUICK START - CODESPACE EDITION

## TL;DR - The Problem
After repo reorganization + switching to codespace, you're missing the YOLO model files that aren't checked into git. Everything else is fine.

## 🎯 ONE-LINE FIX

Run this in your terminal:

```bash
bash emergency_fix.sh
```

This will:
1. Install any missing Python packages
2. Download the 2 missing YOLO models (~58 MB total)
3. Run the pipeline on your test video

Expected time: 2-5 minutes for setup + processing time (depends on video length).

---

## 📊 Alternative: Use the Interactive Notebook

Open and run: **`setup_and_run.ipynb`**

This gives you cell-by-cell control with status checks at each step.

---

## 🔍 Want to Diagnose First?

Check what's missing:

```bash
python3 check_status.py
```

Or full diagnostic:

```bash
python3 diagnose_and_fix.py
```

---

## 📝 What's Actually Missing

From my scan of your codespace:

### ✅ Present:
- All code files ✓
- Test video (data/input/test_video.mp4) ✓
- MediaPipe hand model (7.5 MB) ✓
- Directory structure ✓

### ❌ Missing:
- `data/models/yolov8m-pose.pt` (~52 MB)
- `data/models/yolov8n-face.pt` (~6 MB)

### ❓ Unknown:
- Python package installation status (likely need `pip install -r requirements.txt`)

---

## 🛠️ Manual Fix (If Scripts Fail)

### Step 1: Install Packages
```bash
pip install -r requirements.txt
```

### Step 2: Download Models

**Option A - Use the download script:**
```bash
python3 scripts/tools/download_models.py
```

**Option B - Direct Python:**
```python
from ultralytics import YOLO
import shutil
from pathlib import Path

# Download
YOLO('yolov8m-pose.pt')
YOLO('yolov8n.pt')

# Copy to data/models/
cache = Path.home() / ".cache" / "ultralytics"
models = Path("data/models")

for f in cache.rglob("yolov8m-pose.pt"):
    shutil.copy(f, models / "yolov8m-pose.pt")
    break

for f in cache.rglob("yolov8n.pt"):
    shutil.copy(f, models / "yolov8n-face.pt")
    break
```

**Option C - wget:**
```bash
cd data/models
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
mv yolov8n.pt yolov8n-face.pt
```

### Step 3: Verify
```bash
ls -lh data/models/
# Should show all 3 files:
#   yolov8m-pose.pt, yolov8n-face.pt, hand_landmarker.task
```

### Step 4: Run
```bash
python3 scripts/processing/run_pipeline.py
```

---

## 📂 Output Location

After successful run:
- **Video:** `data/output/output_full.mp4` (your video with skeleton overlays)
- **Metrics:** `data/output/analytics.csv` (frame-by-frame data)

---

## ⏱️ How Long Will It Take?

**Setup:** 2-5 minutes (downloading models)
**Processing:** Depends on video length
- ~30 second video = ~5-10 minutes in codespace (CPU-only)
- Longer videos scale proportionally

This is normal - the pipeline runs 5 AI models per frame:
1. YOLOv8 Pose
2. YOLOv8 Face
3. MediaPipe Hands
4. Mask R-CNN (body segmentation)
5. MediaPipe Face Mesh

---

## 🐛 Troubleshooting

### "No module named 'torch'"
```bash
pip install -r requirements.txt
```

### "FileNotFoundError: yolov8m-pose.pt"
Models didn't download. See Step 2 above.

### "NNPACK warnings"
Ignore - these are suppressed and non-fatal.

### Pipeline runs but produces errors
Check: `python3 scripts/tools/verify_setup.py` for diagnostics

---

## 📚 More Help

- **Full setup guide:** [SETUP.md](SETUP.md)
- **Detailed recovery:** [CODESPACE_RECOVERY.md](CODESPACE_RECOVERY.md)
- **Usage guide:** [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## ✨ Files I Created For You

I've added several helper files to the repo root to make this easier:

1. **emergency_fix.sh** - One-command fix (run this first!)
2. **setup_and_run.ipynb** - Interactive Jupyter notebook version
3. **check_status.py** - Quick diagnostic
4. **diagnose_and_fix.py** - Comprehensive diagnostic with auto-fix
5. **quick_check.sh** - Bash diagnostic
6. **CODESPACE_RECOVERY.md** - Detailed recovery guide
7. **THIS FILE** - Quick start reference

All of these are git-ignored by default, so they won't pollute your repo.

---

## 🎬 Ready? Let's Go!

```bash
bash emergency_fix.sh
```

That's it! 🚀
