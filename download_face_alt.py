#!/usr/bin/env python3
"""
Direct download of MediaPipe Face Landmarker from GitHub releases
Google Storage CDN is returning corrupted files (3.6MB instead of 26MB)
"""

import urllib.request
import os
import sys

# Try GitHub releases as alternative source
URLS = [
    # MediaPipe official release (if available)
    "https://github.com/google/mediapipe/raw/master/mediapipe/modules/face_landmark/face_landmarker.task",
    # Google Storage (known to be corrupted currently)
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
]

MODEL_PATH = "data/models/face_landmarker.task"
EXPECTED_MIN_SIZE = 25 * 1024 * 1024  # 25 MB
EXPECTED_MAX_SIZE = 28 * 1024 * 1024  # 28 MB

print("=" * 70)
print("  MediaPipe Face Landmarker - Alternative Download")
print("=" * 70)
print()

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

for url_idx, url in enumerate(URLS, 1):
    print(f"Attempt {url_idx}/{len(URLS)}")
    print(f"  URL: {url}")
    
    try:
        temp_path = MODEL_PATH + ".tmp"
        
        # Download with progress
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        
        with urllib.request.urlopen(req, timeout=120) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            if total_size > 0:
                print(f"  File size: {total_size / (1024*1024):.1f} MB")
            
            downloaded = 0
            chunk_size = 32768
            
            with open(temp_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
            print()  # Newline after progress
        
        # Verify file size
        actual_size = os.path.getsize(temp_path)
        print(f"  Downloaded: {actual_size / (1024*1024):.1f} MB")
        
        if EXPECTED_MIN_SIZE <= actual_size <= EXPECTED_MAX_SIZE:
            # Move to final location
            import shutil
            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
            shutil.move(temp_path, MODEL_PATH)
            
            print(f"  ✓ SUCCESS! Valid model downloaded")
            print()
            print("=" * 70)
            print("  Face landmarker is ready for use!")
            print("  Run: python3 scripts/processing/run_pipeline.py")
            print("=" * 70)
            sys.exit(0)
        else:
            print(f"  ✗ File size incorrect (expected 25-28 MB)")
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    print()

print("=" * 70)
print("  All download attempts failed")
print("=" * 70)
print()
print("WORKAROUND OPTIONS:")
print()
print("1. Manual download:")
print("   - Visit: https://developers.google.com/mediapipe/solutions/vision/face_landmarker")
print("   - Download face_landmarker.task manually")
print("   - Place in: data/models/face_landmarker.task")
print()
print("2. Run without gaze detection:")
print("   The pipeline will work with all other features:")
print("   - Pose skeleton")
print("   - Hand landmarks")
print("   - Body segmentation")
print()
print("   Just missing gaze cone visualization")
print()
sys.exit(1)
