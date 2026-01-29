#!/usr/bin/env python3
"""
Quick setup and run script for Smart Coach pipeline.
Downloads face landmarker model if needed and runs the pipeline.
"""

import os
import sys
import subprocess

print("=" * 60)
print("Smart Coach - Quick Setup & Run")
print("=" * 60)

# Check if face landmarker exists
FACE_MODEL_PATH = "data/models/face_landmarker.task"

if not os.path.exists(FACE_MODEL_PATH):
    print("\n⚠ Face landmarker model not found")
    print("  This is required for gaze detection (one-time download ~26 MB)")
    response = input("\nDownload now? (Y/n): ").strip().lower()
    
    if response == '' or response == 'y' or response == 'yes':
        print("\nDownloading face landmarker model...")
        result = subprocess.run([sys.executable, 'download_face_landmarker.py'])
        if result.returncode != 0:
            print("\n✗ Download failed")
            print("  Pipeline will run WITHOUT gaze visualization")
            response = input("\nContinue anyway? (Y/n): ").strip().lower()
            if response != '' and response != 'y' and response != 'yes':
                sys.exit(1)
    else:
        print("\n⚠ Skipping download - gaze visualization will be disabled")
else:
    print("\n✓ Face landmarker model found")

# Run the pipeline
print("\n" + "=" * 60)
print("Running pipeline...")
print("=" * 60 + "\n")

result = subprocess.run([sys.executable, 'scripts/processing/run_pipeline.py'])
sys.exit(result.returncode)
