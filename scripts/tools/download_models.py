#!/usr/bin/env python3
"""
Download required model files for Smart Coach Pose Estimation.
This script automatically downloads all necessary models to the data/models/ directory.
"""

import sys
import os
from pathlib import Path
import urllib.request
import shutil

def download_file(url, destination, description):
    """Download a file with progress indicator."""
    print(f"Downloading {description}...")
    print(f"  URL: {url}")
    print(f"  Destination: {destination}")
    
    try:
        # Create a temporary file (use Path object for consistency)
        temp_file = destination.with_suffix(destination.suffix + ".tmp")
        
        def show_progress(block_num, block_size, total_size):
            """Show download progress."""
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded / total_size) * 100)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r  Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')
            else:
                mb_downloaded = downloaded / (1024 * 1024)
                print(f"\r  Downloaded: {mb_downloaded:.1f} MB", end='')
        
        urllib.request.urlretrieve(url, str(temp_file), show_progress)
        print()  # New line after progress
        
        # Move temp file to final destination
        shutil.move(str(temp_file), str(destination))
        
        # Verify file exists
        if destination.exists():
            size_mb = destination.stat().st_size / (1024 * 1024)
            print(f"  ✓ Download complete ({size_mb:.1f} MB)\n")
            return True
        else:
            print(f"  ✗ Error: File not found after download\n")
            return False
            
    except Exception as e:
        print(f"\n  ✗ Error downloading: {e}\n")
        # Clean up temp file if it exists
        if temp_file.exists():
            temp_file.unlink()
        return False

def download_yolo_models():
    """Download YOLOv8 models using ultralytics."""
    print("Downloading YOLOv8 models using ultralytics...")
    
    try:
        from ultralytics import YOLO
    except ImportError:
        print("  ✗ Error: ultralytics not installed")
        print("    Install with: pip install ultralytics")
        return False
    
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Download YOLOv8 Pose model
    print("\n1. YOLOv8 Pose Model (yolov8m-pose)...")
    try:
        model = YOLO('yolov8m-pose.pt')
        # Find where it was downloaded
        cache_path = Path.home() / ".cache" / "ultralytics"
        source_file = None
        for root, dirs, files in os.walk(cache_path):
            if "yolov8m-pose.pt" in files:
                source_file = Path(root) / "yolov8m-pose.pt"
                break
        
        dest_file = models_dir / "yolov8m-pose.pt"
        if source_file and source_file.exists():
            shutil.copy(source_file, dest_file)
            size_mb = dest_file.stat().st_size / (1024 * 1024)
            print(f"  ✓ Copied to {dest_file} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ Could not locate downloaded file")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # Download YOLOv8 Face model
    print("\n2. YOLOv8 Face Model (yolov8n-face)...")
    print("  Note: Standard YOLOv8 doesn't include face detection by default.")
    print("  Using yolov8n.pt as a generic object detector.")
    print("  ⚠ WARNING: This is NOT a face-specific model. For production use,")
    print("  consider training or obtaining a custom YOLOv8 face detection model.")
    try:
        model = YOLO('yolov8n.pt')
        cache_path = Path.home() / ".cache" / "ultralytics"
        source_file = None
        for root, dirs, files in os.walk(cache_path):
            if "yolov8n.pt" in files:
                source_file = Path(root) / "yolov8n.pt"
                break
        
        dest_file = models_dir / "yolov8n-face.pt"
        if source_file and source_file.exists():
            shutil.copy(source_file, dest_file)
            size_mb = dest_file.stat().st_size / (1024 * 1024)
            print(f"  ✓ Copied to {dest_file} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ Could not locate downloaded file")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    return True

def download_mediapipe_hand_model(use_lightweight=False):
    """Download MediaPipe Hand Landmarker model.
    
    Args:
        use_lightweight: If True, downloads lightweight model (~3.6MB float16). 
                        If False, downloads full model (~26MB full precision).
                        Note: Currently only float16 version is available from MediaPipe.
    """
    print("\n3. MediaPipe Hand Landmarker Model...")
    
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Note: MediaPipe only provides float16 version publicly
    # The float16 version is ~3.6MB and is suitable for both cases
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    
    if use_lightweight:
        print("  Using lightweight model (float16) - optimized for codespace")
    else:
        print("  Using standard model (float16)")
    
    destination = models_dir / "hand_landmarker.task"
    
    if destination.exists():
        print(f"  File already exists: {destination}")
        size_mb = destination.stat().st_size / (1024 * 1024)
        print(f"  Size: {size_mb:.1f} MB")
        
        # Skip re-download prompt in automated environments
        if os.environ.get('SMART_COACH_CODESPACE') or os.environ.get('CI'):
            print("  Skipping download (file exists).\n")
            return True
            
        response = input("  Re-download? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("  Skipping download.\n")
            return True
        print()
    
    return download_file(url, destination, "MediaPipe Hand Landmarker")

def main():
    """Main entry point."""
    print("=" * 70)
    print("Smart Coach Model Download Script")
    print("=" * 70)
    print()
    print("This script downloads all required model files for the pipeline.")
    print()
    
    # Change to repo root if script is run from scripts/tools/
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    os.chdir(repo_root)
    print(f"Repository root: {repo_root}\n")
    
    # Create models directory
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    print(f"Models directory: {models_dir}\n")
    
    # Check if we're in a codespace or should use lightweight models
    use_lightweight = (
        os.environ.get('SMART_COACH_CODESPACE') == 'true' or
        os.environ.get('USE_LIGHTWEIGHT_MODELS') == 'true' or
        os.environ.get('CODESPACES') is not None
    )
    
    if use_lightweight:
        print("🌐 Codespace/Lightweight mode detected")
        print("   Using optimized models for faster download and lower memory usage\n")
    
    print("=" * 70)
    print("Downloading Models")
    print("=" * 70)
    
    # Download models
    results = {
        "YOLOv8 Models": download_yolo_models(),
        "MediaPipe Hand Model": download_mediapipe_hand_model(use_lightweight=use_lightweight)
    }
    
    # Summary
    print("=" * 70)
    print("Download Summary")
    print("=" * 70)
    
    all_success = all(results.values())
    
    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {name}")
    
    print()
    
    if all_success:
        print("✓ All models downloaded successfully!")
        print()
        print("Verify your setup:")
        print("  python scripts/tools/verify_setup.py")
        print()
        print("Next steps:")
        print("  1. Add a test video to data/input/test_video.mp4")
        print("  2. Run: python scripts/processing/run_pipeline.py")
        return 0
    else:
        print("✗ Some downloads failed. Please check the errors above.")
        print()
        print("Manual download instructions in SETUP.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
