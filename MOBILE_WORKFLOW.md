# Mobile Workflow Guide

This guide provides practical advice for working with the Smart Coach pipeline on mobile devices (phones, tablets, or other constrained environments).

## Quick Assessment: Can You Run This on Mobile?

### ✅ What Works Well on Mobile
- Reading documentation
- Viewing code and making small edits
- Git operations (clone, commit, push)
- Running setup verification
- Analyzing CSV output files (with pandas)

### ⚠️ What's Challenging on Mobile
- Installing dependencies (can take 10-30 minutes)
- Running the full pipeline (CPU-intensive, slow)
- Processing long/high-resolution videos
- Working with large model files (85 MB total)

### ❌ What Doesn't Work on Mobile
- GPU acceleration (most mobile devices don't support CUDA)
- Real-time processing
- Batch processing of multiple videos

## Recommended Mobile Workflows

### Workflow 1: Documentation & Code Review (100% Mobile)
**Best for:** Understanding the project, planning changes, reviewing code

```bash
# 1. Clone the repo
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation

# 2. Browse documentation
cat README.md
cat SETUP.md
cat TROUBLESHOOTING.md

# 3. Review code
cat scripts/processing/run_pipeline.py
cat smart_coach/constants/pose_landmarks.py

# 4. Make small edits if needed
nano README.md  # or use your mobile editor
git add README.md
git commit -m "Update documentation"
git push
```

**Tools needed:**
- Termux (Android) or iSH Shell (iOS)
- Git
- Text editor (nano, vim, or mobile app)

---

### Workflow 2: Setup & Verification Only (Mobile-Friendly)
**Best for:** Preparing the environment, checking what's missing

```bash
# 1. Clone the repo
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation

# 2. Create virtual environment (lightweight)
python3 -m venv mediapipe_env
source mediapipe_env/bin/activate

# 3. Check what's needed (no heavy downloads yet)
python scripts/tools/verify_setup.py

# 4. Review requirements without installing
cat requirements.txt

# 5. Check available disk space
df -h .
```

**Time:** ~2 minutes  
**Data usage:** Minimal (~50 MB for repo)  
**Storage:** ~100 MB

---

### Workflow 3: Hybrid (Setup on Cloud, Use Mobile for Control)
**Best for:** Actual pipeline execution with mobile monitoring

**Option A: GitHub Codespaces**
1. Open repository on github.com (mobile browser)
2. Click "Code" → "Codespaces" → "Create codespace"
3. Run setup in cloud environment:
   ```bash
   bash scripts/tools/setup.sh
   ```
4. Upload video, run pipeline, download results
5. Analyze results on mobile

**Option B: Google Colab**
1. Create a Colab notebook on mobile browser
2. Clone and setup:
   ```python
   !git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
   %cd Smart_Coach_Pose_Estimation
   !pip install -q -r requirements.txt
   !python scripts/tools/download_models.py
   ```
3. Upload test video
4. Run pipeline:
   ```python
   !python scripts/processing/run_pipeline.py
   ```
5. Download results to mobile

**Option C: Cloud VM (AWS, GCP, Azure)**
1. SSH into cloud instance from mobile
2. Run full setup and pipeline
3. Use `scp` or cloud storage to download results

**Time:** ~15-30 minutes total  
**Cost:** Free (Codespaces/Colab) or paid (VMs)  
**Advantage:** GPU acceleration available

---

### Workflow 4: Minimal Mobile Processing (Advanced)
**Best for:** Testing with very short clips only

```bash
# 1. Complete setup (be patient, takes time)
bash scripts/tools/setup.sh
# This will take 15-30 minutes on mobile

# 2. Create a VERY short test video (5 seconds)
python scripts/tools/create_test_video.py
# Then manually edit or use ffmpeg to keep only 5 seconds:
ffmpeg -i data/input/test_video.mp4 -t 5 data/input/short_test.mp4

# 3. Edit pipeline to use short video
nano scripts/processing/run_pipeline.py
# Change: VIDEO_PATH = "data/input/short_test.mp4"

# 4. Use lightest models
# Change: POSE_MODEL_PATH = "data/models/yolov8n-pose.pt"

# 5. Run pipeline (expect 5-10 minutes for 5-second video)
python scripts/processing/run_pipeline.py

# 6. Analyze results
python -c "import pandas as pd; df = pd.read_csv('data/output/analytics.csv'); print(df.head())"
```

**Time:** 45-60 minutes total  
**Processing speed:** ~1-2 FPS on mobile CPU  
**Practical for:** 5-10 second test clips only

---

## Mobile Setup Challenges & Solutions

### Challenge 1: Limited Storage
**Problem:** Model files (85 MB) + dependencies (200+ MB) + Python packages (300+ MB)

**Solutions:**
- Use external SD card (Android)
- Clear app cache before setup
- Use cloud storage for model files (download when needed)
- Delete models after processing (keep backup)

```bash
# Store models in cloud, download on demand
# (Requires setup once)
rclone copy data/models/ gdrive:smart_coach/models/

# Before processing, download models
rclone copy gdrive:smart_coach/models/ data/models/

# After processing, remove models to save space
rm -rf data/models/*.pt data/models/*.task
```

### Challenge 2: Slow Installation
**Problem:** `pip install -r requirements.txt` takes 20-30 minutes

**Solutions:**
- Do it once, keep the virtual environment
- Install overnight when connected to charger
- Use pre-built wheels if available
- Install packages individually as needed

```bash
# Install just what you need for a specific task
pip install numpy pandas  # For data analysis only
pip install opencv-python  # For video manipulation only
```

### Challenge 3: Battery Drain
**Problem:** Pipeline processing drains battery quickly

**Solutions:**
- Process only when connected to power
- Use cloud processing (see Workflow 3)
- Process shorter videos
- Lower priority: `nice -n 19 python scripts/processing/run_pipeline.py`

### Challenge 4: Typing on Mobile
**Problem:** Typing long commands is difficult

**Solutions:**
- Create shell script shortcuts:
  ```bash
  # Save common commands
  echo '#!/bin/bash' > run.sh
  echo 'source mediapipe_env/bin/activate' >> run.sh
  echo 'python scripts/processing/run_pipeline.py' >> run.sh
  chmod +x run.sh
  
  # Then just run:
  ./run.sh
  ```

- Use command history: Press ↑ to recall previous commands
- Prepare commands in notes app, copy/paste
- Use external keyboard if available

### Challenge 5: Network Issues
**Problem:** Large downloads fail on mobile networks

**Solutions:**
- Download on WiFi only
- Use download managers with resume capability
- Download models separately on another device, transfer via USB
- Use manual download instructions in SETUP.md

```bash
# Alternative: Download models on desktop, transfer via USB or cloud
# On desktop:
# 1. Download models to Desktop/smart_coach_models/
# 2. Upload to Google Drive / Dropbox
# On mobile:
# 3. Download from cloud to data/models/
```

---

## Recommended Mobile Apps & Tools

### Android
- **Termux** - Full Linux terminal environment
  - Install: Google Play Store or F-Droid
  - Setup Python: `pkg install python`
  - Install Git: `pkg install git`

- **AnLinux** - Run Linux distributions
  - More powerful but heavier
  - Can run full Ubuntu/Debian

- **Text Editors:**
  - QuickEdit Text Editor
  - Acode
  - Turbo Editor

### iOS
- **iSH Shell** - Linux shell emulator
  - Limited but functional
  - Slower than Termux

- **Working Copy** - Git client with editor
  - Excellent for code review and small edits

- **Pythonista** - Python IDE
  - Can't install all dependencies but useful for scripts

### Cross-Platform
- **GitHub Mobile App** - Code review, commits
- **Jupyter Mobile** - Notebook interface (if using Colab)
- **Solid Explorer** - File management

---

## Performance Expectations

### Test Scenario: 10-second video at 720p (300 frames)

| Device Type | Time to Process | Practical? |
|-------------|----------------|------------|
| High-end phone (2023+) | 30-45 minutes | Barely |
| Mid-range phone | 60-90 minutes | No |
| Low-end phone/tablet | 2+ hours | No |
| Laptop (CPU) | 5-10 minutes | Yes |
| Desktop (GPU) | 1-2 minutes | Yes |

**Recommendation:** For videos longer than 10 seconds, use cloud processing.

---

## Practical Mobile Workflows by Use Case

### Use Case 1: "I want to understand the code"
**Workflow:** Documentation & Code Review (Workflow 1)
- Time: Any
- Storage: Minimal
- Network: Low
- ✅ 100% doable on mobile

### Use Case 2: "I want to test if it works"
**Workflow:** Hybrid with Colab (Workflow 3B)
- Time: 30 minutes
- Storage: Minimal on mobile
- Network: Medium
- ✅ Very practical

### Use Case 3: "I need to process one quick video"
**Workflow:** Hybrid with Codespaces (Workflow 3A)
- Time: 20 minutes
- Storage: Minimal on mobile
- Network: Medium
- ✅ Recommended approach

### Use Case 4: "I want to analyze existing results"
**Tools:** pandas on mobile
```bash
# If you already have analytics.csv
source mediapipe_env/bin/activate
pip install pandas jupyter
jupyter notebook
# Open notebook, analyze data
```
- ✅ Works well on mobile

### Use Case 5: "I need to contribute code"
**Workflow:** Edit on mobile, test on cloud
1. Make edits on mobile (small files)
2. Commit and push to your branch
3. Test on Codespaces or CI
- ✅ Practical for documentation and small changes

---

## Step-by-Step: First Time Mobile Setup

### Complete Beginner Path (30 minutes)

**Step 1: Install Termux (Android) or iSH (iOS)** (5 min)

**Step 2: Install Git and Python** (5 min)
```bash
# Termux:
pkg install git python

# iSH:
apk add git python3
```

**Step 3: Clone Repository** (2 min)
```bash
cd ~
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation
```

**Step 4: Quick Verification** (1 min)
```bash
python3 scripts/tools/verify_setup.py
# Shows what's missing - that's expected!
```

**Step 5: Read Documentation** (10 min)
```bash
cat SETUP.md | less
cat MOBILE_WORKFLOW.md | less
cat TROUBLESHOOTING.md | less
```

**Step 6: Decide Next Steps** (5 min)
- Want to process videos? → Go to cloud (Workflow 3)
- Want to understand code? → Browse files locally
- Want to contribute docs? → Make edits and commit

---

## When NOT to Use Mobile

❌ **Don't process on mobile if:**
- Video is longer than 30 seconds
- You need results quickly (< 10 minutes)
- You're on limited mobile data
- Battery is low
- Storage is limited

✅ **Do use cloud instead:**
- Google Colab (free, GPU available)
- GitHub Codespaces (free tier available)
- AWS/GCP free tier
- Local desktop/laptop if available

---

## Quick Reference: Mobile Commands

```bash
# Essential commands for mobile
cd Smart_Coach_Pose_Estimation          # Navigate to repo
source mediapipe_env/bin/activate       # Activate environment
python scripts/tools/verify_setup.py    # Check status
cat TROUBLESHOOTING.md | less           # Read docs
git status                               # Check git status
git add -A && git commit -m "msg"       # Quick commit
git push                                 # Push changes
df -h .                                  # Check disk space
du -sh mediapipe_env                    # Check venv size
```

---

## Mobile Workflow: Summary

**Best Practices:**
1. ✅ Use mobile for: Documentation, code review, small edits
2. ✅ Use cloud for: Pipeline execution, model downloads
3. ✅ Use mobile analysis for: CSV data, results visualization
4. ⚠️ Only process on mobile: Short test clips (<10 sec) on high-end devices
5. ❌ Don't attempt on mobile: Long videos, batch processing, real-time inference

**Optimal Setup:**
- Mobile device: Code editing, git operations, documentation
- Cloud service: Pipeline execution, heavy processing
- Result analysis: Can be done on mobile with pandas

**Time Investment:**
- Setup on mobile: 45-60 minutes (one time)
- Setup on cloud: 10-15 minutes (per session)
- Processing 10-sec video on mobile: 30-60 minutes
- Processing 30-sec video on cloud: 5-10 minutes

**Recommendation:** Use mobile for repository management and documentation, cloud for actual pipeline execution. This gives you the flexibility of mobile while maintaining practical processing times.

---

## Getting Started Right Now

**Immediate Next Steps:**
1. Install Termux (Android) or iSH (iOS)
2. Clone the repository
3. Read the documentation
4. Decide if you need cloud processing or can work locally
5. Follow the appropriate workflow above

**Questions?** See TROUBLESHOOTING.md for mobile-specific issues.
