# Devcontainer Configuration

This directory contains the configuration for running Smart Coach Pose Estimation in a GitHub Codespace or VS Code devcontainer.

## What's Included

- **devcontainer.json**: Main configuration for the development container
- **setup.sh**: Automated setup script that runs when the codespace is created

## Features

### Automatic Setup
When you open this repository in a codespace:
1. Python 3.11 environment is configured
2. All dependencies are installed automatically
3. Model files are downloaded (lightweight versions for faster setup)
4. Directory structure is created
5. Environment variables are set for optimal performance

### Optimizations for Codespace
- **LOW_MEMORY_MODE**: Enabled by default (disables Mask R-CNN to save ~2GB RAM)
- **Lightweight Models**: Uses float16 versions of MediaPipe models (~3.6MB vs 26MB)
- **OpenCV Headless**: Uses opencv-python-headless to avoid display dependencies
- **Warning Suppression**: Configures environment to suppress non-critical warnings

### Environment Variables
The following environment variables are automatically set:
- `SMART_COACH_CODESPACE=true`: Indicates running in codespace
- `PYTORCH_NO_NNPACK=1`: Disables NNPACK (not supported in codespace)
- `TORCH_CPP_LOG_LEVEL=ERROR`: Reduces PyTorch log verbosity
- `PYTHONUNBUFFERED=1`: Ensures immediate output visibility

## Resource Requirements

### Minimum (2-core, 8GB RAM)
✅ Works with LOW_MEMORY_MODE=True
- Pose detection: ✅
- Hand detection: ✅
- Face/gaze detection: ✅
- Body segmentation: ❌ (disabled to save memory)
- Processing speed: ~10-20 seconds per frame

### Recommended (4-core, 16GB RAM)
✅ All features enabled
- Pose detection: ✅
- Hand detection: ✅
- Face/gaze detection: ✅
- Body segmentation: ✅
- Processing speed: ~5-10 seconds per frame

## Usage

### First Time Setup
The setup script runs automatically when you open the codespace. If you need to run it manually:

```bash
bash .devcontainer/setup.sh
```

### Verify Setup
```bash
python scripts/tools/verify_setup.py
```

### Run the Pipeline
```bash
python scripts/processing/run_pipeline.py
```

## Customization

### Enable Full Features
If you have a 4-core/16GB codespace and want to enable body segmentation:

1. Edit `scripts/processing/run_pipeline.py`
2. Change `LOW_MEMORY_MODE = True` to `LOW_MEMORY_MODE = False`
3. Re-run the pipeline

### Use Full Precision Models
If you want higher accuracy and have bandwidth/storage:

```bash
# Set environment variable before downloading
export USE_LIGHTWEIGHT_MODELS=false
python scripts/tools/download_models.py
```

## Troubleshooting

### Out of Memory
If you get memory errors:
- Ensure `LOW_MEMORY_MODE = True` in run_pipeline.py
- Consider using a smaller/shorter test video
- Upgrade to 4-core/16GB codespace

### Slow Processing
This is normal for CPU-only processing:
- Each frame requires inference from 5 models
- 30-second video may take 5-10 minutes
- Consider processing shorter clips for testing

### Model Download Fails
```bash
# Manually download models
python scripts/tools/download_models.py

# Or check network and retry
python scripts/tools/verify_setup.py
```

## Files

### devcontainer.json
Defines the container configuration:
- Base image (Python 3.11)
- VS Code extensions
- Environment variables
- Startup commands

### setup.sh
Automated setup script:
- Installs Python dependencies
- Downloads model files
- Creates directory structure
- Verifies installation
- Displays next steps

## More Information

- [START_HERE_CODESPACE.md](../docs/guides/START_HERE_CODESPACE.md) - Quick start guide
- [CODESPACE_RECOVERY.md](../docs/guides/CODESPACE_RECOVERY.md) - Recovery instructions
- [README.md](../README.md) - Main project documentation
