# Codespace Memory Optimization Guide

## Problem: Exit Code 143 (SIGTERM / OOM)

Exit code 143 indicates the process was terminated, usually by the OOM (Out Of Memory) killer when your codespace runs out of RAM.

---

## SOLUTION 1: Use Low Memory Mode (RECOMMENDED)

**Already implemented!** The pipeline now has `LOW_MEMORY_MODE = True` by default.

Edit `/workspaces/Smart_Coach_Pose_Estimation/scripts/processing/run_pipeline.py` line ~148:

```python
# Set to True to disable memory-intensive features
LOW_MEMORY_MODE = True  # Disables Mask R-CNN (~2GB RAM saved)
```

**What this disables:**
- Mask R-CNN body segmentation (saves ~2GB RAM)
- Body mask overlay visualization

**What still works:**
- ✓ Full pose skeleton (17 keypoints)
- ✓ Hand landmarks (21 points each hand)
- ✓ Gaze detection (when face model available)
- ✓ All CSV metrics

**Run now:**
```bash
python3 scripts/processing/run_pipeline.py
```

---

## SOLUTION 2: Increase Codespace Machine Type

GitHub Codespaces come in different sizes:

### Current (likely 2-core / 8GB RAM):
```bash
# Check current resources
free -h
nproc
```

### Upgrade Options:

1. **Via GitHub Web UI:**
   - Go to your repository on GitHub
   - Click the green "Code" button
   - Find your active codespace
   - Click "..." (three dots) → "Change machine type"
   - Select 4-core (16 GB RAM) or 8-core (32 GB RAM)
   - Restart codespace

2. **Via Codespace Settings:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Codespaces: Change Machine Type"
   - Select larger machine
   - Rebuild codespace

3. **Via `.devcontainer/devcontainer.json`:**
   ```json
   {
     "hostRequirements": {
       "cpus": 4,
       "memory": "16gb",
       "storage": "32gb"
     }
   }
   ```
   Then rebuild: Ctrl+Shift+P → "Codespaces: Rebuild Container"

**Cost Note:** Larger machines cost more core-hours but may be necessary for ML workloads.

---

## SOLUTION 3: Use Smaller Models

Edit run_pipeline.py to use lighter YOLO models:

```python
# Line ~63 - Change from yolov8m-pose to yolov8n-pose
POSE_MODEL_PATH = "data/models/yolov8n-pose.pt"  # nano (~6MB vs 50MB)
```

Download nano model:
```bash
python3 << EOF
from ultralytics import YOLO
model = YOLO('yolov8n-pose.pt')
model.export(format='pt')
EOF
mv yolov8n-pose.pt data/models/
```

---

## SOLUTION 4: Process in Batches

For very long videos, process in segments:

```bash
# Install ffmpeg if not available
sudo apt-get install ffmpeg

# Split video into 30-second chunks
ffmpeg -i data/input/test_video.mp4 -c copy -map 0 -segment_time 30 \
  -f segment data/input/chunk_%03d.mp4

# Process each chunk
for chunk in data/input/chunk_*.mp4; do
  # Update VIDEO_PATH in run_pipeline.py to point to $chunk
  python3 scripts/processing/run_pipeline.py
done

# Merge results afterward
```

---

## SOLUTION 5: Check Current Memory Usage

**Before running pipeline:**
```bash
free -h
```

**During pipeline execution (in another terminal):**
```bash
watch -n 1 "ps aux --sort=-%mem | head -10"
```

**Check OOM killer logs:**
```bash
dmesg | grep -i "killed process"
dmesg | grep -i "out of memory"
```

---

## SOLUTION 6: Run Locally Instead

If codespace limitations persist, run on your local machine:

```bash
# Clone repo
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation

# Create virtual environment
python3 -m venv mediapipe_env
source mediapipe_env/bin/activate  # Windows: mediapipe_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run pipeline
python3 scripts/processing/run_pipeline.py
```

Local machines typically have more RAM available than free codespaces.

---

## Quick Status Check

Run this to see what's consuming memory:

```bash
python3 << 'EOF'
import torch
import sys

print("Python executable:", sys.executable)
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print(f"CUDA memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    print(f"CUDA memory reserved: {torch.cuda.memory_reserved() / 1e9:.2f} GB")

# Check system memory
import subprocess
result = subprocess.run(['free', '-h'], capture_output=True, text=True)
print("\nSystem Memory:")
print(result.stdout)
EOF
```

---

## Recommended Configuration for Codespaces

**Best balance of features vs memory:**

```python
# In run_pipeline.py
LOW_MEMORY_MODE = True         # Disable Mask R-CNN
POSE_MODEL_PATH = "yolov8s-pose.pt"  # Use 'small' instead of 'medium'
```

This should work on 2-core (8GB) codespaces while keeping most features functional.

---

## Contact / Issues

If none of these solutions work:
1. Check codespace free tier limits on your account
2. Verify video file isn't corrupted: `ffprobe data/input/test_video.mp4`
3. Try with a shorter/smaller test video first
