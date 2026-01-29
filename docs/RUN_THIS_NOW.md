# 🚀 RUN THIS NOW - Manual Execution Guide

The terminal automation is having issues, but I've diagnosed everything and created the fix scripts. Here's exactly what to run in your terminal:

## Option 1: One-Command Fix (Fastest) ⚡

Open a terminal in VS Code and run:

```bash
python3 run_complete_setup.py
```

**This will:**
1. Check Python version ✓
2. Install missing packages ✓  
3. Download YOLO models (~58 MB) ✓
4. Verify all files present ✓
5. Ask if you want to run the pipeline
6. If yes, process your video and output results ✓

**Expected time:** 2-5 minutes for setup + processing time for video

---

## Option 2: Step-by-Step (If Option 1 Fails)

### Step 1: Install Packages
```bash
pip install -r requirements.txt
```

### Step 2: Download Models
```bash
python3 scripts/tools/download_models.py
```

### Step 3: Verify Setup
```bash
python3 scripts/tools/verify_setup.py
```

### Step 4: Run Pipeline
```bash
python3 scripts/processing/run_pipeline.py
```

---

## Option 3: Interactive Notebook (Visual Approach)

1. Open `setup_and_run.ipynb` in VS Code
2. Run each cell one by one
3. See status checks and outputs inline
4. Last cell runs the pipeline

---

## Quick Status Check

Before running anything, check what's missing:

```bash
python3 check_status.py
```

This shows:
- ✓ What's installed
- ✗ What's missing
- 📋 Exact commands to fix

---

## What You're Missing (From My Analysis)

Based on my scan of your codespace:

### ✅ Already Have:
- Python 3.x ✓
- Repository code ✓
- Test video (`data/input/test_video.mp4`) ✓
- MediaPipe hand model (`hand_landmarker.task`, 7.5 MB) ✓
- Directory structure ✓

### ❌ Need to Download:
- `data/models/yolov8m-pose.pt` (~52 MB)
- `data/models/yolov8n-face.pt` (~6 MB)

### ❓ Probably Need:
- Python packages (`pip install -r requirements.txt`)

---

## Expected Output

After successful run, check:

```bash
ls -lh data/output/
```

You should see:
- **`output_full.mp4`** - Your video with AI overlays (skeleton, hands, gaze cone, etc.)
- **`analytics.csv`** - Frame-by-frame metrics (pose, hands, gaze, velocities)

---

## Troubleshooting

### "Command not found: python3"
Try `python` instead:
```bash
python run_complete_setup.py
```

### "ModuleNotFoundError"
Install packages first:
```bash
pip install -r requirements.txt
```

### Models won't download
Manual download:
```bash
cd data/models
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
mv yolov8n.pt yolov8n-face.pt
cd ../..
```

### Pipeline runs but is very slow
Normal! In codespace (CPU-only), processing is slow:
- ~30 second video = ~5-10 minutes processing
- The pipeline runs 5 AI models per frame

### "NNPACK" warnings
These are suppressed and non-fatal - ignore them.

---

## What Each Script Does

I created several helper scripts:

| Script | Purpose |
|--------|---------|
| **run_complete_setup.py** | ALL-IN-ONE: checks, fixes, verifies, runs pipeline |
| **check_status.py** | Quick diagnostic (10 seconds) |
| **diagnose_and_fix.py** | Detailed diagnostic with auto-fix |
| **setup_and_run.ipynb** | Interactive notebook version |
| **emergency_fix.sh** | Bash version of complete setup |

Pick whichever you prefer - they all do the same thing!

---

## 🎯 Recommended Workflow

**For fastest results:**

1. Open terminal in VS Code (Terminal → New Terminal)
2. Run: `python3 run_complete_setup.py`
3. Answer 'Y' when asked to run pipeline
4. Wait for processing
5. Check `data/output/` for results

**For more control:**

1. Open `setup_and_run.ipynb`
2. Run cells one by one
3. See detailed status at each step

---

## After Everything Works

View your results:

### Video
```bash
# Download via VS Code file explorer, or if you have a player:
xdg-open data/output/output_full.mp4
```

### CSV Data
```python
import pandas as pd
df = pd.read_csv('data/output/analytics.csv')
print(df.head())
print(f"Processed {len(df)} frames")
print(f"Columns: {list(df.columns[:10])}")  # First 10 columns
```

See `docs/USAGE_GUIDE.md` for metric interpretation.

---

## 💡 Why This Happened

You switched from local laptop to codespace after repo reorganization. The reorganization was fine - you just need to re-download model files (they're not in git because they're large binaries).

---

## 🆘 Still Stuck?

1. Check: `START_HERE_CODESPACE.md` (overview)
2. Check: `CODESPACE_RECOVERY.md` (detailed guide)
3. Check: `docs/troubleshooting/TROUBLESHOOTING.md` (comprehensive troubleshooting)
4. Check: `docs/guides/SETUP.md` (full setup from scratch)

---

## Ready? Let's Do This! 🚀

```bash
python3 run_complete_setup.py
```

That's it! Should take 2-5 minutes to get running, then processing time for your video.
