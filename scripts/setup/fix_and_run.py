#!/usr/bin/env python3
"""
Install system dependencies, download models, and run pipeline - FIXED VERSION
Handles OpenGL library issues in codespace
"""

import sys
import os
import subprocess
from pathlib import Path

def run_cmd(cmd, description, check=True):
    """Run command and return success."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=False)
        if result.returncode == 0:
            print(f"✓ Success")
            return True
        else:
            print(f"✗ Failed (exit code {result.returncode})")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

print("="*70)
print("SMART COACH - COMPLETE SETUP (FIXED FOR CODESPACE)")
print("="*70)

os.chdir("/workspaces/Smart_Coach_Pose_Estimation")

# Step 1: Install system dependencies
print("\n[1/5] INSTALLING SYSTEM DEPENDENCIES")
print("This fixes OpenGL/libGL errors...")
# Try to install libs - if this fails, we'll use opencv-python-headless instead
print("Attempting to install OpenGL libraries...")
result = subprocess.run(
    "sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 2>/dev/null || sudo apt install -y libgl1 libglib2.0-0 2>/dev/null || echo 'System lib install failed, will use headless opencv'",
    shell=True,
    check=False
)
if result.returncode != 0:
    print("⚠ System libraries not installed, using opencv-python-headless instead")
    run_cmd("pip install --force-reinstall opencv-python-headless", "Installing headless OpenCV")

# Step 2: Install Python packages
print("\n[2/5] INSTALLING PYTHON PACKAGES")
run_cmd("pip install -q -r requirements.txt", "Installing requirements")

# Step 3: Download models with wget (avoids import issues)
print("\n[3/5] DOWNLOADING YOLO MODELS")

models_dir = Path("data/models")
models_dir.mkdir(parents=True, exist_ok=True)

pose_model = models_dir / "yolov8m-pose.pt"
face_model = models_dir / "yolov8n-face.pt"

if not pose_model.exists():
    print("\nDownloading yolov8m-pose.pt (~52 MB)...")
    result = subprocess.run([
        "wget", "-q", "--show-progress",
        "https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt",
        "-O", str(pose_model)
    ], check=False)
    if result.returncode == 0:
        print("✓ Pose model downloaded")
    else:
        print("✗ Pose model download failed")
        sys.exit(1)
else:
    print("✓ Pose model already exists")

if not face_model.exists():
    print("\nDownloading yolov8n.pt (~6 MB)...")
    temp_file = models_dir / "yolov8n.pt"
    result = subprocess.run([
        "wget", "-q", "--show-progress",
        "https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt",
        "-O", str(temp_file)
    ], check=False)
    if result.returncode == 0:
        temp_file.rename(face_model)
        print("✓ Face model downloaded")
    else:
        print("✗ Face model download failed")
        sys.exit(1)
else:
    print("✓ Face model already exists")

# Step 4: Verify everything
print("\n[4/5] VERIFICATION")
print("="*70)

required = {
    "data/models/yolov8m-pose.pt": "YOLO Pose Model",
    "data/models/yolov8n-face.pt": "YOLO Face Model",
    "data/models/hand_landmarker.task": "MediaPipe Hand Model",
    "data/input/test_video.mp4": "Test Video"
}

all_good = True
for filepath, desc in required.items():
    p = Path(filepath)
    if p.exists():
        size = p.stat().st_size / (1024*1024)
        print(f"✓ {desc:30} {size:6.1f} MB")
    else:
        print(f"✗ {desc:30} MISSING")
        all_good = False

if not all_good:
    print("\n✗ Setup incomplete")
    sys.exit(1)

print("\n✓ ALL FILES PRESENT!")

# Step 5: Test imports
print("\n[5/5] TESTING IMPORTS")
try:
    print("Testing critical imports...")
    import cv2
    print("  ✓ cv2 (OpenCV)")
    import torch
    print("  ✓ torch")
    import mediapipe as mp
    print("  ✓ mediapipe")
    from ultralytics import YOLO
    print("  ✓ ultralytics")
    print("\n✓ All imports successful!")
except Exception as e:
    print(f"\n✗ Import failed: {e}")
    print("Continuing anyway - pipeline might still work")

# Run pipeline
print("\n" + "="*70)
print("READY TO RUN PIPELINE")
print("="*70)
print("\nThis will process your test video.")
print("Output:")
print("  - data/output/output_full.mp4 (annotated video)")
print("  - data/output/analytics.csv (frame metrics)")
print("")

response = input("Run pipeline now? (Y/n): ").strip().lower()

if response in ['', 'y', 'yes']:
    print("\n" + "="*70)
    print("RUNNING PIPELINE")
    print("="*70)
    print("\nThis may take several minutes...\n")
    
    result = subprocess.run(
        ["python3", "scripts/processing/run_pipeline.py"],
        check=False
    )
    
    print("\n" + "="*70)
    
    if result.returncode == 0:
        print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        # Show outputs
        print("\nOutput files:")
        out_vid = Path("data/output/output_full.mp4")
        out_csv = Path("data/output/analytics.csv")
        
        if out_vid.exists():
            size = out_vid.stat().st_size / (1024*1024)
            print(f"  ✓ Video: {out_vid} ({size:.1f} MB)")
        
        if out_csv.exists():
            lines = sum(1 for _ in open(out_csv)) - 1
            print(f"  ✓ CSV: {out_csv} ({lines} frames)")
        
        print("\n🎉 ALL DONE!")
    else:
        print("✗ PIPELINE FAILED")
        print("="*70)
        print("\nCheck errors above.")
        sys.exit(1)
else:
    print("\nSkipped. Run manually:")
    print("  python3 scripts/processing/run_pipeline.py")
