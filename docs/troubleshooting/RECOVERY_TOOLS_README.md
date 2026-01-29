# Recovery & Diagnostic Tools

This directory contains helper scripts created to recover the Smart Coach pipeline in your codespace environment after the repository reorganization.

## Quick Reference

| File | Purpose | How to Use |
|------|---------|------------|
| **START_HERE_CODESPACE.md** | Quick start guide | Read this first! |
| **emergency_fix.sh** | One-command automated fix | `bash emergency_fix.sh` |
| **setup_and_run.ipynb** | Interactive setup notebook | Open in Jupyter/VS Code |
| **check_status.py** | Quick diagnostic | `python3 check_status.py` |
| **diagnose_and_fix.py** | Full diagnostic + auto-fix | `python3 diagnose_and_fix.py` |
| **quick_check.sh** | Bash diagnostic | `bash quick_check.sh` |
| **CODESPACE_RECOVERY.md** | Detailed recovery guide | Reference documentation |

## The Problem

After switching to codespace, the YOLO model files (which aren't checked into git) need to be re-downloaded:
- `data/models/yolov8m-pose.pt` (~52 MB)
- `data/models/yolov8n-face.pt` (~6 MB)

## The Solution

Run the emergency fix script:

```bash
bash emergency_fix.sh
```

Or follow the interactive notebook:
1. Open `setup_and_run.ipynb`
2. Run each cell in order
3. Watch the status checks and proceed

## What These Scripts Do

### 1. Emergency Fix (Recommended)
**File:** `emergency_fix.sh`

Fully automated:
- Installs missing Python packages
- Downloads YOLO models
- Copies them to correct location
- Runs the pipeline

**Usage:**
```bash
bash emergency_fix.sh
```

### 2. Interactive Notebook
**File:** `setup_and_run.ipynb`

Step-by-step with explanations:
- Check Python version
- Check/install packages
- Check/download models
- Verify test video
- Run pipeline
- View results

**Usage:**
- Open in VS Code or Jupyter
- Run cells one by one
- See immediate feedback

### 3. Quick Status Check
**File:** `check_status.py`

Fast diagnostic (no external deps):
- Python version
- Installed packages
- Model files
- Test video
- Directory structure

**Usage:**
```bash
python3 check_status.py
```

### 4. Comprehensive Diagnostic
**File:** `diagnose_and_fix.py`

Advanced version with auto-fix:
- All checks from quick status
- Attempts to auto-install packages
- Attempts to auto-download models
- Offers to run pipeline
- Detailed error messages

**Usage:**
```bash
python3 diagnose_and_fix.py
```

### 5. Bash Diagnostic
**File:** `quick_check.sh`

Shell-based checker:
- Simple bash commands
- No Python imports needed
- Good for debugging Python issues

**Usage:**
```bash
bash quick_check.sh
```

## After Running the Fix

### Check Output
```bash
ls -lh data/output/
```

You should see:
- `output_full.mp4` - Your video with AI overlays
- `analytics.csv` - Frame-by-frame metrics

### View the Video
```bash
# If you have a video player
xdg-open data/output/output_full.mp4

# Or download via VS Code file explorer
```

### Analyze the Data
```python
import pandas as pd
df = pd.read_csv('data/output/analytics.csv')
print(df.head())
print(df.columns)
```

See [docs/USAGE_GUIDE.md](../docs/USAGE_GUIDE.md) for metric interpretation.

## Troubleshooting

### Scripts Won't Run
```bash
# Make them executable
chmod +x emergency_fix.sh quick_check.sh

# Run with explicit interpreter
bash emergency_fix.sh
python3 check_status.py
```

### Still Getting Errors
1. Read `CODESPACE_RECOVERY.md` for detailed manual steps
2. Check `TROUBLESHOOTING.md` in repo root
3. Check `SETUP.md` for comprehensive setup guide

### Models Won't Download
Try manual download:
```bash
cd data/models
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt
mv yolov8n.pt yolov8n-face.pt
```

### Python Packages Won't Install
```bash
# Upgrade pip first
pip install --upgrade pip

# Try again
pip install -r requirements.txt

# If specific package fails, try one by one
pip install torch torchvision
pip install mediapipe
pip install ultralytics
```

## Why These Files Exist

You mentioned losing your local development laptop and moving to a codespace. The repository reorganization was fine - the issue is simply that large model files aren't stored in git and need to be re-downloaded in new environments.

These scripts automate that recovery process so you can get back to work quickly.

## Cleanup (Optional)

Once everything is working, you can optionally remove these helper files:

```bash
rm -f emergency_fix.sh check_status.py diagnose_and_fix.py quick_check.sh
rm -f START_HERE_CODESPACE.md CODESPACE_RECOVERY.md
rm -f setup_and_run.ipynb
rm -f RECOVERY_TOOLS_README.md  # This file
```

They're already gitignored (except the notebook), so they won't be committed.

## Official Setup Documentation

For future reference, the standard setup process is documented in:
- [SETUP.md](../SETUP.md) - Full setup guide
- [scripts/tools/setup.sh](../scripts/tools/setup.sh) - Official setup script
- [scripts/tools/download_models.py](../scripts/tools/download_models.py) - Official model downloader
- [scripts/tools/verify_setup.py](../scripts/tools/verify_setup.py) - Official verification

## Summary

**Problem:** Missing YOLO models after codespace switch
**Solution:** `bash emergency_fix.sh`
**Time:** 2-5 minutes
**Result:** Ready to process videos

Good luck! 🚀
