# Model Persistence in Codespace/Dev Environments

## Overview

Model files are **NOT tracked by git** due to their large size (67MB total), but they **MUST persist** in your development environment to run the pipeline. This document explains how to ensure models aren't deleted between sessions.

## Why Models Aren't in Git

Model files are excluded via `.gitignore`:
- `data/models/*.pt` - PyTorch model files
- `data/models/*.task` - MediaPipe model files

This prevents:
- Large files bloating the repository
- Slow git operations
- Exceeding GitHub's file size limits

## How Models Persist

### In GitHub Codespaces

Codespaces preserve the entire workspace filesystem, including:
- `data/models/` directory and all model files
- `data/input/` test videos
- `mediapipe_env/` virtual environment

**Models persist automatically** as long as:
1. You don't delete the codespace
2. You don't run `git clean -fdx` (which removes ignored files)
3. The codespace doesn't get garbage collected (happens after 30 days of inactivity)

### In Local Development

Models persist in your local clone indefinitely since they're just regular files that happen to be git-ignored.

## Initial Model Setup

### Automatic Download (Recommended)

```bash
# Activate virtual environment
source mediapipe_env/bin/activate

# Run download script
python scripts/tools/download_models.py
```

This downloads:
- `yolov8m-pose.pt` (51 MB) - Body pose detection
- `yolov8n-face.pt` (6.3 MB) - Face detection  
- `face_landmarker.task` (3.6 MB) - Face landmarks for gaze
- `hand_landmarker.task` (3.6 MB) - Hand landmarks **Note: May fail due to CDN restrictions**

### Manual Hand Model Setup

If automatic download fails for `hand_landmarker.task`:

1. **Download from MediaPipe** (if accessible):
   ```bash
   cd data/models
   curl -L -o hand_landmarker.task \
     "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
   ```

2. **Alternative: Add via GitHub Web Interface**:
   - Go to GitHub repository in browser
   - Navigate to `data/models/`
   - Click "Add file" → "Upload files"
   - Upload your local copy of `hand_landmarker.task`
   - This makes it available in all codespaces

3. **From another source**:
   - Download from a mirror or backup source
   - Place in `data/models/hand_landmarker.task`

## Verifying Models

Run the verification script:

```bash
bash scripts/setup/verify_models.sh
```

Expected output:
```
✓ YOLOv8 Pose: 51MB (valid)
✓ YOLOv8 Face: 7MB (valid)
✓ Face Landmarker: 4MB (valid)
✓ Hand Landmarker: 4MB (valid)
```

## Common Issues

### "Models deleted after PR merge"

Models are **never deleted by git** - they're ignored. If they disappear:
- Check if you ran `git clean -fdx` (removes ignored files)
- Check if codespace was recreated
- Check if someone manually deleted them

**Solution**: Re-run download script or verify_models.sh

### "Models missing in fresh codespace"

**This should NOT happen** - codespaces clone the repo but don't have models initially.

**Solution**: Run setup script on first use:
```bash
bash scripts/setup/verify_models.sh || python scripts/tools/download_models.py
```

### "Hand model fails to download"

Google CDN may block downloads. Options:
1. Download on local machine and upload via GitHub web interface
2. Use alternative CDN/mirror
3. Get from team member who has it

## Best Practices

1. **Never commit model files to git** - they're too large
2. **Run verify_models.sh** before running pipeline
3. **Keep models in data/models/** - scripts expect them there
4. **Document successful download methods** if you find alternatives
5. **Share models with team** via cloud storage if CDN is blocked

## Developer Workflow

### First time setup:
```bash
# Clone repo
git clone <repo-url>
cd Smart_Coach_Pose_Estimation

# Setup environment
source mediapipe_env/bin/activate
pip install -r requirements.txt

# Download models (only needed once)
python scripts/tools/download_models.py

# Or manually add hand_landmarker.task if download fails

# Verify
bash scripts/setup/verify_models.sh
```

### Daily workflow:
```bash
# Models persist - just activate and run
source mediapipe_env/bin/activate
python scripts/processing/run_pipeline.py
```

### After pulling changes:
```bash
# Models unchanged - no need to re-download
git pull
python scripts/processing/run_pipeline.py
```

## File Sizes Reference

| Model | Size | Purpose |
|-------|------|---------|
| yolov8m-pose.pt | 51 MB | Full body pose (17 keypoints) |
| yolov8n-face.pt | 6.3 MB | Face bounding boxes |
| face_landmarker.task | 3.6 MB | Face mesh for gaze tracking |
| hand_landmarker.task | 3.6 MB | Hand landmarks (21 per hand) |
| **Total** | **~65 MB** | Complete pipeline |

## Troubleshooting

If models keep disappearing:
1. Check `.gitignore` - should exclude `data/models/*.pt` and `data/models/*.task`
2. Check if someone is running `git clean -fdx`
3. Check codespace settings - ensure persistence is enabled
4. Document the issue and share with team

For additional help, see:
- `HAND_MODEL_SETUP.md` - Hand model specific instructions
- `data/models/README.md` - Model download instructions
- `scripts/tools/download_models.py` - Automatic download script
