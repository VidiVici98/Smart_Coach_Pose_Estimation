#!/usr/bin/env python3
"""
Comprehensive diagnostic and fix script for Smart Coach pipeline.
Checks all requirements and attempts to auto-fix issues.
"""

import sys
import os
from pathlib import Path
import subprocess

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_python():
    """Check Python version."""
    print("\n[1/7] Checking Python version...")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 10:
        print("  ✓ Python version is compatible")
        return True
    else:
        print("  ✗ Python 3.10+ required")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def check_packages():
    """Check required Python packages."""
    print("\n[2/7] Checking Python packages...")
    
    packages = {
        "torch": "torch",
        "torchvision": "torchvision",
        "opencv-python": "cv2",
        "numpy": "numpy",
        "mediapipe": "mediapipe",
        "ultralytics": "ultralytics",
        "pandas": "pandas",
        "scipy": "scipy"
    }
    
    missing = []
    for pkg, import_name in packages.items():
        if check_package(pkg, import_name):
            print(f"  ✓ {pkg}")
        else:
            print(f"  ✗ {pkg} (missing)")
            missing.append(pkg)
    
    if missing:
        print(f"\n  Found {len(missing)} missing packages")
        return False, missing
    else:
        print("\n  ✓ All packages installed")
        return True, []

def install_packages(packages):
    """Install missing packages."""
    print("\n  Attempting to install missing packages...")
    try:
        cmd = [sys.executable, "-m", "pip", "install"] + packages
        print(f"  Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("  ✓ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Installation failed: {e}")
        return False

def check_models():
    """Check if required model files exist."""
    print("\n[3/7] Checking model files...")
    
    models_dir = Path("data/models")
    required_models = {
        "yolov8m-pose.pt": "YOLOv8 Pose Model",
        "yolov8n-face.pt": "YOLOv8 Face Model",
        "hand_landmarker.task": "MediaPipe Hand Landmarker"
    }
    
    missing = []
    for filename, description in required_models.items():
        filepath = models_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  ✓ {description} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ {description} (missing)")
            missing.append(filename)
    
    if missing:
        print(f"\n  Found {len(missing)} missing models")
        return False, missing
    else:
        print("\n  ✓ All models present")
        return True, []

def download_models():
    """Download missing models."""
    print("\n  Attempting to download models...")
    try:
        script_path = Path("scripts/tools/download_models.py")
        if script_path.exists():
            print(f"  Running: python {script_path}")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                check=False,
                capture_output=False
            )
            if result.returncode == 0:
                print("  ✓ Models downloaded successfully")
                return True
            else:
                print(f"  ⚠ Download script returned code {result.returncode}")
                print("    You may need to download models manually")
                return False
        else:
            print(f"  ✗ Download script not found: {script_path}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def check_test_video():
    """Check if test video exists."""
    print("\n[4/7] Checking test video...")
    
    video_path = Path("data/input/test_video.mp4")
    if video_path.exists():
        size_mb = video_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Test video found ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ✗ Test video not found: {video_path}")
        print("    You need to provide a test video:")
        print(f"    cp /path/to/your/video.mp4 {video_path}")
        return False

def check_output_dir():
    """Check and create output directory."""
    print("\n[5/7] Checking output directory...")
    
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ Output directory ready: {output_dir}")
    return True

def check_imports():
    """Try importing main pipeline script to check for import errors."""
    print("\n[6/7] Checking pipeline script imports...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        # Suppress NNPACK warnings
        os.environ["PYTORCH_NO_NNPACK"] = "1"
        os.environ["TORCH_CPP_LOG_LEVEL"] = "ERROR"
        
        print("  Testing imports...")
        import cv2
        print("    ✓ cv2")
        import torch
        print("    ✓ torch")
        import numpy
        print("    ✓ numpy")
        import mediapipe
        print("    ✓ mediapipe")
        from ultralytics import YOLO
        print("    ✓ ultralytics.YOLO")
        from torchvision.models.detection import maskrcnn_resnet50_fpn
        print("    ✓ torchvision.maskrcnn")
        
        print("\n  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"\n  ✗ Import error: {e}")
        return False

def run_pipeline_test():
    """Attempt to run the pipeline."""
    print("\n[7/7] Testing pipeline execution...")
    
    script_path = Path("scripts/processing/run_pipeline.py")
    if not script_path.exists():
        print(f"  ✗ Pipeline script not found: {script_path}")
        return False
    
    print(f"  Running: python {script_path}")
    print("  (This may take a few minutes...)\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=False,
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n  ✓ Pipeline executed successfully!")
            return True
        else:
            print(f"\n  ⚠ Pipeline returned code {result.returncode}")
            return False
    except Exception as e:
        print(f"\n  ✗ Error running pipeline: {e}")
        return False

def main():
    """Main diagnostic and fix routine."""
    print_header("Smart Coach Pipeline Diagnostics")
    print("\nThis script will check your environment and attempt to fix issues.\n")
    
    # Change to repo root
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}\n")
    
    issues = []
    
    # Check Python
    if not check_python():
        issues.append("Python version incompatible")
        print("\n✗ Cannot proceed - Python 3.10+ required")
        return 1
    
    # Check packages
    packages_ok, missing_packages = check_packages()
    if not packages_ok:
        issues.append(f"Missing packages: {', '.join(missing_packages)}")
        print("\nAttempting to fix...")
        if install_packages(missing_packages):
            print("✓ Packages installed - recheck...")
            packages_ok, _ = check_packages()
        
        if not packages_ok:
            print("\n⚠ Some packages still missing - try manual install:")
            print(f"  pip install {' '.join(missing_packages)}")
    
    # Check models
    models_ok, missing_models = check_models()
    if not models_ok:
        issues.append(f"Missing models: {', '.join(missing_models)}")
        print("\nAttempting to fix...")
        if download_models():
            print("✓ Models downloaded - recheck...")
            models_ok, _ = check_models()
        
        if not models_ok:
            print("\n⚠ Some models still missing - see SETUP.md for manual download")
    
    # Check test video
    if not check_test_video():
        issues.append("Test video missing")
    
    # Check output directory
    check_output_dir()
    
    # Check imports
    if not check_imports():
        issues.append("Import errors detected")
    
    # Summary
    print_header("Diagnostic Summary")
    
    if not issues:
        print("\n✓ All checks passed! Ready to run pipeline.\n")
        
        # Offer to run pipeline
        response = input("Would you like to run the pipeline now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            run_pipeline_test()
        else:
            print("\nTo run manually:")
            print("  python scripts/processing/run_pipeline.py")
        
        return 0
    else:
        print("\n⚠ Issues detected:\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\nRefer to SETUP.md for manual setup instructions.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Download models: python scripts/tools/download_models.py")
        print("  - Add test video: cp /path/to/video.mp4 data/input/test_video.mp4")
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
