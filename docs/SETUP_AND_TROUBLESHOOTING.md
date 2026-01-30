# Setup and Troubleshooting Guide

Complete guide for setting up Smart Coach Pose Estimation and resolving common issues.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Detailed Setup](#detailed-setup)
3. [Mobile/Codespace Workflow](#mobilecodespace-workflow)
4. [Troubleshooting](#troubleshooting)
5. [Memory and Performance](#memory-and-performance)

---

## Quick Start

### Prerequisites
- Python 3.8+
- 8GB+ RAM recommended
- 2GB free disk space for models

### Installation (3 commands)

```bash
# 1. Clone repository
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run pipeline
python scripts/processing/run_pipeline.py
```

---

## Detailed Setup

### Local Setup (Desktop/Laptop)

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download Models** (automatic on first run)
   - YOLOv8 Pose (51MB)
   - YOLOv8 Face (6MB)
   - MediaPipe Face Landmarker (4MB)
   - Mask R-CNN (downloaded automatically)

3. **Prepare Input Video**
   - Place video in `data/input/`
   - Rename to `test_video.mp4` or update `VIDEO_PATH` in script

4. **Run Pipeline**
   ```bash
   python scripts/processing/run_pipeline.py
   ```

### GitHub Codespaces Setup

**Recommended for mobile users** - provides full Linux environment in browser.

1. **Create Codespace**
   - Go to repository on GitHub
   - Click "Code" → "Codespaces" → "Create codespace on main"

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Pipeline**
   ```bash
   python scripts/processing/run_pipeline.py
   ```

4. **Download Results**
   - Files in `data/output/` can be downloaded via VS Code interface

---

## Mobile/Codespace Workflow

### Option 1: GitHub Codespaces (Recommended)
✅ Full Python environment  
✅ GPU acceleration (on paid plans)  
✅ 60 hours/month free  
✅ Works on any device with browser

**Limitations:**
- Limited to 2-4 cores (free tier)
- Network-dependent
- Stops after inactivity

### Option 2: Google Colab
✅ Free GPU access  
✅ Good for experimentation  
✅ Jupyter notebook interface

**Setup:**
```python
!git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
%cd Smart_Coach_Pose_Estimation
!pip install -r requirements.txt
!python scripts/processing/run_pipeline.py
```

### Workflow Recommendations

**For Quick Tests (< 10 frames):**
- Use MAX_FRAMES limit in script
- Process locally if possible

**For Full Videos:**
- Use GitHub Codespaces (free tier)
- Upload video to `data/input/`
- Run pipeline
- Download results

---

## Troubleshooting

### Common Issues

#### 1. Import Error: `libGL.so.1 not found`

**Solution:** Use opencv-python-headless for headless environments
```bash
pip install opencv-python-headless
```

#### 2. CUDA/GPU Errors

**Solution:** Install CPU-only PyTorch
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

#### 3. Model Download Failures

**Solution:** Models download automatically on first run. If issues persist, check network connection.

#### 4. Out of Memory (OOM)

**Solution:** Enable LOW_MEMORY_MODE in script or set MAX_FRAMES limit:
```python
# In run_pipeline.py
MAX_FRAMES = 30  # Process only first 30 frames
LOW_MEMORY_MODE = True
```

#### 5. Video Codec Issues

**Solution:** Convert video with ffmpeg
```bash
ffmpeg -i input.mov -c:v libx264 -crf 23 output.mp4
```

#### 6. Slow Processing

**Solutions:**
- Reduce video resolution
- Set MAX_FRAMES for testing
- Use GPU if available

---

## Memory and Performance

### Memory Requirements

| Component | RAM Usage |
|-----------|-----------|
| YOLOv8 Pose | ~2GB |
| YOLOv8 Face | ~500MB |
| Mask R-CNN | ~1.5GB |
| MediaPipe | ~200MB |
| Frame Buffer | ~50MB/frame |
| **Total** | **~5-6GB minimum** |

### Performance Optimization

**1. Reduce Resolution**
```bash
ffmpeg -i input.mp4 -vf scale=960:540 input_small.mp4
```

**2. Limit Frames**
```python
# In run_pipeline.py
MAX_FRAMES = 30  # Process only first 30 frames
```

**3. Use Lighter Models**
```python
# Use YOLOv8n instead of YOLOv8m
POSE_MODEL_PATH = "data/models/yolov8n-pose.pt"  # Faster, less accurate
```

---

## System Requirements

### Minimum
- CPU: 4 cores
- RAM: 8GB
- Disk: 5GB free
- Python: 3.8+

### Recommended
- CPU: 8+ cores
- RAM: 16GB
- GPU: CUDA-capable (optional but faster)
- Disk: 10GB free
- Python: 3.10+

---

## Getting Help

**If you encounter issues:**

1. Check error message against this guide
2. Search GitHub issues
3. Open new issue with error details

**Diagnostic commands:**
```bash
# Check versions
python --version
pip list | grep -E "torch|opencv|mediapipe|ultralytics"

# Test imports
python -c "import cv2, torch, mediapipe, ultralytics; print('All imports OK')"
```

---

**Last Updated:** 2026-01-30  
**For advanced topics, see [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)**
