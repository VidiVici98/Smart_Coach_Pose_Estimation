#!/usr/bin/env python3
"""
Extract screenshots from the pipeline output video at specific frames.
This script reads the output video and saves frames at SAMPLE_FRAMES positions.
"""

import cv2
import os
import sys

# Configuration - must match pipeline script
VIDEO_PATH = "data/output/output_full.mp4"
OUTPUT_DIR = "screenshots"
SAMPLE_FRAMES = [10, 30, 60, 75, 100, 120, 140]

def extract_screenshots():
    """Extract screenshots from the output video at specified frames."""
    
    print("=" * 60)
    print("Screenshot Extraction Tool")
    print("=" * 60)
    
    # Create output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✓ Created output directory: {OUTPUT_DIR}")
    
    # Open video
    if not os.path.exists(VIDEO_PATH):
        print(f"✗ Error: Video file not found: {VIDEO_PATH}")
        sys.exit(1)
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"✗ Error: Could not open video: {VIDEO_PATH}")
        sys.exit(1)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"✓ Video opened successfully:")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Total frames: {total_frames}")
    print()
    
    print(f"Extracting screenshots at frames: {SAMPLE_FRAMES}")
    print()
    
    # Extract screenshots
    extracted_count = 0
    for frame_num in SAMPLE_FRAMES:
        if frame_num >= total_frames:
            print(f"⚠ Warning: Frame {frame_num} exceeds total frames ({total_frames}), skipping")
            continue
        
        # Seek to the specific frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        
        if not ret:
            print(f"✗ Error: Could not read frame {frame_num}")
            continue
        
        # Save screenshot
        output_path = os.path.join(OUTPUT_DIR, f"frame_{frame_num:04d}.png")
        cv2.imwrite(output_path, frame)
        
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✓ Saved frame {frame_num:4d} → {output_path} ({file_size_mb:.2f} MB)")
        extracted_count += 1
    
    cap.release()
    
    print()
    print("=" * 60)
    print(f"✓ Extraction complete: {extracted_count}/{len(SAMPLE_FRAMES)} screenshots saved")
    print(f"✓ Output directory: {OUTPUT_DIR}/")
    print("=" * 60)

if __name__ == "__main__":
    extract_screenshots()
