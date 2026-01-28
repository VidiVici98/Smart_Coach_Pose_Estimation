# Using the Enhanced Metrics Collection

## Overview
The pipeline now collects 285 comprehensive metrics per frame, providing complete biomechanical and spatial data for defensive handgun shooter coaching.

## Running the Pipeline

```bash
# Activate the virtual environment
source mediapipe_env/bin/activate

# Run the pipeline on your video
python scripts/processing/run_pipeline.py

# The script reads from: data/input/test_video.mp4
# And outputs to:
#   - data/output/output_full.mp4 (annotated video)
#   - data/output/analytics.csv (metrics data)
```

## Validating Output

After running the pipeline, validate the CSV structure:

```bash
python scripts/tools/validate_metrics.py data/output/analytics.csv
```

Expected output:
```
✅ CSV validation passed!
   Total fields: 285
   Total rows: [number of frames]

📊 Field Categories:
   - Basic metrics: 5 fields
   - Pose keypoints: 85 fields (17 points × 5 metrics)
   - Hand landmarks: 170 fields (2 hands × 21 points × 4 metrics + 2 trigger)
   - Gaze metrics: 3 fields
   - Joint angles: 8 fields
   - Arm metrics: 2 fields
   - Grip metrics: 2 fields
   - Body position: 3 fields
   - Head orientation: 3 fields
   - Elevation metrics: 4 fields
   TOTAL: 285 fields
```

## Understanding the Output

### CSV Structure
Each row in `analytics.csv` represents one frame and contains:

1. **Basic Info** (5 fields)
   - `frame` - Frame number (0-indexed)
   - `timestamp` - Time in seconds (frame/fps)
   - `shoulder_width` - Normalization factor (pixels)
   - `hip_width` - Hip distance (pixels)
   - `stance_width` - Foot distance (pixels)

2. **Pose Keypoints** (85 fields: 17 × 5)
   - Format: `kps_{i}_x`, `kps_{i}_y`, `kps_{i}_vx`, `kps_{i}_vy`, `kps_{i}_conf`
   - Where i = 0-16 (nose, eyes, ears, shoulders, elbows, wrists, hips, knees, ankles)
   - Positions in pixels, velocities in pixels/frame, confidence 0.0-1.0

3. **Hand Landmarks** (170 fields: 2×21×4 + 2)
   - Format: `{L|R}_hand_{i}_x`, `{L|R}_hand_{i}_y`, `{L|R}_hand_{i}_vx`, `{L|R}_hand_{i}_vy`
   - Where i = 0-20 (wrist, thumb, index, middle, ring, pinky)
   - Plus: `L_trigger_pull`, `R_trigger_pull` (binary)

4. **Joint Angles** (8 fields in degrees)
   - `L_elbow_angle`, `R_elbow_angle` - Arm flexion
   - `L_shoulder_angle`, `R_shoulder_angle` - Shoulder position
   - `L_hip_angle`, `R_hip_angle` - Hip flexion
   - `L_knee_angle`, `R_knee_angle` - Knee flexion

5. **Specialized Metrics** (remaining fields)
   - Gaze direction and body intersection
   - Arm extension (normalized by shoulder_width)
   - Wrist/elbow elevation (normalized)
   - Hand distance and grip symmetry
   - Center of mass position (normalized)
   - Body lean angle (degrees from vertical)
   - Head orientation (pitch, yaw, roll in degrees)

### Working with the Data

#### Python Example
```python
import pandas as pd
import numpy as np

# Load the data
df = pd.read_csv('data/output/analytics.csv')

# Get right elbow angle over time
right_elbow = df['R_elbow_angle']

# Calculate arm extension consistency
left_arm_ext = df['L_arm_extension']
right_arm_ext = df['R_arm_extension']
extension_symmetry = np.abs(left_arm_ext - right_arm_ext)

# Find frames where both hands are detected
both_hands = df['grip_symmetry'] == 1.0

# Get center of mass trajectory
com_x = df['center_of_mass_x']
com_y = df['center_of_mass_y']

# Detect potential trigger pulls
trigger_frames = df[(df['L_trigger_pull'] == 1) | (df['R_trigger_pull'] == 1)]
```

#### Filtering by Confidence
```python
# Only use frames where key keypoints are high confidence
good_frames = (
    (df['kps_5_conf'] > 0.5) &  # Left shoulder
    (df['kps_6_conf'] > 0.5) &  # Right shoulder
    (df['kps_9_conf'] > 0.5) &  # Left wrist
    (df['kps_10_conf'] > 0.5)   # Right wrist
)

clean_data = df[good_frames]
```

## Keypoint Reference

YOLOv8 Pose keypoints (17 total):
- 0: nose
- 1-2: eyes (left, right)
- 3-4: ears (left, right)
- 5-6: shoulders (left, right)
- 7-8: elbows (left, right)
- 9-10: wrists (left, right)
- 11-12: hips (left, right)
- 13-14: knees (left, right)
- 15-16: ankles (left, right)

MediaPipe Hand landmarks (21 per hand):
- 0: wrist
- 1-4: thumb (CMC, MCP, IP, tip)
- 5-8: index finger (MCP, PIP, DIP, tip)
- 9-12: middle finger (MCP, PIP, DIP, tip)
- 13-16: ring finger (MCP, PIP, DIP, tip)
- 17-20: pinky (MCP, PIP, DIP, tip)

## Troubleshooting

### "CSV validation failed - missing fields"
The pipeline code may not have run correctly. Check that:
- All model files exist in `data/models/`
- Video input is accessible
- No errors during processing

### "Missing hand data (all zeros)"
Hand detection failed. This is normal if:
- Hands are occluded or out of frame
- Hands are too far from camera
- Lighting is poor

Use `grip_symmetry` field to filter frames where both hands were detected.

### "Joint angles are 0.0"
Required keypoints were not detected. Check confidence scores:
```python
# For elbow angle, need shoulder, elbow, wrist
left_elbow_valid = (
    (df['kps_5_conf'] > 0.3) &
    (df['kps_7_conf'] > 0.3) &
    (df['kps_9_conf'] > 0.3)
)
```

## Performance Notes

- Processing speed: ~2-5 FPS on CPU (depends on resolution)
- CSV file size: ~100 KB per 100 frames (285 fields × 100 rows)
- Memory usage: ~2 GB during processing

## Next Steps

1. **Analyze your data** - Use pandas/numpy for time-series analysis
2. **Visualize metrics** - Plot joint angles, COM trajectory, etc.
3. **Build coaching insights** - Define thresholds and patterns
4. **Train ML models** - Use comprehensive features for classification/regression

## Documentation

- [COMPREHENSIVE_METRICS_UPDATE.md](../docs/COMPREHENSIVE_METRICS_UPDATE.md) - Detailed metric descriptions
- [IMPLEMENTATION_SUMMARY.md](../docs/IMPLEMENTATION_SUMMARY.md) - Technical implementation details
- [metrics_reference.md](../docs/metrics_reference.md) - Original metrics specification

## Support

For issues or questions, refer to the documentation or create an issue in the repository.
