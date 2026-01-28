#!/usr/bin/env python3
import subprocess
import sys

print("Installing libGL system library...")

# Try multiple methods
methods = [
    "apt-get install -y libgl1-mesa-glx",
    "apt-get install -y libgl1",
    "apt install -y libgl1-mesa-glx", 
    "apt install -y libgl1"
]

for cmd in methods:
    print(f"Trying: {cmd}")
    result = subprocess.run(f"sudo {cmd}", shell=True, capture_output=True)
    if result.returncode == 0:
        print("✓ Installed!")
        break
    else:
        print(f"  Failed: {result.stderr.decode()[:100]}")

print("\nTesting import...")
try:
    import cv2
    print("✓ cv2 works!")
    print("\nRunning pipeline...")
    subprocess.run([sys.executable, "scripts/processing/run_pipeline.py"])
except Exception as e:
    print(f"✗ Still failing: {e}")
