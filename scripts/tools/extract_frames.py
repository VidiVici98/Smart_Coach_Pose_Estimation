#!/usr/bin/env python3
"""
Extract specific frames from the output video as PNG images for validation.
"""
import cv2
import sys
import os

def extract_frames(video_path, frame_indices, output_dir):
    """Extract specific frames from video and save as PNG images."""
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return False
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video has {total_frames} total frames")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract each requested frame
    for frame_idx in frame_indices:
        # Set position to specific frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if ret:
            output_path = os.path.join(output_dir, f"frame_{frame_idx:03d}.png")
            cv2.imwrite(output_path, frame)
            print(f"✓ Extracted frame {frame_idx} -> {output_path}")
        else:
            print(f"✗ Could not read frame {frame_idx}")
    
    cap.release()
    return True

if __name__ == "__main__":
    video_path = "data/output/output_full.mp4"
    frame_indices = [5, 15, 25, 35, 45]
    output_dir = "data/output/screenshots"
    
    print("=" * 60)
    print("Frame Extraction Tool")
    print("=" * 60)
    print(f"Video: {video_path}")
    print(f"Frames to extract: {frame_indices}")
    print(f"Output directory: {output_dir}")
    print()
    
    if not os.path.exists(video_path):
        print(f"Error: Video not found at {video_path}")
        print("Run the pipeline first: python scripts/processing/run_pipeline.py")
        sys.exit(1)
    
    success = extract_frames(video_path, frame_indices, output_dir)
    
    if success:
        print()
        print("=" * 60)
        print("✓ Frame extraction complete!")
        print(f"Screenshots saved to: {output_dir}")
        print("=" * 60)
    else:
        print("✗ Frame extraction failed")
        sys.exit(1)
