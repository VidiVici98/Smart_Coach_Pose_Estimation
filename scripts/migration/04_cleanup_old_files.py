#!/usr/bin/env python3
"""
Cleanup Old Files (Post-Migration)
Removes original files after successful migration and testing.
USE WITH CAUTION - only run after verifying the new structure works!
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Files to remove (originals that have been migrated)
FILES_TO_REMOVE = [
    "scripts/yolo_pose_with_mediapipe_hands.py",
    "scripts/pose_demo.py",
    "scripts/debug_gaze.py",
    "smart_coach/pose_landmarks.py",
    "gun_dataset.yaml",
]

# Directories to remove (after contents are migrated)
DIRS_TO_REMOVE = [
    "models",
    "input",
    "output", 
    "Gunmen_Dataset",
    "detectron2",
]

def remove_file(file_path: Path, dry_run=True):
    """Remove a file."""
    if not file_path.exists():
        print(f"⊘ Already removed: {file_path.relative_to(BASE_DIR)}")
        return False
    
    if dry_run:
        print(f"[DRY RUN] Would remove: {file_path.relative_to(BASE_DIR)}")
        return True
    
    try:
        file_path.unlink()
        print(f"✓ Removed: {file_path.relative_to(BASE_DIR)}")
        return True
    except Exception as e:
        print(f"✗ Failed to remove {file_path.relative_to(BASE_DIR)}: {e}")
        return False

def remove_directory(dir_path: Path, dry_run=True):
    """Remove a directory and all its contents."""
    if not dir_path.exists():
        print(f"⊘ Already removed: {dir_path.relative_to(BASE_DIR)}")
        return False
    
    if dry_run:
        print(f"[DRY RUN] Would remove directory: {dir_path.relative_to(BASE_DIR)}")
        return True
    
    try:
        shutil.rmtree(dir_path)
        print(f"✓ Removed directory: {dir_path.relative_to(BASE_DIR)}")
        return True
    except Exception as e:
        print(f"✗ Failed to remove {dir_path.relative_to(BASE_DIR)}: {e}")
        return False

def verify_new_structure():
    """Verify that new structure exists before cleaning up."""
    print("\n" + "="*60)
    print("Verifying New Structure")
    print("="*60)
    
    required_paths = [
        "scripts/processing/run_pipeline.py",
        "scripts/processing/pose_demo.py",
        "scripts/processing/debug_gaze.py",
        "smart_coach/constants/pose_landmarks.py",
        "data/models/yolov8m-pose.pt",
        "data/models/yolov8n-face.pt",
        "data/models/hand_landmarker.task",
        "config/gun_dataset.yaml",
    ]
    
    all_exist = True
    for path_str in required_paths:
        path = BASE_DIR / path_str
        if path.exists():
            print(f"✓ {path_str}")
        else:
            print(f"✗ MISSING: {path_str}")
            all_exist = False
    
    return all_exist

def main():
    """Main execution."""
    print("="*60)
    print("Smart Coach Cleanup Script")
    print("="*60)
    print("\n⚠️  WARNING ⚠️")
    print("This script will DELETE original files after migration.")
    print("Only run this after thoroughly testing the new structure!\n")
    
    # First verify new structure exists
    if not verify_new_structure():
        print("\n" + "="*60)
        print("❌ CLEANUP ABORTED")
        print("="*60)
        print("\nNew structure is incomplete!")
        print("Please complete migration and verify before cleanup.")
        return
    
    print("\n" + "="*60)
    print("Ready to Clean Up")
    print("="*60)
    
    # Dry run first
    print("\nPerforming dry run...\n")
    
    print("Files to remove:")
    for file_rel_path in FILES_TO_REMOVE:
        remove_file(BASE_DIR / file_rel_path, dry_run=True)
    
    print("\nDirectories to remove:")
    for dir_rel_path in DIRS_TO_REMOVE:
        remove_directory(BASE_DIR / dir_rel_path, dry_run=True)
    
    # Confirm before actual deletion
    print("\n" + "="*60)
    response = input("\nProceed with ACTUAL deletion? Type 'DELETE' to confirm: ").strip()
    
    if response != "DELETE":
        print("\nCleanup cancelled. No files were deleted.")
        return
    
    # Actual deletion
    print("\n" + "="*60)
    print("Performing Cleanup")
    print("="*60)
    
    removed_count = 0
    
    print("\nRemoving files...")
    for file_rel_path in FILES_TO_REMOVE:
        if remove_file(BASE_DIR / file_rel_path, dry_run=False):
            removed_count += 1
    
    print("\nRemoving directories...")
    for dir_rel_path in DIRS_TO_REMOVE:
        if remove_directory(BASE_DIR / dir_rel_path, dry_run=False):
            removed_count += 1
    
    print("\n" + "="*60)
    print("Cleanup Complete")
    print("="*60)
    print(f"\n{removed_count} items removed")
    print("\nMigration is now complete!")
    print("Your repository has been successfully reorganized.")

if __name__ == "__main__":
    main()
