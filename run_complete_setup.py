#!/usr/bin/env python3
"""
Complete setup and run script - executes all steps inline
Run this with: python3 run_complete_setup.py
"""

import sys
import os
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def run_command(cmd, description):
    """Run a shell command and return success status."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✓ {description} - Success\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} - Failed (exit code {e.returncode})\n")
        return False

# Change to repo root
script_dir = Path(__file__).parent
os.chdir(script_dir)
print(f"Working directory: {script_dir}\n")

print_header("STEP 1: CHECK PYTHON")
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
if sys.version_info < (3, 10):
    print("✗ Need Python 3.10+")
    sys.exit(1)
print("✓ Python version OK")

print_header("STEP 2: INSTALL PACKAGES")
print("Installing requirements (this may take a minute)...")
success = run_command(
    f"{sys.executable} -m pip install -q -r requirements.txt",
    "Package installation"
)
if not success:
    print("⚠ Continuing despite package errors...\n")

print_header("STEP 3: CHECK EXISTING MODELS")
models_dir = Path("data/models")
models_dir.mkdir(parents=True, exist_ok=True)

required_models = {
    "yolov8m-pose.pt": "YOLO Pose",
    "yolov8n-face.pt": "YOLO Face",
    "hand_landmarker.task": "MediaPipe Hands"
}

missing = []
for filename, desc in required_models.items():
    filepath = models_dir / filename
    if filepath.exists():
        size = filepath.stat().st_size / (1024*1024)
        print(f"✓ {desc:20} {size:6.1f} MB")
    else:
        print(f"✗ {desc:20} MISSING")
        missing.append(filename)

if not missing:
    print("\n✓ All models present, skipping download")
else:
    print(f"\n⚠ Need to download {len(missing)} model(s)")
    
    print_header("STEP 4: DOWNLOAD YOLO MODELS")
    
    try:
        print("Importing ultralytics...")
        from ultralytics import YOLO
        import shutil
        
        print("✓ ultralytics imported\n")
        
        # Download pose model if missing
        if "yolov8m-pose.pt" in missing:
            print("Downloading yolov8m-pose.pt (~52 MB)...")
            pose_model = YOLO('yolov8m-pose.pt')
            print("✓ Downloaded to cache\n")
        
        # Download face model if missing
        if "yolov8n-face.pt" in missing:
            print("Downloading yolov8n.pt (used as face model, ~6 MB)...")
            face_model = YOLO('yolov8n.pt')
            print("✓ Downloaded to cache\n")
        
        # Copy from cache to data/models/
        if missing:
            print("Copying models from cache to data/models/...")
            cache_dir = Path.home() / ".cache" / "ultralytics"
            
            if "yolov8m-pose.pt" in missing:
                for f in cache_dir.rglob("yolov8m-pose.pt"):
                    dest = models_dir / "yolov8m-pose.pt"
                    shutil.copy(f, dest)
                    size = dest.stat().st_size / (1024*1024)
                    print(f"  ✓ Copied yolov8m-pose.pt ({size:.1f} MB)")
                    break
            
            if "yolov8n-face.pt" in missing:
                for f in cache_dir.rglob("yolov8n.pt"):
                    dest = models_dir / "yolov8n-face.pt"
                    shutil.copy(f, dest)
                    size = dest.stat().st_size / (1024*1024)
                    print(f"  ✓ Copied yolov8n-face.pt ({size:.1f} MB)")
                    break
            
            print("\n✓ Models downloaded and copied successfully!")
    
    except Exception as e:
        print(f"✗ Error during download: {e}")
        print("\nTry manual download:")
        print("  cd data/models")
        print("  wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m-pose.pt")
        print("  wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt")
        print("  mv yolov8n.pt yolov8n-face.pt")
        sys.exit(1)

print_header("STEP 5: FINAL VERIFICATION")

# Check all required files
all_present = True
required_files = [
    "data/models/yolov8m-pose.pt",
    "data/models/yolov8n-face.pt",
    "data/models/hand_landmarker.task",
    "data/input/test_video.mp4"
]

for filepath in required_files:
    p = Path(filepath)
    if p.exists():
        size = p.stat().st_size / (1024*1024)
        print(f"✓ {filepath:45} {size:6.1f} MB")
    else:
        print(f"✗ {filepath:45} MISSING")
        all_present = False

if not all_present:
    print("\n✗ Setup incomplete - some files missing")
    sys.exit(1)

print("\n✓ All required files present!")

print_header("STEP 6: RUN PIPELINE")

print("Ready to process video!")
print("Output will be saved to:")
print("  - data/output/output_full.mp4 (annotated video)")
print("  - data/output/analytics.csv (frame metrics)")
print("")

response = input("Run pipeline now? (Y/n): ").strip().lower()
if response in ['', 'y', 'yes']:
    print("\nStarting pipeline...")
    print("This may take several minutes depending on video length.\n")
    print("="*70)
    
    # Run the pipeline
    result = subprocess.run(
        [sys.executable, "scripts/processing/run_pipeline.py"],
        check=False
    )
    
    print("="*70)
    
    if result.returncode == 0:
        print("\n✓ PIPELINE COMPLETED SUCCESSFULLY!")
        
        # Check output
        print("\nOutput files:")
        output_video = Path("data/output/output_full.mp4")
        output_csv = Path("data/output/analytics.csv")
        
        if output_video.exists():
            size = output_video.stat().st_size / (1024*1024)
            print(f"  ✓ Video: {output_video} ({size:.1f} MB)")
        
        if output_csv.exists():
            import csv
            with open(output_csv, 'r') as f:
                reader = csv.reader(f)
                rows = sum(1 for _ in reader) - 1  # subtract header
            print(f"  ✓ CSV: {output_csv} ({rows} frames)")
        
        print("\n" + "="*70)
        print("ALL DONE! 🎉")
        print("="*70)
    else:
        print(f"\n✗ Pipeline failed with exit code {result.returncode}")
        print("Check error messages above")
        sys.exit(1)
else:
    print("\nSkipped pipeline execution.")
    print("Run manually with: python3 scripts/processing/run_pipeline.py")
    sys.exit(0)
