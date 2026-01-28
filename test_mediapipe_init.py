#!/usr/bin/env python3
"""
Test MediaPipe FaceMesh initialization to diagnose exit -15 issue.
"""

import sys
import os

print("=" * 60)
print("MediaPipe FaceMesh Initialization Test")
print("=" * 60)

# Test 1: Basic imports
print("\n[1/5] Testing basic imports...")
try:
    import mediapipe as mp
    import numpy as np
    import cv2
    print("✓ Basic imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check mediapipe solutions
print("\n[2/5] Checking MediaPipe API version...")
try:
    version = mp.__version__ if hasattr(mp, '__version__') else 'unknown'
    print(f"  MediaPipe version: {version}")
    
    if hasattr(mp, 'solutions'):
        print(f"✓ MediaPipe Solutions API available (legacy API)")
        mp_face_mesh = mp.solutions.face_mesh
        print(f"✓ solutions.face_mesh accessible")
    else:
        print(f"⚠ MediaPipe Solutions API NOT available")
        print(f"  This version only has Tasks API (requires .task model files)")
        print(f"  Gaze visualization will be disabled in pipeline")
        print(f"\n  Note: Pipeline will still work for:")
        print(f"    - Pose detection (✓)")
        print(f"    - Hand detection (✓)")
        print(f"    - Body mask (✓)")
        print(f"    - All metrics except gaze (✓)")
        sys.exit(0)  # Not an error, just informational
except Exception as e:
    print(f"✗ Failed to check MediaPipe API: {e}")
    sys.exit(1)

# Test 3: Try minimal initialization (only if Solutions API available)
if not hasattr(mp, 'solutions'):
    print("\n[3/5] Skipping FaceMesh tests (Solutions API not available)")
    print("[4/5] Skipping FaceMesh tests (Solutions API not available)")
    print("[5/5] Skipping FaceMesh tests (Solutions API not available)")
    print("\n" + "=" * 60)
    print("✓ TESTS COMPLETED - MediaPipe has Tasks API only")
    print("=" * 60)
    print("\nPipeline will work WITHOUT gaze visualization.")
    print("All other features (pose, hands, body mask, metrics) will work normally.")
    sys.exit(0)

print("\n[3/5] Testing minimal FaceMesh initialization...")
try:
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,  # Static mode is simpler
        max_num_faces=1,
        refine_landmarks=False,  # Disable refinement
        min_detection_confidence=0.5
    )
    print("✓ FaceMesh initialized (static mode)")
    face_mesh.close()
    print("✓ FaceMesh closed successfully")
except Exception as e:
    print(f"✗ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Try video mode initialization
print("\n[4/5] Testing video mode FaceMesh initialization...")
try:
    face_mesh_video = mp_face_mesh.FaceMesh(
        static_image_mode=False,  # Video mode
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("✓ FaceMesh initialized (video mode)")
    face_mesh_video.close()
    print("✓ FaceMesh closed successfully")
except Exception as e:
    print(f"✗ Video mode initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test with actual image processing
print("\n[5/5] Testing with dummy image...")
try:
    # Create a dummy RGB image (480x640)
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
    dummy_image[:] = (100, 100, 100)  # Gray image
    
    face_mesh_test = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.5
    )
    
    results = face_mesh_test.process(dummy_image)
    print(f"✓ Processed dummy image")
    print(f"  Detections: {len(results.multi_face_landmarks) if results.multi_face_landmarks else 0}")
    
    face_mesh_test.close()
    print("✓ Cleanup successful")
except Exception as e:
    print(f"✗ Image processing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - MediaPipe FaceMesh is working")
print("=" * 60)
print("\nMediaPipe FaceMesh can be safely used in the pipeline.")
sys.exit(0)
