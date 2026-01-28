#!/usr/bin/env python3
"""Quick test to verify pipeline can initialize without errors."""

import sys
import os

# Add project root to path
sys.path.insert(0, '/workspaces/Smart_Coach_Pose_Estimation')

print("Testing pipeline initialization...")

try:
    # Test imports
    print("1. Testing imports...")
    import cv2
    import torch
    import numpy as np
    from ultralytics import YOLO
    import mediapipe as mp
    print("   ✓ All imports successful")
    
    # Test MediaPipe FaceMesh initialization
    print("2. Testing MediaPipe FaceMesh...")
    mp_face_mesh = mp.solutions.face_mesh
    mp_face = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("   ✓ MediaPipe FaceMesh initialized")
    mp_face.close()
    
    # Test model files exist
    print("3. Checking model files...")
    model_files = [
        "data/models/yolov8m-pose.pt",
        "data/models/yolov8n-face.pt",
        "data/models/hand_landmarker.task"
    ]
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"   ✓ {model_file}")
        else:
            print(f"   ✗ {model_file} - MISSING")
            sys.exit(1)
    
    # Test video file exists
    print("4. Checking input video...")
    video_path = "data/input/test_video.mp4"
    if os.path.exists(video_path):
        print(f"   ✓ {video_path}")
    else:
        print(f"   ✗ {video_path} - MISSING")
        sys.exit(1)
    
    print("\n✓ All pre-flight checks passed!")
    print("Pipeline should be ready to run.")
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ Error during initialization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
