# Codespace Resource Configuration
# This file documents resource requirements and optimizations

## GitHub Codespaces Machine Types

### 2-core (8 GB RAM, 32 GB storage)
- **Status**: ✅ Supported
- **Features**: 
  - ✅ Pose detection
  - ✅ Hand detection
  - ✅ Face/gaze detection
  - ❌ Body segmentation (disabled via LOW_MEMORY_MODE)
- **Processing Speed**: ~10-20 seconds per frame
- **Cost**: Free tier available

### 4-core (16 GB RAM, 32 GB storage)
- **Status**: ✅ Recommended
- **Features**: 
  - ✅ All features enabled
  - ✅ Body segmentation (Mask R-CNN)
- **Processing Speed**: ~5-10 seconds per frame
- **Cost**: Paid tier

## Storage Optimization

### Model Files (~67 MB total)
- yolov8m-pose.pt: ~51 MB
- yolov8n-face.pt: ~6.3 MB
- face_landmarker.task: ~3.6 MB (lightweight)
- hand_landmarker.task: Not downloaded by default

### Large Files Excluded (via .gitignore)
- Video files (*.mp4, *.avi, *.mov)
- Model weights in data/models/
- Output files in data/output/
- Virtual environments (mediapipe_env/)

## Memory Optimization

### LOW_MEMORY_MODE (Enabled by default in codespace)
Disables Mask R-CNN to save ~2GB RAM:
- Memory savings: ~2-3 GB
- Feature impact: Body mask overlay unavailable
- All other features work normally

### To Enable All Features (4-core codespace)
Set environment variable before running:
```bash
export LOW_MEMORY_MODE=false
python scripts/processing/run_pipeline.py
```

The pipeline auto-detects codespace and enables LOW_MEMORY_MODE by default.
Override with the environment variable to use all features.

## Processing Optimization

### Video Length Recommendations
- **Test/Development**: 5-15 seconds
- **Short Clips**: 30-60 seconds
- **Full Analysis**: 1-2 minutes

Longer videos scale linearly in processing time.

## Network/Bandwidth Considerations

### Initial Setup
- Dependencies download: ~200-300 MB
- Model downloads: ~67 MB
- Total first-time: ~300-400 MB

### Ongoing Usage
- Minimal bandwidth after setup
- Video uploads depend on file size
- Output downloads (video + CSV)

## Disk Space Management

### After Setup
- ~500-600 MB used
- ~31.5 GB available (on 32 GB codespace)

### With Processed Videos
- Each 30-second video: ~50-100 MB output
- CSV files: ~1-5 MB per video
- Safe to process dozens of videos

### Cleanup Commands
```bash
# Remove output files
rm -rf data/output/*.mp4 data/output/*.csv

# Remove cache
rm -rf ~/.cache/torch
rm -rf ~/.cache/ultralytics
```

## Performance Tips

### 1. Use Shorter Test Videos
Process 10-15 second clips for testing/development

### 2. Skip Optional Features
Set LOW_MEMORY_MODE=True if memory is tight

### 3. Batch Processing
Process multiple short clips rather than one long video

### 4. Monitor Resources
```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check process resources
top
```

## Troubleshooting

### Out of Memory Error
- ✅ Enable LOW_MEMORY_MODE
- ✅ Process shorter videos
- ✅ Upgrade to 4-core codespace

### Disk Space Full
- ✅ Clean output directory
- ✅ Remove cache directories
- ✅ Delete large video files

### Slow Processing
- ✅ Expected on CPU-only
- ✅ Each frame = 5 models
- ✅ Consider shorter test clips

## Environment Variables

```bash
# Codespace detection
CODESPACES=true                    # Set by GitHub
SMART_COACH_CODESPACE=true         # Set by devcontainer

# Performance
LOW_MEMORY_MODE=true               # Auto-enabled in codespace
PYTORCH_NO_NNPACK=1                # Disable NNPACK
TORCH_CPP_LOG_LEVEL=ERROR          # Reduce logging

# Model selection
USE_LIGHTWEIGHT_MODELS=true        # Use smaller models
```

## Estimated Processing Times

### 2-core Codespace (LOW_MEMORY_MODE)
- 10-second video: ~2-3 minutes
- 30-second video: ~5-10 minutes
- 1-minute video: ~10-20 minutes

### 4-core Codespace (All features)
- 10-second video: ~1-2 minutes
- 30-second video: ~3-5 minutes
- 1-minute video: ~6-10 minutes

*Times vary based on video complexity and frame rate*
