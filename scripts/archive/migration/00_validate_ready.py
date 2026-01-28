#!/usr/bin/env python3
"""
Pre-Migration Validator
Checks that everything is ready for migration.
Run this before starting the migration process.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

def check_file_exists(path, description):
    """Check if a file exists."""
    full_path = BASE_DIR / path
    if full_path.exists():
        size = full_path.stat().st_size if full_path.is_file() else "dir"
        print(f"  ✓ {description}: {path} ({size})")
        return True
    else:
        print(f"  ✗ MISSING: {description}: {path}")
        return False

def check_critical_files():
    """Check that all critical files exist before migration."""
    print("\n" + "="*60)
    print("Checking Critical Files")
    print("="*60)
    
    critical_files = [
        ("scripts/yolo_pose_with_mediapipe_hands.py", "Main pipeline script"),
        ("scripts/pose_demo.py", "Pose demo script"),
        ("scripts/debug_gaze.py", "Gaze debug script"),
        ("smart_coach/pose_landmarks.py", "Pose landmarks module"),
        ("models/yolov8m-pose.pt", "YOLOv8 pose model"),
        ("models/yolov8n-face.pt", "YOLOv8 face model"),
        ("models/hand_landmarker.task", "MediaPipe hand model"),
        ("gun_dataset.yaml", "Dataset config"),
    ]
    
    all_exist = True
    for path, desc in critical_files:
        if not check_file_exists(path, desc):
            all_exist = False
    
    return all_exist

def check_new_structure():
    """Check that new structure has been created."""
    print("\n" + "="*60)
    print("Checking New Structure")
    print("="*60)
    
    new_dirs = [
        "smart_coach/core",
        "smart_coach/models",
        "smart_coach/metrics",
        "smart_coach/constants",
        "scripts/processing",
        "data/input",
        "data/output",
        "data/models",
        "config",
    ]
    
    all_exist = True
    for dir_path in new_dirs:
        if check_file_exists(dir_path, f"Directory"):
            pass
        else:
            all_exist = False
    
    return all_exist

def check_migration_scripts():
    """Check that migration scripts exist."""
    print("\n" + "="*60)
    print("Checking Migration Scripts")
    print("="*60)
    
    scripts = [
        "scripts/migration/02_migrate_files.py",
        "scripts/migration/03_update_references.py",
        "scripts/migration/04_cleanup_old_files.py",
    ]
    
    all_exist = True
    for script in scripts:
        if not check_file_exists(script, "Migration script"):
            all_exist = False
    
    return all_exist

def check_disk_space():
    """Check available disk space."""
    print("\n" + "="*60)
    print("Checking Disk Space")
    print("="*60)
    
    try:
        stat = os.statvfs(BASE_DIR)
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        print(f"  ℹ Available space: {free_gb:.2f} GB")
        
        # Rough estimate: models + datasets can be several GB
        if free_gb < 5:
            print(f"  ⚠ Warning: Low disk space. Migration copies files.")
            return False
        else:
            print(f"  ✓ Sufficient space for migration")
            return True
    except:
        print(f"  ⚠ Could not check disk space")
        return True

def check_python_version():
    """Check Python version."""
    print("\n" + "="*60)
    print("Checking Python Environment")
    print("="*60)
    
    import sys
    version = sys.version_info
    print(f"  ℹ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print(f"  ✓ Python version OK")
        return True
    else:
        print(f"  ✗ Python 3.7+ required")
        return False

def check_no_running_scripts():
    """Remind user to check for running scripts."""
    print("\n" + "="*60)
    print("Running Scripts Check")
    print("="*60)
    
    print("  ⚠ IMPORTANT: Make sure your current processing script has finished!")
    print("  ℹ Migration will copy large files (models, datasets)")
    print("  ℹ This is safe but may be slow if script is using resources")
    
    response = input("\n  Has your script finished running? (yes/no): ").strip().lower()
    return response in ['yes', 'y']

def estimate_migration_size():
    """Estimate total size of files to be migrated."""
    print("\n" + "="*60)
    print("Estimating Migration Size")
    print("="*60)
    
    dirs_to_copy = ["models", "Gunmen_Dataset", "detectron2", "input", "output"]
    total_size = 0
    
    for dir_name in dirs_to_copy:
        dir_path = BASE_DIR / dir_name
        if dir_path.exists():
            size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
            size_mb = size / (1024**2)
            print(f"  ℹ {dir_name}: {size_mb:.1f} MB")
            total_size += size
    
    total_gb = total_size / (1024**3)
    print(f"\n  ℹ Total to copy: ~{total_gb:.2f} GB")
    print(f"  ℹ Time estimate: ~{int(total_gb * 2)} minutes (2min/GB)")
    
    return True

def main():
    """Main validation."""
    print("="*60)
    print("Smart Coach Pre-Migration Validator")
    print("="*60)
    print(f"\nBase directory: {BASE_DIR}\n")
    
    checks = []
    
    # Run all checks
    checks.append(("Python version", check_python_version()))
    checks.append(("Critical files", check_critical_files()))
    checks.append(("New structure", check_new_structure()))
    checks.append(("Migration scripts", check_migration_scripts()))
    checks.append(("Disk space", check_disk_space()))
    
    estimate_migration_size()
    
    # Summary
    print("\n" + "="*60)
    print("Validation Summary")
    print("="*60)
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
    
    all_passed = all(result for _, result in checks)
    
    if all_passed:
        print("\n✅ All checks passed! Ready to migrate.")
        if check_no_running_scripts():
            print("\n🚀 Next step:")
            print("   python scripts/migration/02_migrate_files.py")
        else:
            print("\n⏳ Wait for your script to finish, then run:")
            print("   python scripts/migration/02_migrate_files.py")
    else:
        print("\n❌ Some checks failed. Please resolve issues before migration.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
