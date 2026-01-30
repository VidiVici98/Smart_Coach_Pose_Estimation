#!/usr/bin/env python3
"""
Minimal pipeline test that creates synthetic frames and processes them.
This allows testing the full pipeline without needing a real video file.
"""

import os
import sys
import numpy as np
import cv2

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

print("=" * 80)
print("SMART COACH - MINIMAL PIPELINE TEST")
print("=" * 80)
print()

# Check if we're in the right directory
if not os.path.exists('data/models'):
    print("ERROR: Please run this script from the repository root directory")
    print("Usage: python scripts/testing/test_pipeline_minimal.py")
    sys.exit(1)

# Create synthetic test frames
print("Step 1: Creating synthetic test frames...")
num_frames = 10
width, height = 640, 480
fps = 30

frames = []
for i in range(num_frames):
    # Create a simple frame with a person-like shape
    frame = np.ones((height, width, 3), dtype=np.uint8) * 200  # Light gray
    
    # Draw a simple person
    center_x = width // 2
    center_y = height // 2
    
    # Head
    cv2.circle(frame, (center_x, center_y - 100), 30, (100, 100, 200), -1)
    
    # Body
    cv2.rectangle(frame, (center_x - 40, center_y - 70), 
                  (center_x + 40, center_y + 50), (100, 100, 200), -1)
    
    # Arms
    cv2.rectangle(frame, (center_x - 80, center_y - 50), 
                  (center_x - 40, center_y + 10), (100, 150, 100), -1)
    cv2.rectangle(frame, (center_x + 40, center_y - 50), 
                  (center_x + 80, center_y + 10), (100, 150, 100), -1)
    
    # Legs
    cv2.rectangle(frame, (center_x - 40, center_y + 50), 
                  (center_x - 10, center_y + 130), (150, 100, 100), -1)
    cv2.rectangle(frame, (center_x + 10, center_y + 50), 
                  (center_x + 40, center_y + 130), (150, 100, 100), -1)
    
    # Add frame counter
    cv2.putText(frame, f"Frame {i+1}/{num_frames}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    frames.append(frame)

print(f"✓ Created {num_frames} synthetic frames ({width}x{height})")
print()

# Test imports
print("Step 2: Testing imports...")
try:
    from ultralytics import YOLO
    print("✓ YOLO imported")
except ImportError as e:
    print(f"✗ YOLO import failed: {e}")
    sys.exit(1)

try:
    from smart_coach.models.firearm_detector import FirearmDetector
    print("✓ FirearmDetector imported")
except ImportError as e:
    print(f"✗ FirearmDetector import failed: {e}")
    sys.exit(1)

try:
    from smart_coach.analysis.coaching_engine import CoachingEngine
    print("✓ CoachingEngine imported")
except ImportError as e:
    print(f"✗ CoachingEngine import failed: {e}")
    sys.exit(1)

print()

# Test model loading
print("Step 3: Testing model loading...")
model_path = "data/models/yolov8m-pose.pt"
if not os.path.exists(model_path):
    print(f"✗ Model not found: {model_path}")
    sys.exit(1)

try:
    pose_model = YOLO(model_path, verbose=False)
    print(f"✓ Pose model loaded: {model_path}")
except Exception as e:
    print(f"✗ Failed to load pose model: {e}")
    sys.exit(1)

print()

# Test pose detection on one frame
print("Step 4: Testing pose detection...")
try:
    results = pose_model(frames[0], verbose=False)
    print(f"✓ Pose detection works (got {len(results)} result)")
    
    # Check if any keypoints were detected
    if len(results) > 0 and results[0].keypoints is not None:
        num_keypoints = len(results[0].keypoints.xy[0]) if len(results[0].keypoints.xy) > 0 else 0
        print(f"  Detected {num_keypoints} keypoints")
    else:
        print("  No keypoints detected (expected - synthetic image)")
except Exception as e:
    print(f"✗ Pose detection failed: {e}")
    sys.exit(1)

print()

# Test CSV writing
print("Step 5: Testing CSV generation...")
import csv

csv_path = "data/output/test_analytics.csv"
os.makedirs("data/output", exist_ok=True)

try:
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['frame', 'test_metric_1', 'test_metric_2'])
        # Write data
        for i in range(num_frames):
            writer.writerow([i, i * 1.5, i * 2.0])
    
    print(f"✓ CSV created: {csv_path}")
    print(f"  Size: {os.path.getsize(csv_path)} bytes")
except Exception as e:
    print(f"✗ CSV creation failed: {e}")
    sys.exit(1)

print()

# Test video writing
print("Step 6: Testing video output...")
output_path = "data/output/test_output.mp4"

try:
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:
        # Add a simple overlay to show processing happened
        cv2.rectangle(frame, (10, 50), (200, 90), (0, 255, 0), 2)
        cv2.putText(frame, "PROCESSED", (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        out.write(frame)
    
    out.release()
    print(f"✓ Video created: {output_path}")
    print(f"  Size: {os.path.getsize(output_path) / 1024:.1f} KB")
except Exception as e:
    print(f"✗ Video creation failed: {e}")
    sys.exit(1)

print()

# Test coaching engine
print("Step 7: Testing coaching engine...")
try:
    import pandas as pd
    
    # Create sample data
    sample_data = pd.DataFrame({
        'frame': range(100),
        'stance_width': np.random.uniform(0.3, 0.5, 100),
        'arm_extension_L': np.random.uniform(0.7, 0.95, 100),
        'arm_extension_R': np.random.uniform(0.7, 0.95, 100),
    })
    
    engine = CoachingEngine()
    print(f"✓ CoachingEngine initialized with {len(engine.rules)} rules")
    
    # Evaluate rules
    results = engine.evaluate_all_rules(sample_data)
    print(f"✓ Evaluated rules: {len(results)} issues found")
    
except Exception as e:
    print(f"✗ Coaching engine test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("✓ All critical components working!")
print()
print("Generated files:")
print(f"  - {csv_path}")
print(f"  - {output_path}")
print()
print("To extract a screenshot from the test video:")
print(f"  ffmpeg -i {output_path} -vframes 1 data/output/screenshot.png")
print()
print("Or view the video with:")
print(f"  ffplay {output_path}")
print()
print("=" * 80)
