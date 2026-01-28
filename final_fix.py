#!/usr/bin/env python3
"""
ONE-STEP FIX: Just replace opencv with headless version and run pipeline
Models are already downloaded, just need to fix the import error
"""
import subprocess
import sys

print("="*70)
print("FIXING OPENCV AND RUNNING PIPELINE")
print("="*70)

# Fix: Replace opencv-python with opencv-python-headless
print("\n[1/2] Fixing OpenCV (installing headless version)...")
subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "--force-reinstall", "opencv-python-headless"
], check=True)
print("✓ OpenCV headless installed (no display libs needed)")

# Test the import
print("\n[2/2] Testing import...")
try:
    import cv2
    print("✓ cv2 imports successfully!")
except Exception as e:
    print(f"✗ Still broken: {e}")
    sys.exit(1)

# Run the pipeline
print("\n" + "="*70)
print("RUNNING PIPELINE")
print("="*70)
print()

result = subprocess.run([sys.executable, "scripts/processing/run_pipeline.py"])

if result.returncode == 0:
    print("\n" + "="*70)
    print("✓ SUCCESS!")
    print("="*70)
    print("\nCheck output in data/output/")
else:
    print("\n✗ Pipeline failed")
    sys.exit(1)
