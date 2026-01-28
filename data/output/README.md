# Output Files

This directory contains the processed output from the Smart Coach pipeline.

## What Gets Generated

When you run `python scripts/processing/run_pipeline.py`, two files are created here:

### 1. output_full.mp4
- **Type:** Annotated video
- **Content:** Original video with overlays showing:
  - Body skeleton (17 keypoints)
  - Hand landmarks (21 points per hand)
  - Body segmentation mask (semi-transparent)
  - Gaze direction cone
  - Frame and timestamp information

### 2. analytics.csv
- **Type:** Metrics data
- **Content:** Frame-by-frame measurements (285 fields per frame)
- **Size:** ~1 MB per 1000 frames
- **Format:** CSV (comma-separated values)

## Using the Output

### View the Annotated Video
```bash
# Linux
vlc data/output/output_full.mp4
xdg-open data/output/output_full.mp4

# macOS
open data/output/output_full.mp4

# Windows
start data/output/output_full.mp4
```

### Analyze the Metrics Data
```python
import pandas as pd

# Load the data
df = pd.read_csv('data/output/analytics.csv')

# View basic info
print(df.shape)  # (num_frames, 285)
print(df.columns)  # All field names

# Example: Get right elbow angle over time
right_elbow = df['R_elbow_angle']

# Example: Find frames with both hands detected
both_hands = df['grip_symmetry'] == 1.0
```

See [docs/USAGE_GUIDE.md](../../docs/USAGE_GUIDE.md) for detailed information on:
- Understanding all 285 metrics
- Working with the CSV data
- Filtering by confidence
- Analyzing pose and motion

### Validate the Output
```bash
# Check CSV structure
python scripts/tools/validate_metrics.py data/output/analytics.csv
```

## Output Files Are Gitignored

The `.gitignore` file excludes these output files because:
- They can be large (videos especially)
- They're generated/reproducible
- Each user will have different videos

**Important:** Back up your output files separately if you need to keep them!

## Typical File Sizes

For a 30-second video at 30 fps (900 frames):
- **output_full.mp4:** 5-20 MB (depends on resolution and compression)
- **analytics.csv:** ~1 MB (285 fields × 900 rows)

## Multiple Processing Runs

**Warning:** Each pipeline run overwrites previous files in this directory!

To keep multiple outputs:
```bash
# Rename outputs after each run
mv data/output/output_full.mp4 data/output/video1_output.mp4
mv data/output/analytics.csv data/output/video1_analytics.csv

# Or create subdirectories
mkdir -p data/output/run1
mv data/output/*.{mp4,csv} data/output/run1/
```

## Troubleshooting

### No Output Files Generated
If the pipeline completes but no files appear:
1. Check for error messages in console
2. Verify input video exists and is valid
3. Check disk space
4. Ensure you have write permissions

### Output Video is Black/Empty
If `output_full.mp4` plays but shows no overlays:
1. Detection may have failed (no person detected)
2. Check confidence thresholds in pipeline config
3. Try with a clearer video

### CSV is Empty or Missing Data
If `analytics.csv` exists but has zeros/nulls:
1. Check detection confidence (view output video)
2. Lower `CONF_THRES` in pipeline script
3. Ensure person is clearly visible in input video

### File Permissions Error
```bash
# Fix permissions
chmod -R u+w data/output/
```

## What's Next?

After generating output:
1. **View** the annotated video to verify detection quality
2. **Validate** the CSV structure
3. **Analyze** the metrics data in Python/Jupyter
4. **Iterate** on different videos or settings

For detailed guidance, see:
- [USAGE_GUIDE.md](../../docs/USAGE_GUIDE.md) - How to use the output
- [COMPREHENSIVE_METRICS_UPDATE.md](../../docs/COMPREHENSIVE_METRICS_UPDATE.md) - Metric descriptions
- [TROUBLESHOOTING.md](../../TROUBLESHOOTING.md) - Common issues
