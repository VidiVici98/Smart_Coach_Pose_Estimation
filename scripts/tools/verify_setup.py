#!/usr/bin/env python3
"""
Verification script to check if Smart Coach environment is set up correctly.
Run this after initial setup to ensure all dependencies and models are in place.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"Checking Python version... ", end="")
    if version.major == 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro}")
        print(f"  Warning: Python 3.10+ recommended, you have {version.major}.{version.minor}")
        return False

def check_virtual_env():
    """Check if running in a virtual environment."""
    print(f"Checking virtual environment... ", end="")
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        venv_path = sys.prefix
        print(f"✓ Active: {os.path.basename(venv_path)}")
        return True
    else:
        print("✗ No virtual environment detected")
        print("  Run: python3 -m venv mediapipe_env && source mediapipe_env/bin/activate")
        return False

def check_packages():
    """Check if required packages are installed."""
    required_packages = [
        'torch',
        'torchvision',
        'cv2',
        'numpy',
        'mediapipe',
        'ultralytics',
        'pandas',
        'scipy'
    ]
    
    print(f"Checking required packages...")
    all_installed = True
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
                print(f"  ✓ opencv-python ({cv2.__version__})")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print(f"  ✓ {package} ({version})")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            all_installed = False
    
    if not all_installed:
        print("\n  Install missing packages: pip install -r requirements.txt")
    
    return all_installed

def check_gpu():
    """Check if GPU is available."""
    print(f"Checking GPU availability... ", end="")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✓ GPU available: {gpu_name}")
            return True
        else:
            print("⚠ No GPU available (CPU only)")
            print("  This is okay but processing will be slower")
            return False
    except:
        print("⚠ Cannot check GPU (torch not installed)")
        return False

def check_model_files():
    """Check if required model files exist."""
    model_dir = Path("data/models")
    required_models = {
        "yolov8m-pose.pt": "YOLOv8 Pose Model",
        "yolov8n-face.pt": "YOLOv8 Face Model",
        "hand_landmarker.task": "MediaPipe Hand Landmarker"
    }
    
    print(f"Checking model files...")
    all_exist = True
    
    for filename, description in required_models.items():
        filepath = model_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  ✓ {filename} ({size_mb:.1f} MB) - {description}")
        else:
            print(f"  ✗ {filename} - NOT FOUND")
            print(f"     {description} missing")
            all_exist = False
    
    if not all_exist:
        print("\n  See SETUP.md Step 4 for model download instructions")
    
    return all_exist

def check_input_video():
    """Check if test video exists."""
    video_path = Path("data/input/test_video.mp4")
    print(f"Checking input video... ", end="")
    
    if video_path.exists():
        size_mb = video_path.stat().st_size / (1024 * 1024)
        print(f"✓ test_video.mp4 ({size_mb:.1f} MB)")
        return True
    else:
        print("✗ test_video.mp4 NOT FOUND")
        print("  Copy your video: cp your_video.mp4 data/input/test_video.mp4")
        print("  Or generate test: python scripts/tools/create_test_video.py")
        return False

def check_directories():
    """Check if required directories exist."""
    required_dirs = [
        "data/input",
        "data/output",
        "data/models"
    ]
    
    print(f"Checking directories... ", end="")
    all_exist = True
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"\n  ✗ {dir_path} - creating...")
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            all_exist = False
    
    if all_exist:
        print("✓ All directories exist")
    else:
        print("  Created missing directories")
    
    return True

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Smart Coach Setup Verification")
    print("=" * 60)
    print()
    
    # Change to repo root if script is run from scripts/tools/
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    os.chdir(repo_root)
    print(f"Repository root: {repo_root}\n")
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("Required Packages", check_packages),
        ("GPU Support", check_gpu),
        ("Model Files", check_model_files),
        ("Input Video", check_input_video),
        ("Directories", check_directories),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
            print()
        except Exception as e:
            print(f"✗ Error during {name} check: {e}\n")
            results[name] = False
    
    # Summary
    print("=" * 60)
    print("Setup Summary")
    print("=" * 60)
    
    critical_checks = ["Required Packages", "Model Files", "Directories"]
    critical_passed = all(results.get(check, False) for check in critical_checks)
    
    if critical_passed and results.get("Input Video", False):
        print("✓ Setup complete! You can run the pipeline:")
        print("  python scripts/processing/run_pipeline.py")
    elif critical_passed:
        print("⚠ Setup almost complete! Missing:")
        if not results.get("Input Video", False):
            print("  - Test video (see SETUP.md Step 5)")
    else:
        print("✗ Setup incomplete. Please fix the issues above.")
        print("  See SETUP.md for detailed instructions.")
    
    print()
    print("For full documentation, see:")
    print("  - SETUP.md (setup guide)")
    print("  - README.md (project overview)")
    print("  - docs/USAGE_GUIDE.md (usage details)")
    print("=" * 60)
    
    # Return exit code
    return 0 if critical_passed else 1

if __name__ == "__main__":
    sys.exit(main())
