# Mobile Quick Start (Android)

**One-click solution for running Smart Coach on Android phones using Termux.**

---

## Quick Start (3 Steps)

### 1. Install Termux
- Download **Termux** from [F-Droid](https://f-droid.org/en/packages/com.termux/) (not Play Store)
- Open Termux app

### 2. Setup (First Time Only)
```bash
# Install git and Python
pkg install git python

# Clone repository
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation
```

### 3. Run Mobile Script
```bash
bash mobile_runner.sh
```

That's it! The script will:
- ✅ Check your Python installation
- ✅ Install lightweight dependencies (numpy, opencv)
- ✅ Extract first 10 frames from test video
- ✅ Save frames as JPEGs for inspection

---

## What This Does (and Doesn't Do)

### ✅ What Works on Android:
- Frame extraction from videos
- Basic image processing
- Lightweight Python operations
- Viewing extracted frames

### ❌ What Doesn't Work on Android:
- **Full pose estimation** (requires PyTorch + YOLO models)
- Heavy ML inference (needs 8GB+ RAM, GPU)
- Real-time processing

---

## For Full Pipeline: Use GitHub Codespaces

**Recommended for mobile users who need full pose estimation:**

### Setup (One Time):
1. **Open GitHub on your phone browser**
2. Go to: https://github.com/VidiVici98/Smart_Coach_Pose_Estimation
3. Tap **Code** → **Codespaces** → **Create codespace on main**
4. Wait 1-2 minutes for environment to load

### Run Pipeline:
```bash
# In Codespace terminal
python scripts/processing/run_pipeline.py
```

### Download Results:
- Navigate to `data/output/` in file browser
- Download `output_full.mp4` and `analytics.csv`
- **Free tier:** 60 hours/month

---

## Why Codespaces?

| Feature | Android (Termux) | GitHub Codespaces |
|---------|------------------|-------------------|
| Frame extraction | ✅ Works | ✅ Works |
| Pose estimation | ❌ Too heavy | ✅ Full support |
| RAM needed | ~500MB | 8GB available |
| Speed | Slow | Fast (cloud CPU) |
| Cost | Free | Free (60h/month) |
| Setup time | 5 minutes | 2 minutes |

---

## Alternative: Google Colab

Another cloud option with free GPU:

1. Go to [Google Colab](https://colab.research.google.com/)
2. New Notebook → Run:
```python
!git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
%cd Smart_Coach_Pose_Estimation
!pip install -r requirements.txt
!python scripts/processing/run_pipeline.py
```

---

## File Sizes to Know

**Models (downloaded automatically):**
- YOLOv8 Pose: 51MB
- YOLOv8 Face: 6MB
- MediaPipe: 4MB
- Mask R-CNN: 180MB
- **Total:** ~250MB

**Not recommended for mobile data!** Use WiFi or Codespaces.

---

## Troubleshooting

### Termux: "pkg: command not found"
→ You're not in Termux. Install Termux from F-Droid.

### "Permission denied"
→ Run: `chmod +x mobile_runner.sh`

### "Video not found"
→ Place video at `data/input/test_video.mp4`

### "Out of memory"
→ Use Codespaces instead (Android has limited RAM)

---

## Quick Comparison

**Mobile Script (this file):**
- ⚡ Fast setup (5 min)
- 📱 Runs on phone
- 🎞️ Frame extraction only
- 🚫 No pose estimation

**Full Pipeline (Codespaces):**
- ⚡ Fast setup (2 min)
- ☁️ Runs in cloud
- 🎞️ Full video processing
- ✅ Complete pose estimation
- 📊 303 metrics per frame

---

## Next Steps

1. **Just exploring?** → Run `mobile_runner.sh` to see frame extraction
2. **Need full pipeline?** → Use GitHub Codespaces (see above)
3. **Questions?** → Check `docs/SETUP_AND_TROUBLESHOOTING.md`

---

**For complete documentation:** See `docs/README.md`

**Happy coaching! 🎯**
