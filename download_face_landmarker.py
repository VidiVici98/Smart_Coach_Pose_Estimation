#!/usr/bin/env python3
"""
Download MediaPipe Face Landmarker model for gaze detection.
This is required for MediaPipe >= 0.10.8 which uses Tasks API.
"""

import urllib.request
import urllib.error
import os
import sys
import time

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL_PATH = "data/models/face_landmarker.task"
EXPECTED_SIZE_MB = 26.3  # Approximate expected size

print("=" * 60)
print("MediaPipe Face Landmarker Model Download")
print("=" * 60)

# Ensure directory exists
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# Check if already exists and is complete
if os.path.exists(MODEL_PATH):
    size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    print(f"\n✓ Face landmarker model already exists ({size_mb:.1f} MB)")
    print(f"  Location: {MODEL_PATH}")
    
    # Verify it's complete (should be ~26 MB)
    if size_mb < 25 or size_mb > 28:
        print(f"  ⚠ File size unexpected ({size_mb:.1f} MB), expected ~{EXPECTED_SIZE_MB:.1f} MB")
        print("  This indicates an incomplete or corrupted download")
        print("  Removing and re-downloading...")
        try:
            os.remove(MODEL_PATH)
        except:
            pass
    else:
        print("\n✓ Model is ready to use!")
        sys.exit(0)

print(f"\nDownloading face landmarker model...")
print(f"  URL: {MODEL_URL}")
print(f"  Destination: {MODEL_PATH}")
print(f"\n⏳ Starting download (this will take 30-60 seconds)...\n")

# Use a more robust download method with chunked reading
temp_path = MODEL_PATH + ".tmp"
max_retries = 3
retry_delay = 2

for attempt in range(max_retries):
    try:
        if attempt > 0:
            print(f"\n  Retry attempt {attempt + 1}/{max_retries}...")
            time.sleep(retry_delay)
        
        # Clean up any partial download
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Create request with headers
        req = urllib.request.Request(MODEL_URL)
        req.add_header('User-Agent', 'Mozilla/5.0')
        
        # Open connection
        with urllib.request.urlopen(req, timeout=60) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            
            if total_size == 0:
                print("  ⚠ Warning: Could not determine file size")
                total_size = int(EXPECTED_SIZE_MB * 1024 * 1024)  # Estimate
            
            downloaded = 0
            chunk_size = 8192  # 8KB chunks
            
            with open(temp_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Update progress
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        bars = int(percent / 2)
                        print(f"\r  [{'=' * bars}{' ' * (50 - bars)}] {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="", flush=True)
        
        print()  # New line after progress
        
        # Verify download completed
        if os.path.exists(temp_path):
            size_mb = os.path.getsize(temp_path) / (1024 * 1024)
            
            # Check if size is reasonable
            if size_mb < 25:
                print(f"\n  ⚠ Downloaded file too small ({size_mb:.1f} MB)")
                os.remove(temp_path)
                if attempt < max_retries - 1:
                    continue
                else:
                    raise Exception(f"Download incomplete after {max_retries} attempts")
            
            # Move temp file to final location
            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
            os.rename(temp_path, MODEL_PATH)
            
            print(f"\n" + "=" * 60)
            print(f"✓ Download successful! ({size_mb:.1f} MB)")
            print("=" * 60)
            print(f"\n  Model saved to: {MODEL_PATH}")
            print("\n✓ Gaze detection is now ENABLED")
            print("  You can now run the pipeline with full functionality:")
            print("    python3 scripts/processing/run_pipeline.py")
            sys.exit(0)
        else:
            raise Exception("Downloaded file not found")
            
    except KeyboardInterrupt:
        print("\n\n⚠ Download cancelled by user")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        sys.exit(1)
        
    except Exception as e:
        print(f"\n  ✗ Download attempt {attempt + 1} failed: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if attempt < max_retries - 1:
            continue
        else:
            print(f"\n✗ Download failed after {max_retries} attempts")
            print("\nTroubleshooting:")
            print("  1. Check your internet connection")
            print("  2. Try using wget or curl directly:")
            print(f"     wget {MODEL_URL} -O {MODEL_PATH}")
            print("     or")
            print(f"     curl -L {MODEL_URL} -o {MODEL_PATH}")
            print(f"\n  3. Verify the file size is ~26 MB after download")
            print(f"  4. If behind a proxy, you may need to configure it")
            sys.exit(1)
