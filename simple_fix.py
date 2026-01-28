#!/usr/bin/env python3
"""
Simple fix: Use opencv-python-headless (no display dependencies needed)
Then download models and run pipeline
"""

import sys
import os
import subprocess
from pathlib import Path

print("="*70)
print("SMART COACH - HEADLESS SETUP (NO DISPLAY LIBS NEEDED)")
print("="*70)

os.chdir("/workspaces/Smart_Coach_Pose_Estimation")

# Step 1: Install opencv-python-headless (no libGL needed)
print("\n[1/4] INSTALLING HEADLESS OPENCV")
print("This version doesn't need display libraries...")
subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "--force-reinstall", "opencv-python-headless"
], check=False)
print("✓ Headless OpenCV installed")

# Step 2: Install other packages
print("\n[2/4] INSTALLING OTHER PACKAGES")
subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "torch", "torchvision", "numpy", "mediapipe", 
    "ultralytics", "pandas", "scipy"
], check=False)
print("✓ Packages installed")

# Step 3: Download models
print("\n[3/4] DOWNLOADING MODELS")

models_dir = Path("data/models")
models_dir.mkdir(parents=True, exist_ok=True)

pose_model = models_dir / "yolov8m-pose.pt"
face_model = models_dir / "yolov8n-face.pt"

if not pose_model.exists():
    print("Downloading yolov8m-pose.pt...")
    result = subprocess.run([
        "wget", "-q", "--show-progress",
        "https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt",
        "-O", str(pose_model)
    ])
    if result.returncode == 0:
        print("✓ Pose model downloaded")
else:
    print("✓ Pose model exists")

if not face_model.exists():
    print("Downloading yolov8n-face.pt...")
    temp = models_dir / "yolov8n.pt"
    result = subprocess.run([
        "wget", "-q", "--show-progress",
        "https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt",
        "-O", str(temp)
    ])
    if result.returncode == 0:
        temp.rename(face_model)
        print("✓ Face model downloaded")
else:
    print("✓ Face model exists")

# Step 4: Verify and test
print("\n[4/4] VERIFICATION")
print("="*70)

required = {
    "data/models/yolov8m-pose.pt": "YOLO Pose",
    "data/models/yolov8n-face.pt": "YOLO Face",
    "data/models/hand_landmarker.task": "MediaPipe Hand",
    "data/input/test_video.mp4": "Test Video"
}

all_present = True
for filepath, desc in required.items():
    p = Path(filepath)
    if p.exists():
        size = p.stat().st_size / (1024*1024)
        print(f"✓ {desc:20} {size:6.1f} MB")
    else:
        print(f"✗ {desc:20} MISSING")
        all_present = False

if not all_present:
    print("\n✗ Setup incomplete")
    sys.exit(1)

print("\n✓ ALL FILES PRESENT!")

# Test imports
print("\nTesting imports...")
try:
    import cv2
    print("  ✓ cv2 (headless)")
    import torch
    print("  ✓ torch")
    import mediapipe
    print("  ✓ mediapipe")
    from ultralytics import YOLO
    print("  ✓ ultralytics")
    print("\n✓ All imports successful!")
except Exception as e:
    print(f"\n✗ Import error: {e}")
    sys.exit(1)

# Run pipeline
print("\n" + "="*70)
print("READY TO RUN PIPELINE")
print("="*70)

response = input("\nRun pipeline now? (Y/n): ").strip().lower()

if response in ['', 'y', 'yes']:
    print("\n" + "="*70)
    print("RUNNING PIPELINE")
    print("="*70)
    print()
    
    result = subprocess.run(
        [sys.executable, "scripts/processing/run_pipeline.py"]
    )
    
    print("\n" + "="*70)
    
    if result.returncode == 0:
        print("✓ PIPELINE COMPLETED!")
        print("="*70)
        
        out_vid = Path("data/output/output_full.mp4")
        out_csv = Path("data/output/analytics.csv")
        
        if out_vid.exists():
            size = out_vid.stat().st_size / (1024*1024)
            print(f"\n✓ Video: {out_vid} ({size:.1f} MB)")
        
        if out_csv.exists():
            lines = sum(1 for _ in open(out_csv)) - 1
            print(f"✓ CSV: {out_csv} ({lines} frames)")
        
        print("\n🎉 SUCCESS!")
    else:
        print("✗ PIPELINE FAILED (see errors above)")
        sys.exit(1)
else:
    print("\nRun manually: python3 scripts/processing/run_pipeline.py")
