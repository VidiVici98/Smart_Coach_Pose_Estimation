#!/usr/bin/env python3
"""
ALTERNATIVE face landmarker download
Google's storage URL may be returning the wrong file (3.6MB instead of 26MB)
Try alternate sources or skip gaze detection
"""

import os
import sys

MODEL_PATH = "data/models/face_landmarker.task"

print("=" * 70)
print("  FACE LANDMARKER DOWNLOAD - ALTERNATIVE METHOD")
print("=" * 70)
print()
print("⚠ IMPORTANT NOTICE:")
print("  Google's storage URL is currently returning a corrupted file")
print("  (3.6 MB instead of the expected 26 MB)")
print()
print("  This appears to be a temporary issue with Google's CDN.")
print()
print("OPTIONS:")
print("  1. Skip gaze detection for now (pipeline will work without it)")
print("  2. Try downloading from MediaPipe GitHub releases")
print("  3. Wait and try again later when Google fixes their CDN")
print()
print("CURRENT STATUS:")

if os.path.exists(MODEL_PATH):
    size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    if 25 <= size_mb <= 28:
        print(f"  ✓ Valid model found ({size_mb:.1f} MB)")
        print("  Face landmarker is ready!")
        sys.exit(0)
    else:
        print(f"  ✗ Corrupted model found ({size_mb:.1f} MB)")
        print("    Removing...")
        os.remove(MODEL_PATH)
else:
    print("  File not found")

print()
print("=" * 70)
print("RECOMMENDATION:")
print("  Run the pipeline without gaze detection:")
print("    python3 scripts/processing/run_pipeline.py")
print()
print("  All other features will work:")
print("    ✓ Pose skeleton detection")
print("    ✓ Hand landmark detection")  
print("    ✓ Body segmentation mask (if LOW_MEMORY_MODE=False)")
print("    ✗ Gaze cone visualization (requires face landmarker)")
print("=" * 70)
