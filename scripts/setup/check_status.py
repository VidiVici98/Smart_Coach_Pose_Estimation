#!/usr/bin/env python3
"""
Simple inline diagnostic - run this to check system status
"""
import sys
import os
from pathlib import Path

print("="*70)
print("SMART COACH DIAGNOSTICS")
print("="*70)

# 1. Python version
print(f"\n[1] Python: {sys.version}")
print(f"    Executable: {sys.executable}")

# 2. Check packages
print("\n[2] Package Status:")
packages = {
    'torch': 'torch',
    'torchvision': 'torchvision', 
    'cv2': 'opencv-python',
    'numpy': 'numpy',
    'mediapipe': 'mediapipe',
    'ultralytics': 'ultralytics',
    'pandas': 'pandas',
    'scipy': 'scipy'
}

missing = []
for import_name, pkg_name in packages.items():
    try:
        mod = __import__(import_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"    ✓ {pkg_name} ({version})")
    except ImportError as e:
        print(f"    ✗ {pkg_name} - MISSING")
        missing.append(pkg_name)

# 3. Check models
print("\n[3] Model Files:")
models_dir = Path("data/models")
required = {
    "yolov8m-pose.pt": "YOLO Pose",
    "yolov8n-face.pt": "YOLO Face", 
    "hand_landmarker.task": "MediaPipe Hands"
}

missing_models = []
for filename, desc in required.items():
    filepath = models_dir / filename
    if filepath.exists():
        size = filepath.stat().st_size / (1024*1024)
        print(f"    ✓ {desc} ({size:.1f} MB)")
    else:
        print(f"    ✗ {desc} - MISSING: {filepath}")
        missing_models.append(filename)

# 4. Check test video
print("\n[4] Test Video:")
video_path = Path("data/input/test_video.mp4")
if video_path.exists():
    size = video_path.stat().st_size / (1024*1024)
    print(f"    ✓ test_video.mp4 ({size:.1f} MB)")
else:
    print(f"    ✗ test_video.mp4 - MISSING")

# 5. Check output directory
print("\n[5] Output Directory:")
output_dir = Path("data/output")
output_dir.mkdir(parents=True, exist_ok=True)
print(f"    ✓ {output_dir} exists")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

issues = []
if missing:
    issues.append(f"Missing packages: {', '.join(missing)}")
    print(f"\n✗ Missing Python packages ({len(missing)}):")
    print(f"   Fix: pip install {' '.join(missing)}")

if missing_models:
    issues.append(f"Missing models: {', '.join(missing_models)}")
    print(f"\n✗ Missing model files ({len(missing_models)}):")
    print(f"   Fix: python scripts/tools/download_models.py")

if not video_path.exists():
    issues.append("Missing test video")
    print(f"\n✗ Missing test video:")
    print(f"   Fix: cp your_video.mp4 data/input/test_video.mp4")

if not issues:
    print("\n✓ All requirements met! Ready to run:")
    print("   python scripts/processing/run_pipeline.py")
else:
    print(f"\n⚠ Found {len(issues)} issue(s) - see fixes above")

print("\nFor detailed help, see: SETUP.md")
print("="*70)
