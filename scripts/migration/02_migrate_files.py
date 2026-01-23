#!/usr/bin/env python3
"""
Migrate Files to New Structure
Copies (not moves) files to their new locations in the reorganized structure.
Creates copies so original files remain intact until you verify everything works.
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Migration map: (source, destination)
# Using copies instead of moves for safety
FILE_MIGRATIONS = [
    # Scripts
    ("scripts/yolo_pose_with_mediapipe_hands.py", "scripts/processing/run_pipeline.py"),
    ("scripts/pose_demo.py", "scripts/processing/pose_demo.py"),
    ("scripts/debug_gaze.py", "scripts/processing/debug_gaze.py"),
    
    # Smart coach modules
    ("smart_coach/pose_landmarks.py", "smart_coach/constants/pose_landmarks.py"),
]

DIRECTORY_MIGRATIONS = [
    # Models
    ("models", "data/models"),
    
    # Input/Output
    ("input", "data/input"),
    ("output", "data/output"),
    
    # Datasets
    ("Gunmen_Dataset", "data/datasets/gunmen"),
    
    # Third-party
    ("detectron2", "third_party/detectron2"),
]

CONFIG_MIGRATIONS = [
    ("gun_dataset.yaml", "config/gun_dataset.yaml"),
]

def copy_file(src, dst, force=False):
    """Copy a single file with error handling."""
    src_path = BASE_DIR / src
    dst_path = BASE_DIR / dst
    
    if not src_path.exists():
        print(f"⚠ Source not found: {src}")
        return False
    
    if dst_path.exists() and not force:
        print(f"⊘ Already exists: {dst}")
        return False
    
    try:
        # Create parent directory if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        print(f"✓ Copied: {src} → {dst}")
        return True
    except Exception as e:
        print(f"✗ Failed: {src} → {dst}")
        print(f"  Error: {e}")
        return False

def copy_directory(src, dst, force=False):
    """Copy an entire directory tree."""
    src_path = BASE_DIR / src
    dst_path = BASE_DIR / dst
    
    if not src_path.exists():
        print(f"⚠ Source not found: {src}")
        return False
    
    if dst_path.exists() and not force:
        print(f"⊘ Already exists: {dst}")
        return False
    
    try:
        if dst_path.exists():
            shutil.rmtree(dst_path)
        shutil.copytree(src_path, dst_path)
        print(f"✓ Copied directory: {src} → {dst}")
        return True
    except Exception as e:
        print(f"✗ Failed: {src} → {dst}")
        print(f"  Error: {e}")
        return False

def migrate_files(force=False):
    """Migrate individual files."""
    print("\n" + "="*60)
    print("Migrating Files")
    print("="*60)
    
    success_count = 0
    for src, dst in FILE_MIGRATIONS:
        if copy_file(src, dst, force):
            success_count += 1
    
    print(f"\nFiles migrated: {success_count}/{len(FILE_MIGRATIONS)}")
    return success_count

def migrate_directories(force=False):
    """Migrate entire directories."""
    print("\n" + "="*60)
    print("Migrating Directories")
    print("="*60)
    print("⚠ Warning: This will copy large directories (models, detectron2, etc.)")
    
    success_count = 0
    for src, dst in DIRECTORY_MIGRATIONS:
        if copy_directory(src, dst, force):
            success_count += 1
    
    print(f"\nDirectories migrated: {success_count}/{len(DIRECTORY_MIGRATIONS)}")
    return success_count

def migrate_configs(force=False):
    """Migrate configuration files."""
    print("\n" + "="*60)
    print("Migrating Configuration Files")
    print("="*60)
    
    success_count = 0
    for src, dst in CONFIG_MIGRATIONS:
        if copy_file(src, dst, force):
            success_count += 1
    
    print(f"\nConfig files migrated: {success_count}/{len(CONFIG_MIGRATIONS)}")
    return success_count

def verify_critical_files():
    """Verify critical files exist in new locations."""
    print("\n" + "="*60)
    print("Verifying Critical Files")
    print("="*60)
    
    critical_files = [
        "scripts/processing/run_pipeline.py",
        "smart_coach/constants/pose_landmarks.py",
        "data/models/yolov8m-pose.pt",
        "data/models/yolov8n-face.pt",
        "data/models/hand_landmarker.task",
    ]
    
    all_exist = True
    for file_path in critical_files:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            print(f"✓ Found: {file_path}")
        else:
            print(f"✗ Missing: {file_path}")
            all_exist = False
    
    return all_exist

def main():
    """Main execution."""
    print("="*60)
    print("Smart Coach File Migration")
    print("="*60)
    print(f"\nBase directory: {BASE_DIR}")
    print("\nThis script copies files to their new locations.")
    print("Original files remain untouched for safety.\n")
    
    response = input("Proceed with migration? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Migration cancelled.")
        return
    
    force = False
    if input("Overwrite existing files? (yes/no): ").strip().lower() in ['yes', 'y']:
        force = True
    
    total_success = 0
    total_success += migrate_files(force)
    total_success += migrate_configs(force)
    
    if input("\nMigrate large directories (models, datasets, detectron2)? (yes/no): ").strip().lower() in ['yes', 'y']:
        total_success += migrate_directories(force)
    else:
        print("\nSkipping directory migration. You can run this script again later.")
    
    print("\n" + "="*60)
    print("Verification")
    print("="*60)
    verify_critical_files()
    
    print("\n" + "="*60)
    print("Migration Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run: python scripts/migration/03_update_references.py")
    print("2. Test the new structure: python scripts/processing/run_pipeline.py")
    print("3. If everything works, remove old files")
    print("\nOriginal files are still in place and unchanged.")

if __name__ == "__main__":
    main()
