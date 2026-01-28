#!/usr/bin/env python3
"""
Create a simple test video for Smart Coach pipeline testing.
This generates a video with basic motion patterns that can be used
to validate the pipeline when you don't have real training footage.
"""

import sys
import os
from pathlib import Path

def create_test_video():
    """Create a simple test video with basic motion."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("Error: OpenCV not installed")
        print("Install with: pip install opencv-python")
        return False
    
    # Video parameters
    width = 1280
    height = 720
    fps = 30
    duration = 10  # seconds
    output_path = "data/input/test_video.mp4"
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print(f"Error: Could not create video file at {output_path}")
        return False
    
    print(f"Creating test video: {output_path}")
    print(f"Resolution: {width}x{height}, FPS: {fps}, Duration: {duration}s")
    
    total_frames = fps * duration
    
    # Generate frames
    for frame_num in range(total_frames):
        # Create a frame with gradient background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add gradient background
        for y in range(height):
            color_value = int(50 + (y / height) * 50)
            frame[y, :] = [color_value, color_value, color_value]
        
        # Calculate animation parameters
        t = frame_num / fps  # time in seconds
        progress = frame_num / total_frames
        
        # Draw a moving "person" (simplified stick figure)
        center_x = int(width / 2 + 100 * np.sin(2 * np.pi * t / 3))
        center_y = int(height / 2)
        
        # Head
        cv2.circle(frame, (center_x, center_y - 100), 30, (200, 200, 255), -1)
        cv2.circle(frame, (center_x, center_y - 100), 30, (255, 255, 255), 2)
        
        # Body
        cv2.line(frame, (center_x, center_y - 70), (center_x, center_y + 50), (255, 255, 255), 5)
        
        # Arms - with motion
        arm_angle = 20 * np.sin(2 * np.pi * t / 2)
        left_arm_x = int(center_x - 60 * np.cos(np.radians(45 + arm_angle)))
        left_arm_y = int(center_y - 20 + 60 * np.sin(np.radians(45 + arm_angle)))
        right_arm_x = int(center_x + 60 * np.cos(np.radians(45 - arm_angle)))
        right_arm_y = int(center_y - 20 + 60 * np.sin(np.radians(45 - arm_angle)))
        
        cv2.line(frame, (center_x, center_y - 20), (left_arm_x, left_arm_y), (255, 255, 255), 5)
        cv2.line(frame, (center_x, center_y - 20), (right_arm_x, right_arm_y), (255, 255, 255), 5)
        
        # Hands
        cv2.circle(frame, (left_arm_x, left_arm_y), 15, (150, 200, 255), -1)
        cv2.circle(frame, (right_arm_x, right_arm_y), 15, (150, 200, 255), -1)
        
        # Legs
        leg_angle = 15 * np.sin(2 * np.pi * t / 2 + np.pi)
        left_leg_x = int(center_x - 30 * np.sin(np.radians(leg_angle)))
        left_leg_y = int(center_y + 50 + 80 * np.cos(np.radians(leg_angle)))
        right_leg_x = int(center_x + 30 * np.sin(np.radians(leg_angle)))
        right_leg_y = int(center_y + 50 + 80 * np.cos(np.radians(leg_angle)))
        
        cv2.line(frame, (center_x, center_y + 50), (left_leg_x, left_leg_y), (255, 255, 255), 5)
        cv2.line(frame, (center_x, center_y + 50), (right_leg_x, right_leg_y), (255, 255, 255), 5)
        
        # Add frame info text
        cv2.putText(frame, f"Test Video - Frame {frame_num}/{total_frames}", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {t:.2f}s / {duration}s", 
                   (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        
        # Add instructions
        cv2.putText(frame, "Simple test pattern for pose detection", 
                   (20, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 1)
        cv2.putText(frame, "Replace with actual training video for real analysis", 
                   (20, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 1)
        
        # Write frame
        out.write(frame)
        
        # Progress indicator
        if frame_num % fps == 0:
            print(f"  Progress: {progress*100:.0f}% ({frame_num}/{total_frames} frames)")
    
    # Release video writer
    out.release()
    
    # Verify the file was created
    if Path(output_path).exists():
        size_mb = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"\n✓ Test video created successfully!")
        print(f"  Location: {output_path}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Duration: {duration} seconds")
        print(f"  Resolution: {width}x{height}")
        print(f"\nYou can now run the pipeline:")
        print(f"  python scripts/processing/run_pipeline.py")
        return True
    else:
        print(f"\n✗ Error: Video file was not created")
        return False

def main():
    """Main entry point."""
    print("=" * 60)
    print("Smart Coach Test Video Generator")
    print("=" * 60)
    print()
    print("This script creates a simple test video for pipeline validation.")
    print("For real analysis, use actual training footage.")
    print()
    
    # Change to repo root if script is run from scripts/tools/
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    os.chdir(repo_root)
    print(f"Working directory: {repo_root}\n")
    
    # Check if test video already exists
    if Path("data/input/test_video.mp4").exists():
        print("Warning: test_video.mp4 already exists!")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Aborted. Keeping existing video.")
            return 0
        print()
    
    # Create the test video
    success = create_test_video()
    
    print()
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
