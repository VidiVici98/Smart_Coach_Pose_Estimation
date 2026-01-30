#!/usr/bin/env python3
"""
Create a simple test video with a stick figure for pipeline testing.
This allows testing without needing large video files.
"""

import cv2
import numpy as np
import os

def create_test_video(output_path, num_frames=30, fps=30, width=640, height=480):
    """
    Create a simple test video with a moving stick figure.
    
    Args:
        output_path: Path to save the video
        num_frames: Number of frames to generate
        fps: Frames per second
        width: Video width
        height: Video height
    """
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"Creating test video: {output_path}")
    print(f"  Frames: {num_frames}, FPS: {fps}, Size: {width}x{height}")
    
    for frame_idx in range(num_frames):
        # Create blank frame
        frame = np.ones((height, width, 3), dtype=np.uint8) * 240  # Light gray background
        
        # Calculate stick figure position (moves left to right)
        progress = frame_idx / num_frames
        x_center = int(width * 0.2 + width * 0.6 * progress)
        y_center = int(height * 0.5)
        
        # Draw stick figure (basic human pose)
        # Head
        cv2.circle(frame, (x_center, y_center - 80), 20, (0, 0, 255), -1)
        
        # Body (vertical line)
        cv2.line(frame, (x_center, y_center - 60), (x_center, y_center + 40), (0, 0, 255), 3)
        
        # Arms (simulating gun holding position)
        # Left arm
        left_shoulder = (x_center - 20, y_center - 50)
        left_elbow = (x_center - 40, y_center - 20)
        left_wrist = (x_center - 60, y_center - 10)
        cv2.line(frame, left_shoulder, left_elbow, (0, 255, 0), 3)
        cv2.line(frame, left_elbow, left_wrist, (0, 255, 0), 3)
        
        # Right arm (extended as if holding gun)
        right_shoulder = (x_center + 20, y_center - 50)
        right_elbow = (x_center + 50, y_center - 30)
        right_wrist = (x_center + 80, y_center - 25)
        cv2.line(frame, right_shoulder, right_elbow, (0, 255, 0), 3)
        cv2.line(frame, right_elbow, right_wrist, (0, 255, 0), 3)
        
        # Legs
        # Left leg
        left_hip = (x_center - 10, y_center + 40)
        left_knee = (x_center - 15, y_center + 80)
        left_ankle = (x_center - 10, y_center + 120)
        cv2.line(frame, left_hip, left_knee, (255, 0, 0), 3)
        cv2.line(frame, left_knee, left_ankle, (255, 0, 0), 3)
        
        # Right leg
        right_hip = (x_center + 10, y_center + 40)
        right_knee = (x_center + 15, y_center + 80)
        right_ankle = (x_center + 10, y_center + 120)
        cv2.line(frame, right_hip, right_knee, (255, 0, 0), 3)
        cv2.line(frame, right_knee, right_ankle, (255, 0, 0), 3)
        
        # Add frame number
        cv2.putText(frame, f"Frame: {frame_idx+1}/{num_frames}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Add "gun" rectangle
        gun_start = (right_wrist[0], right_wrist[1] - 5)
        gun_end = (right_wrist[0] + 40, right_wrist[1] + 5)
        cv2.rectangle(frame, gun_start, gun_end, (50, 50, 50), -1)
        
        # Write frame
        out.write(frame)
    
    out.release()
    print(f"✓ Test video created successfully!")
    print(f"  File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    
    return output_path


if __name__ == "__main__":
    # Create a 1-second test video (30 frames at 30 fps)
    output_path = "data/input/test_video.mp4"
    create_test_video(output_path, num_frames=30, fps=30)
    print(f"\nTest video ready at: {output_path}")
    print("You can now run the pipeline with this test video.")
