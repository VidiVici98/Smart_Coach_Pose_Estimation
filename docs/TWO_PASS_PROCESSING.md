# Two-Pass Processing System

## Overview

The Smart Coach pipeline now supports a **two-pass processing system** for maximum data quality and robustness. This approach trades real-time performance for superior accuracy - ideal for training analysis.

## Architecture

### Pass 1: Raw Detection Collection
- Process every frame sequentially
- Extract all available detections without filtering
- Save raw confidence scores for all keypoints
- Output: `analytics_raw.csv` with unfiltered data

### Pass 2: Intelligent Post-Processing  
- Load complete temporal sequence from Pass 1
- Apply global algorithms with full context:
  - **Outlier Detection**: Z-score based anomaly removal
  - **Temporal Interpolation**: Fill missing frames using PCHIP/cubic splines
  - **Trajectory Smoothing**: Savitzky-Golay filter for noise reduction
  - **Quality Scoring**: Per-frame confidence and completeness metrics

## Why Two-Pass?

### Single-Pass Limitations
- **No future context**: Can't predict if a detection is an outlier
- **Gap filling**: Limited to simple forward smoothing
- **Global trends**: Can't detect systematic drift or bias
- **Incomplete data**: Must process and output immediately

### Two-Pass Advantages
- **Bidirectional interpolation**: Use past AND future frames
- **Global outlier detection**: Compare against entire sequence statistics
- **Optimal smoothing**: Apply filters that require full temporal window
- **Quality metrics**: Calculate frame-by-frame reliability scores

## Usage

### Quick Start
```bash
# Run the two-pass pipeline
python scripts/processing/run_pipeline_two_pass.py
```

### Manual Control
```bash
# Pass 1 only (if you want to inspect raw data first)
python scripts/processing/run_pipeline.py
cp data/output/analytics.csv data/output/analytics_raw.csv

# Pass 2 only (post-process existing raw data)
python -c "
from run_pipeline_two_pass import post_process_dataframe
import pandas as pd
df = pd.read_csv('data/output/analytics_raw.csv')
df_proc = post_process_dataframe(df)
df_proc.to_csv('data/output/analytics_processed.csv', index=False)
"
```

### Python API
```python
from scripts.processing.run_pipeline_two_pass import post_process_dataframe
import pandas as pd

# Load raw detections
df_raw = pd.read_csv('data/output/analytics_raw.csv')

# Configure post-processing
config = {
    'outlier_threshold': 3.0,        # Z-score threshold
    'interpolation_method': 'pchip',  # 'linear', 'cubic', 'pchip'
    'smooth_window': 11,              # Savitzky-Golay window (odd number)
    'smooth_polyorder': 3,            # Polynomial order for smoothing
    'min_confidence': 0.3             # Discard detections below this
}

# Post-process
df_processed = post_process_dataframe(df_raw, config)

# Save
df_processed.to_csv('data/output/analytics_processed.csv', index=False)
```

## Configuration Parameters

### `outlier_threshold` (default: 3.0)
- Z-score threshold for outlier detection
- Higher = more permissive (fewer outliers removed)
- Lower = more aggressive (more outliers removed)
- Recommended: 2.5 - 4.0

### `interpolation_method` (default: 'pchip')
- **'linear'**: Fast, simple, but can create sharp transitions
- **'cubic'**: Smooth, but may overshoot or oscillate
- **'pchip'**: Preserves monotonicity, best for human motion

### `smooth_window` (default: 11)
- Window size for Savitzky-Golay filter
- Must be odd number
- Larger = smoother but more lag
- Recommended: 7-15 frames at 30fps

### `smooth_polyorder` (default: 3)
- Polynomial order for Savitzky-Golay filter
- Higher = more flexible fit
- Must be less than `smooth_window`
- Recommended: 2-4

### `min_confidence` (default: 0.3)
- Minimum detection confidence to keep
- Range: 0.0 - 1.0
- Below this threshold → marked as missing → interpolated
- Recommended: 0.2 - 0.4

## Output Files

### `analytics_raw.csv`
- Direct output from Pass 1
- Unfiltered detections with all noise and gaps
- Useful for debugging detection issues
- Has confidence scores for all keypoints

### `analytics_processed.csv`
- Output from Pass 2
- Outliers removed, gaps filled, trajectories smoothed
- Additional quality columns:
  - `pose_quality`: Average confidence across all keypoints (0-1)
  - `pose_completeness`: Percentage of valid keypoints (0-1)

### `analytics.csv`
- Symlink or copy of `analytics_processed.csv`
- Default file for downstream analysis
- Always use this for coaching insights

## Quality Metrics

The processed CSV includes two new quality indicators per frame:

### `pose_quality`
- Average detection confidence across all 17 keypoints
- Range: 0.0 (no confidence) to 1.0 (perfect confidence)
- Frames below 0.4 may have unreliable detections

### `pose_completeness`
- Percentage of keypoints successfully detected
- Range: 0.0 (no keypoints) to 1.0 (all 17 keypoints)
- Frames below 0.7 have significant missing data

## Algorithm Details

### Outlier Detection (Z-Score Method)
```
For each keypoint trajectory:
  1. Calculate mean and std across all frames
  2. Compute z-score for each frame: z = (value - mean) / std
  3. Mark as outlier if |z| > threshold (default 3.0)
  4. Replace outliers with NaN for interpolation
```

### Interpolation (PCHIP)
- **PCHIP** = Piecewise Cubic Hermite Interpolating Polynomial
- Shape-preserving: No overshoot between data points
- Monotonicity-preserving: Good for trajectories
- Handles non-uniform time steps
- Extrapolation disabled (keeps NaN at edges)

### Smoothing (Savitzky-Golay)
- Fits local polynomial to sliding window
- Preserves peaks better than moving average
- Two-sided filter (requires full sequence)
- Applied only to valid (non-NaN) segments

## Example Workflow

### Training Analysis
```bash
# 1. Record training session
# Save video as: data/input/training_session_1.mp4

# 2. Run two-pass pipeline
python scripts/processing/run_pipeline_two_pass.py

# 3. Analyze results
python -c "
import pandas as pd
df = pd.read_csv('data/output/analytics_processed.csv')

# Filter high-quality frames
good_frames = df[
    (df['pose_quality'] > 0.5) &
    (df['pose_completeness'] > 0.8)
]

print(f'High quality frames: {len(good_frames)}/{len(df)} ({len(good_frames)/len(df):.1%})')

# Analyze specific metrics (example: elbow angles)
print(f'Average left elbow angle: {good_frames[\"L_elbow_angle\"].mean():.1f}°')
print(f'Average right elbow angle: {good_frames[\"R_elbow_angle\"].mean():.1f}°')
"
```

### Comparing Raw vs Processed
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load both
df_raw = pd.read_csv('data/output/analytics_raw.csv')
df_proc = pd.read_csv('data/output/analytics_processed.csv')

# Compare a specific keypoint
kp = 9  # Left wrist
plt.figure(figsize=(12, 6))
plt.plot(df_raw['timestamp'], df_raw[f'kps_{kp}_x'], 'b.', alpha=0.5, label='Raw')
plt.plot(df_proc['timestamp'], df_proc[f'kps_{kp}_x'], 'r-', label='Processed')
plt.xlabel('Time (s)')
plt.ylabel('X position (pixels)')
plt.title(f'Keypoint {kp} X-coordinate: Raw vs Processed')
plt.legend()
plt.savefig('data/output/comparison.png')
print("Saved comparison plot to data/output/comparison.png")
```

## Performance Considerations

- **Processing time**: ~2-3x slower than single-pass
- **Memory usage**: Loads entire CSV into RAM (typically <10MB per 1000 frames)
- **Recommended for**:
  - Offline analysis (not real-time)
  - Training session review
  - High-accuracy coaching feedback
  - Research and development

- **Not recommended for**:
  - Live feedback during training
  - Real-time applications
  - Low-memory systems (<4GB RAM)

## Troubleshooting

### "Not enough valid points to interpolate"
- Detection quality too low
- Try lowering `min_confidence` threshold
- Check video quality/lighting

### "Processed data looks worse than raw"
- Smoothing window too large → reduce `smooth_window`
- Outlier threshold too aggressive → increase `outlier_threshold`
- Interpolation method not suitable → try 'linear' instead

### "Output still has gaps/NaN values"
- Not enough surrounding valid frames for interpolation
- Check `pose_completeness` in those frames
- May need manual annotation for these segments

## Future Enhancements

Planned improvements:
- [ ] Multi-pass outlier detection (iterative refinement)
- [ ] Kalman filter integration for prediction
- [ ] Biomechanical constraint enforcement
- [ ] Cross-frame feature matching for occlusion recovery
- [ ] Per-keypoint adaptive smoothing parameters
- [ ] GPU acceleration for large datasets

## References

- **Savitzky-Golay Filter**: A. Savitzky and M. J. E. Golay, Analytical Chemistry 36 (1964)
- **PCHIP Interpolation**: F. N. Fritsch and R. E. Carlson, SIAM J. Numer. Anal. 17 (1980)
- **Z-Score Outlier Detection**: Standard statistical method

## Contributing

To improve the two-pass system:
1. Test with diverse videos (different sports, lighting, angles)
2. Report issues with specific parameter configurations
3. Suggest new post-processing algorithms
4. Contribute test cases and validation data
