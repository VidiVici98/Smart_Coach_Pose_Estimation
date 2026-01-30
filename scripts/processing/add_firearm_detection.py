"""
Script to add firearm detection capability to existing pipeline

This script demonstrates how to integrate the FirearmDetector into the
Smart Coach pipeline for improved muzzle direction tracking.

Usage:
    python scripts/processing/add_firearm_detection.py [input_video]

This creates an enhanced version of the pipeline with firearm detection.
"""

import os
import sys
import cv2
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from smart_coach.models.firearm_detector import (
    FirearmDetector,
    fuse_firearm_and_arm_estimates,
    check_muzzle_body_intersection,
    draw_firearm_detection
)

# Configuration for firearm detection
FIREARM_DETECTION_CONFIG = {
    'enabled': True,
    'model_path': 'data/models/yolov8n.pt',  # Standard YOLOv8 (may detect some weapons)
    'confidence_threshold': 0.3,
    'target_classes': ['gun', 'handgun', 'pistol', 'firearm', 'weapon', 'rifle'],
    'smoothing_alpha': 0.7,
    'fusion_confidence_threshold': 0.5,
    'fusion_blend_weight': 0.8,
    'visualize_detection': True,
}


def integrate_firearm_detection_example(video_path: str):
    """
    Example of integrating firearm detection into processing pipeline.
    
    This demonstrates the key integration points:
    1. Initialize FirearmDetector
    2. Detect firearm in each frame
    3. Fuse with arm kinematics
    4. Calculate muzzle direction
    5. Check safety (muzzle-body intersection)
    """
    # Load video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video: {video_path}")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"  Total frames: {total_frames}")
    print()
    
    # Initialize firearm detector (if model exists)
    firearm_detector = None
    if os.path.exists(FIREARM_DETECTION_CONFIG['model_path']):
        try:
            from ultralytics import YOLO
            model = YOLO(FIREARM_DETECTION_CONFIG['model_path'])
            firearm_detector = FirearmDetector(
                model=model,
                confidence_threshold=FIREARM_DETECTION_CONFIG['confidence_threshold'],
                target_classes=FIREARM_DETECTION_CONFIG['target_classes'],
                smoothing_alpha=FIREARM_DETECTION_CONFIG['smoothing_alpha']
            )
            print(f"✓ Firearm detector initialized")
            print(f"  Model: {FIREARM_DETECTION_CONFIG['model_path']}")
            print(f"  Target classes: {FIREARM_DETECTION_CONFIG['target_classes']}")
        except Exception as e:
            print(f"⚠ Could not initialize firearm detector: {e}")
            print(f"  Will use arm kinematics only")
    else:
        print(f"⚠ Firearm detection model not found: {FIREARM_DETECTION_CONFIG['model_path']}")
        print(f"  Will use arm kinematics only")
    
    print()
    print("Processing frames...")
    
    # Process frames
    frame_count = 0
    detections_found = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Detect firearm (if detector available)
        firearm_detection = None
        if firearm_detector is not None:
            firearm_detection = firearm_detector.detect(frame)
            if firearm_detection is not None:
                detections_found += 1
        
        # In real pipeline, you would:
        # 1. Get arm kinematics estimate from pose detection
        # 2. Fuse firearm and arm estimates
        # 3. Update CSV with firearm metrics
        # 4. Check safety (muzzle-body intersection)
        # 5. Visualize if enabled
        
        if frame_count % 30 == 0:  # Print every second
            status = "✓" if firearm_detection is not None else " "
            print(f"  Frame {frame_count}/{total_frames} {status}")
    
    cap.release()
    
    print()
    print("Summary:")
    print(f"  Total frames processed: {frame_count}")
    print(f"  Firearm detections: {detections_found}")
    if frame_count > 0:
        print(f"  Detection rate: {100.0 * detections_found / frame_count:.1f}%")
    print()
    
    if detections_found == 0:
        print("⚠ No firearms detected in this video.")
        print("  This is expected if:")
        print("  - The video doesn't contain firearms")
        print("  - Using a model without firearm classes trained")
        print("  - Detection confidence threshold is too high")
        print()
        print("  To enable firearm detection:")
        print("  1. Use a model trained on firearms/weapons")
        print("  2. Fine-tune YOLOv8 on firearm dataset")
        print("  3. Lower confidence threshold (may increase false positives)")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test firearm detection integration"
    )
    parser.add_argument(
        'video',
        nargs='?',
        default='data/input/test_video.mp4',
        help='Path to input video'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Video not found: {args.video}")
        sys.exit(1)
    
    integrate_firearm_detection_example(args.video)


if __name__ == '__main__':
    main()
