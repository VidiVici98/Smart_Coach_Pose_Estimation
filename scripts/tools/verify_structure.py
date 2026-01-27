#!/usr/bin/env python3
"""
Verification script to check repository structure is correct.
"""
import os
import sys
from pathlib import Path

def check_structure():
    """Verify the repository structure is correct."""
    
    repo_root = Path(__file__).parent.parent.parent
    print(f"Checking repository structure at: {repo_root}")
    print()
    
    required_dirs = [
        "smart_coach",
        "smart_coach/constants",
        "smart_coach/core",
        "smart_coach/models",
        "smart_coach/metrics",
        "smart_coach/visualization",
        "smart_coach/utils",
        "scripts",
        "scripts/processing",
        "scripts/tools",
        "scripts/archive",
        "data",
        "data/input",
        "data/output",
        "data/models",
        "data/datasets",
        "config",
        "tests",
        "docs",
        "third_party",
    ]
    
    required_files = [
        "README.md",
        "CONTRIBUTING.md",
        "LICENSE",
        ".gitignore",
        "smart_coach/__init__.py",
        "smart_coach/constants/__init__.py",
        "smart_coach/constants/pose_landmarks.py",
        "scripts/processing/run_pipeline.py",
        "scripts/processing/pose_demo.py",
        "scripts/processing/debug_gaze.py",
        "config/training_dataset.yaml",
        "docs/REPOSITORY_STRUCTURE.md",
        "docs/metrics_reference.md",
    ]
    
    all_good = True
    
    # Check directories
    print("Checking required directories...")
    for dir_path in required_dirs:
        full_path = repo_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - MISSING!")
            all_good = False
    
    print()
    
    # Check files
    print("Checking required files...")
    for file_path in required_files:
        full_path = repo_root / file_path
        if full_path.exists() and full_path.is_file():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING!")
            all_good = False
    
    print()
    
    # Check for old structure artifacts
    print("Checking for old structure artifacts (should not exist)...")
    old_artifacts = [
        "detectron2",
        "migration_report.txt",
        "scripts/migration",
        "MIGRATION_COMPLETE.md",
        "NEW_STRUCTURE.md",
        "RESTRUCTURING_INDEX.md",
    ]
    
    for artifact in old_artifacts:
        full_path = repo_root / artifact
        if not full_path.exists():
            print(f"  ✓ {artifact} - correctly removed/moved")
        else:
            print(f"  ⚠ {artifact} - still exists (should be removed/moved)")
            # This is a warning, not an error
    
    print()
    
    # Check paths in run_pipeline.py
    print("Checking paths in run_pipeline.py...")
    pipeline_path = repo_root / "scripts/processing/run_pipeline.py"
    if pipeline_path.exists():
        with open(pipeline_path, 'r') as f:
            content = f.read()
            
        expected_paths = [
            'data/input/',
            'data/output/',
            'data/models/',
        ]
        
        for path in expected_paths:
            if path in content:
                print(f"  ✓ Uses '{path}' path")
            else:
                print(f"  ✗ Missing '{path}' path")
                all_good = False
    else:
        print(f"  ✗ run_pipeline.py not found!")
        all_good = False
    
    print()
    
    # Summary
    if all_good:
        print("=" * 60)
        print("✅ Repository structure verification PASSED!")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("❌ Repository structure verification FAILED!")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(check_structure())
