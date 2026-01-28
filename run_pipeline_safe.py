#!/usr/bin/env python3
"""
Safe pipeline runner with better error reporting.
Runs the pipeline and captures any errors for debugging.
"""

import sys
import os
import subprocess
import signal

def timeout_handler(signum, frame):
    print("\n" + "=" * 60)
    print("TIMEOUT: Process took too long (>120s)")
    print("=" * 60)
    sys.exit(124)

print("=" * 60)
print("Smart Coach Pipeline Runner (Safe Mode)")
print("=" * 60)

# Change to repo directory
os.chdir('/workspaces/Smart_Coach_Pose_Estimation')

# Set up timeout (120 seconds max for testing)
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(120)

try:
    # Run the pipeline
    print("\nLaunching pipeline...\n")
    result = subprocess.run(
        [sys.executable, 'scripts/processing/run_pipeline.py'],
        capture_output=False,
        text=True,
        timeout=120
    )
    
    signal.alarm(0)  # Cancel timeout
    
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("✓ Pipeline completed successfully!")
    elif result.returncode == -15 or result.returncode == 143:
        print(f"✗ Pipeline terminated with SIGTERM (exit code {result.returncode})")
        print("\nPossible causes:")
        print("  1. Segmentation fault in MediaPipe or OpenCV")
        print("  2. Out of memory")
        print("  3. Incompatible library versions")
        print("\nTry running: python3 test_mediapipe_init.py")
    else:
        print(f"✗ Pipeline failed with exit code {result.returncode}")
    print("=" * 60)
    
    sys.exit(result.returncode)
    
except subprocess.TimeoutExpired:
    signal.alarm(0)
    print("\n" + "=" * 60)
    print("✗ Pipeline timed out after 120 seconds")
    print("=" * 60)
    sys.exit(124)
except KeyboardInterrupt:
    signal.alarm(0)
    print("\n" + "=" * 60)
    print("⚠ Pipeline interrupted by user")
    print("=" * 60)
    sys.exit(130)
except Exception as e:
    signal.alarm(0)
    print("\n" + "=" * 60)
    print(f"✗ Unexpected error: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
