# Input Videos

This directory should contain the video files you want to process with the Smart Coach pipeline.

## Quick Start

### Option 1: Use Your Own Video
Copy your training video here and rename it to `test_video.mp4`:
```bash
cp /path/to/your/video.mp4 data/input/test_video.mp4
```

### Option 2: Generate a Test Video
If you don't have a video yet, you can create a simple test pattern:
```bash
# Make sure you're in the repo root and virtual environment is activated
source mediapipe_env/bin/activate
python scripts/tools/create_test_video.py
```

This will create a 10-second video with a simple animated stick figure for testing the pipeline.

### Option 3: Download a Sample Video
You can download any public domain video with a person in it:
```bash
# Example using youtube-dl (if installed)
# youtube-dl -f mp4 -o data/input/test_video.mp4 [VIDEO_URL]
```

## Video Requirements

For best results with the Smart Coach pipeline:

- **Format**: MP4, AVI, MOV, or WEBM
- **Resolution**: 720p (1280x720) or higher recommended
- **Frame Rate**: 30 fps or higher
- **Content**: Clear view of full body (head to feet)
- **Lighting**: Well-lit environment
- **Duration**: Any length (shorter videos process faster for testing)

## What the Pipeline Expects

The main pipeline script (`scripts/processing/run_pipeline.py`) by default looks for:
```
data/input/test_video.mp4
```

If you want to process a different file, you can either:
1. Rename your file to `test_video.mp4`, or
2. Edit the `VIDEO_PATH` variable in `scripts/processing/run_pipeline.py`

## Processing Multiple Videos

To process multiple videos, you can:

1. Process them one at a time by renaming each to `test_video.mp4`
2. Modify the pipeline script to accept command-line arguments
3. Create a batch processing script (see `scripts/tools/` for examples)

## After Processing

Processed outputs will be saved to:
- `data/output/output_full.mp4` - Annotated video with pose overlays
- `data/output/analytics.csv` - Frame-by-frame metrics data

See [USAGE_GUIDE.md](../../docs/USAGE_GUIDE.md) for details on interpreting the output.
