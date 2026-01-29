#!/usr/bin/env python3
"""
Two-Pass Pipeline for Smart Coach Pose Estimation

Pass 1: Process all frames to collect raw detections
Pass 2: Post-process collected data to interpolate missing/inaccurate landmarks

This approach ensures:
- Complete temporal context for interpolation
- Better outlier detection using global statistics
- More accurate gap filling using bidirectional information
- Smoother trajectories through global optimization
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy import interpolate
from scipy.signal import savgol_filter
from scipy.stats import zscore

# Import the main pipeline (we'll run it to get raw data)
sys.path.insert(0, os.path.dirname(__file__))

def detect_outliers(data, threshold=3.0):
    """
    Detect outliers in a time series using z-score method.
    
    Args:
        data: 1D numpy array of values
        threshold: Z-score threshold for outlier detection
    
    Returns:
        Boolean array where True indicates an outlier
    """
    if len(data) < 4:
        return np.zeros(len(data), dtype=bool)
    
    # Calculate z-scores
    z_scores = np.abs(zscore(data, nan_policy='omit'))
    return z_scores > threshold

def interpolate_missing(times, values, method='cubic'):
    """
    Interpolate missing values in a time series.
    
    Args:
        times: Array of timestamps
        values: Array of values (with NaN for missing)
        method: Interpolation method ('linear', 'cubic', 'pchip')
    
    Returns:
        Interpolated values array
    """
    # Find valid (non-NaN) indices
    valid_mask = ~np.isnan(values)
    
    if np.sum(valid_mask) < 2:
        # Not enough valid points to interpolate
        return np.full_like(values, np.nan)
    
    # Interpolate
    try:
        if method == 'pchip':
            from scipy.interpolate import PchipInterpolator
            f = PchipInterpolator(times[valid_mask], values[valid_mask], extrapolate=False)
        else:
            f = interpolate.interp1d(
                times[valid_mask], 
                values[valid_mask],
                kind=method,
                bounds_error=False,
                fill_value=np.nan
            )
        interpolated = f(times)
        return interpolated
    except (ValueError, RuntimeError) as e:
        # Fallback to linear if method fails
        try:
            f = interpolate.interp1d(
                times[valid_mask],
                values[valid_mask],
                kind='linear',
                bounds_error=False,
                fill_value=np.nan
            )
            return f(times)
        except (ValueError, RuntimeError):
            return values

def smooth_trajectory(values, window_length=11, polyorder=3):
    """
    Smooth a trajectory using Savitzky-Golay filter.
    
    Args:
        values: 1D numpy array
        window_length: Length of filter window (must be odd)
        polyorder: Order of polynomial fit
    
    Returns:
        Smoothed values
    """
    # Handle NaN values
    valid_mask = ~np.isnan(values)
    if np.sum(valid_mask) < window_length:
        return values
    
    # Ensure window_length is odd and <= data length
    window_length = min(window_length, np.sum(valid_mask))
    if window_length % 2 == 0:
        window_length -= 1
    if window_length < polyorder + 2:
        return values
    
    try:
        smoothed = values.copy()
        smoothed[valid_mask] = savgol_filter(
            values[valid_mask],
            window_length=window_length,
            polyorder=polyorder
        )
        return smoothed
    except (ValueError, RuntimeError):
        return values

def post_process_dataframe(df, config=None):
    """
    Post-process raw detection data to improve quality.
    
    Args:
        df: pandas DataFrame with raw detections
        config: Dictionary with processing parameters
    
    Returns:
        Processed DataFrame
    """
    if config is None:
        config = {
            'outlier_threshold': 3.0,
            'interpolation_method': 'pchip',  # Preserves monotonicity
            'smooth_window': 11,
            'smooth_polyorder': 3,
            'min_confidence': 0.3
        }
    
    print("\n" + "=" * 60)
    print("PASS 2: POST-PROCESSING RAW DETECTIONS")
    print("=" * 60)
    
    df_processed = df.copy()
    times = df['timestamp'].values
    
    # Process pose keypoints (17 keypoints × 2 coordinates)
    print("\nProcessing pose keypoints...")
    for i in range(17):
        conf_col = f'kps_{i}_conf'
        
        # Skip if confidence column doesn't exist
        if conf_col not in df.columns:
            continue
        
        # Mark low confidence as NaN
        low_conf_mask = df[conf_col] < config['min_confidence']
        
        for coord in ['x', 'y']:
            col = f'kps_{i}_{coord}'
            if col not in df.columns:
                continue
            
            values = df[col].values.copy().astype(float)
            values[low_conf_mask] = np.nan
            
            # 1. Detect outliers
            outliers = detect_outliers(values[~np.isnan(values)], config['outlier_threshold'])
            if np.any(outliers):
                outlier_indices = np.where(~np.isnan(values))[0][outliers]
                values[outlier_indices] = np.nan
                print(f"  Keypoint {i} {coord}: Removed {len(outlier_indices)} outliers")
            
            # 2. Interpolate missing values
            if np.sum(~np.isnan(values)) >= 2:
                interpolated = interpolate_missing(times, values, config['interpolation_method'])
                values = np.where(np.isnan(values), interpolated, values)
            
            # 3. Smooth trajectory
            values = smooth_trajectory(values, config['smooth_window'], config['smooth_polyorder'])
            
            df_processed[col] = values
        
        # Recalculate velocities after smoothing
        for coord in ['x', 'y']:
            col = f'kps_{i}_{coord}'
            vel_col = f'kps_{i}_v{coord}'
            if col in df_processed.columns and vel_col in df_processed.columns:
                values = df_processed[col].values
                velocities = np.zeros_like(values)
                velocities[1:] = np.diff(values)
                df_processed[vel_col] = velocities
    
    # Process hand landmarks (if available)
    print("\nProcessing hand landmarks...")
    for side in ['L', 'R']:
        for i in range(21):
            has_data = False
            for coord in ['x', 'y']:
                col = f'{side}_hand_{i}_{coord}'
                if col not in df.columns:
                    continue
                
                values = df[col].values.copy().astype(float)
                
                # Mark zero values as NaN (hands not detected)
                values[values == 0.0] = np.nan
                
                if np.sum(~np.isnan(values)) >= 2:
                    has_data = True
                    
                    # Detect outliers
                    outliers = detect_outliers(values[~np.isnan(values)], config['outlier_threshold'])
                    if np.any(outliers):
                        outlier_indices = np.where(~np.isnan(values))[0][outliers]
                        values[outlier_indices] = np.nan
                    
                    # Interpolate
                    interpolated = interpolate_missing(times, values, config['interpolation_method'])
                    values = np.where(np.isnan(values), interpolated, values)
                    
                    # Smooth
                    values = smooth_trajectory(values, config['smooth_window'], config['smooth_polyorder'])
                    
                    df_processed[col] = values
                
        # Recalculate velocities after smoothing
        if has_data:
            for coord in ['x', 'y']:
                col = f'{side}_hand_{i}_{coord}'
                vel_col = f'{side}_hand_{i}_v{coord}'
                if col in df_processed.columns and vel_col in df_processed.columns:
                    values = df_processed[col].values
                    velocities = np.zeros_like(values)
                    velocities[1:] = np.diff(values)
                    df_processed[vel_col] = velocities
            
            if has_data:
                print(f"  {side} hand landmark {i}: Processed")
    
    # Process gaze direction (smooth but don't interpolate - keep as 0 when missing)
    print("\nProcessing gaze direction...")
    for coord in ['x', 'y']:
        col = f'gaze_dir_{coord}'
        if col in df.columns:
            values = df[col].values.copy().astype(float)
            
            # Only smooth non-zero values
            non_zero_mask = values != 0.0
            if np.sum(non_zero_mask) > config['smooth_window']:
                # Extract non-zero segments
                smoothed = values.copy()
                smoothed[non_zero_mask] = smooth_trajectory(
                    values[non_zero_mask], 
                    config['smooth_window'], 
                    config['smooth_polyorder']
                )
                df_processed[col] = smoothed
                print(f"  Gaze {coord}: Smoothed {np.sum(non_zero_mask)} frames")
    
    # Calculate confidence scores
    print("\nCalculating data quality metrics...")
    pose_confidence = df_processed[[f'kps_{i}_conf' for i in range(17) if f'kps_{i}_conf' in df_processed.columns]].mean(axis=1)
    df_processed['pose_quality'] = pose_confidence
    
    # Calculate completeness (percentage of non-zero/non-NaN values)
    total_cols = len([c for c in df_processed.columns if c.startswith('kps_') and '_x' in c])
    valid_cols = (df_processed[[f'kps_{i}_x' for i in range(17) if f'kps_{i}_x' in df_processed.columns]] != 0).sum(axis=1)
    df_processed['pose_completeness'] = valid_cols / max(total_cols, 1)
    
    print(f"\n✓ Post-processing complete")
    print(f"  Average pose quality: {pose_confidence.mean():.2f}")
    print(f"  Average completeness: {df_processed['pose_completeness'].mean():.2%}")
    
    return df_processed

def main():
    """
    Main two-pass pipeline execution.
    """
    print("=" * 60)
    print("TWO-PASS SMART COACH PIPELINE")
    print("=" * 60)
    print("\nThis pipeline processes video in two passes:")
    print("  Pass 1: Extract raw detections from all frames")
    print("  Pass 2: Post-process to improve accuracy and fill gaps")
    print()
    
    # Configuration
    CSV_PATH_RAW = "data/output/analytics_raw.csv"
    CSV_PATH_PROCESSED = "data/output/analytics_processed.csv"
    
    # Check if Pass 1 already completed
    if os.path.exists(CSV_PATH_RAW):
        print("Found existing raw detections from Pass 1")
        print("Use existing raw data? (y/n, default=y): ", end='', flush=True)
        use_existing = input().strip().lower()
        if use_existing == 'n':
            os.remove(CSV_PATH_RAW)
            run_pass1 = True
        else:
            run_pass1 = False  # Default to using existing
    else:
        run_pass1 = True
    
    # Pass 1: Run main pipeline to get raw detections
    if run_pass1:
        print("\n" + "=" * 60)
        print("PASS 1: EXTRACTING RAW DETECTIONS")
        print("=" * 60)
        print("\nRunning main pipeline...")
        
        # Run the pipeline as a subprocess to ensure it executes properly
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/processing/run_pipeline.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"\n✗ Pass 1 failed with error:")
            print(result.stderr)
            return 1
        
        # Check if analytics.csv was created
        if os.path.exists("data/output/analytics.csv"):
            os.rename("data/output/analytics.csv", CSV_PATH_RAW)
            print(f"\n✓ Pass 1 complete: Raw data saved to {CSV_PATH_RAW}")
        else:
            print("\n✗ Pass 1 failed: No output file generated")
            return 1
    
    # Pass 2: Post-process the raw detections
    print("\nLoading raw detections...")
    try:
        df_raw = pd.read_csv(CSV_PATH_RAW)
        print(f"✓ Loaded {len(df_raw)} frames")
    except Exception as e:
        print(f"✗ Failed to load raw data: {e}")
        return 1
    
    # Post-process
    df_processed = post_process_dataframe(df_raw)
    
    # Save processed data
    print(f"\nSaving processed data to {CSV_PATH_PROCESSED}...")
    df_processed.to_csv(CSV_PATH_PROCESSED, index=False)
    print(f"✓ Processed data saved")
    
    # Also save as the default analytics.csv
    df_processed.to_csv("data/output/analytics.csv", index=False)
    print(f"✓ Also saved as data/output/analytics.csv (default)")
    
    print("\n" + "=" * 60)
    print("TWO-PASS PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  Raw detections:    {CSV_PATH_RAW}")
    print(f"  Processed data:    {CSV_PATH_PROCESSED}")
    print(f"  Video overlay:     data/output/output_full.mp4")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
