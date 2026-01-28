#!/usr/bin/env python3
"""
Repository Structure Visualizer
Shows before/after comparison of the repository structure.
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

def print_tree(directory, prefix="", max_depth=3, current_depth=0, ignore_dirs=None):
    """Print directory tree."""
    if ignore_dirs is None:
        ignore_dirs = {'__pycache__', '.git', 'mediapipe_env', '.pytest_cache', 'runs'}
    
    if current_depth >= max_depth:
        return
    
    try:
        items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        dirs = [item for item in items if item.is_dir() and item.name not in ignore_dirs]
        files = [item for item in items if item.is_file()]
        
        # Show first few files and directories
        for i, item in enumerate(dirs[:5] + files[:3]):
            is_last = (i == len(dirs[:5] + files[:3]) - 1)
            print(f"{prefix}{'└── ' if is_last else '├── '}{item.name}{'/' if item.is_dir() else ''}")
            
            if item.is_dir():
                extension = "    " if is_last else "│   "
                print_tree(item, prefix + extension, max_depth, current_depth + 1, ignore_dirs)
        
        if len(dirs) > 5:
            print(f"{prefix}    ... and {len(dirs) - 5} more directories")
        if len(files) > 3:
            print(f"{prefix}    ... and {len(files) - 3} more files")
            
    except PermissionError:
        pass

def show_old_structure():
    """Show relevant parts of OLD structure."""
    print("📁 OLD STRUCTURE (Key Components)")
    print("="*60)
    print("""
smart_coach_pose_estimation/
├── scripts/
│   ├── yolo_pose_with_mediapipe_hands.py  ⚠️ Monolithic
│   ├── pose_demo.py
│   └── debug_gaze.py
├── smart_coach/
│   └── pose_landmarks.py                   ⚠️ Flat structure
├── models/                                  ⚠️ At root
│   ├── yolov8m-pose.pt
│   ├── yolov8n-face.pt
│   └── hand_landmarker.task
├── input/                                   ⚠️ At root
├── output/                                  ⚠️ At root
├── Gunmen_Dataset/                          ⚠️ At root
├── detectron2/                              ⚠️ At root
└── gun_dataset.yaml                         ⚠️ At root

Issues:
• Flat structure - everything at root level
• No clear separation between library, scripts, and data
• Monolithic script mixing concerns
• Hard to scale and maintain
    """)

def show_new_structure():
    """Show NEW structure."""
    print("\n📁 NEW STRUCTURE (Organized)")
    print("="*60)
    print("""
smart_coach_pose_estimation/
├── smart_coach/                    ✅ Core library package
│   ├── core/                       ├─ Pipeline orchestration
│   ├── models/                     ├─ Model wrappers
│   ├── metrics/                    ├─ Metric calculations
│   ├── visualization/              ├─ Rendering
│   ├── utils/                      ├─ Utilities
│   └── constants/                  └─ Definitions (pose_landmarks)
│
├── scripts/                        ✅ Organized scripts
│   ├── processing/                 ├─ run_pipeline.py (main)
│   │   ├── run_pipeline.py         ├─ pose_demo.py
│   │   ├── pose_demo.py            └─ debug_gaze.py
│   │   └── debug_gaze.py
│   ├── tools/                      └─ Utility scripts
│   └── migration/                     (temporary)
│
├── data/                           ✅ All data consolidated
│   ├── input/                      ├─ Input videos
│   ├── output/                     ├─ Results
│   ├── models/                     ├─ Model weights
│   └── datasets/                   └─ Training data
│       └── gunmen/
│
├── config/                         ✅ Configs separated
│   └── gun_dataset.yaml
│
├── tests/                          ✅ Testing infrastructure
├── docs/                           ✅ Documentation
└── third_party/                    ✅ External deps isolated
    └── detectron2/

Benefits:
• Clear separation: library / scripts / data / config
• Modular structure - easy to extend
• Professional Python package layout
• Ready for pip installation (future)
• Better for collaboration
    """)

def show_migration_status():
    """Show migration status."""
    print("\n📊 MIGRATION STATUS")
    print("="*60)
    
    checks = [
        ("New directories created", BASE_DIR / "smart_coach" / "core"),
        ("Migration scripts ready", BASE_DIR / "scripts" / "migration" / "02_migrate_files.py"),
        ("Documentation complete", BASE_DIR / "MIGRATION_GUIDE.md"),
    ]
    
    for description, path in checks:
        status = "✅" if path.exists() else "❌"
        print(f"{status} {description}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Wait for current script to finish")
    print("2. Run: python scripts/migration/02_migrate_files.py")
    print("3. Run: python scripts/migration/03_update_references.py") 
    print("4. Test: python scripts/processing/run_pipeline.py")
    print("5. Cleanup: python scripts/migration/04_cleanup_old_files.py")

def show_file_mapping():
    """Show specific file migrations."""
    print("\n🔄 FILE MIGRATION MAP")
    print("="*60)
    
    mappings = [
        ("scripts/yolo_pose_with_mediapipe_hands.py", "scripts/processing/run_pipeline.py"),
        ("scripts/pose_demo.py", "scripts/processing/pose_demo.py"),
        ("scripts/debug_gaze.py", "scripts/processing/debug_gaze.py"),
        ("smart_coach/pose_landmarks.py", "smart_coach/constants/pose_landmarks.py"),
        ("models/*", "data/models/*"),
        ("input/*", "data/input/*"),
        ("output/*", "data/output/*"),
        ("Gunmen_Dataset/", "data/datasets/gunmen/"),
        ("gun_dataset.yaml", "config/gun_dataset.yaml"),
        ("detectron2/", "third_party/detectron2/"),
    ]
    
    print("FROM → TO")
    print("-" * 60)
    for old, new in mappings:
        print(f"{old:40} → {new}")

def main():
    """Main execution."""
    print("\n" + "="*60)
    print("Smart Coach Repository Structure Comparison")
    print("="*60)
    
    show_old_structure()
    show_new_structure()
    show_file_mapping()
    show_migration_status()
    
    print("\n" + "="*60)
    print("📖 For detailed guide, see: MIGRATION_GUIDE.md")
    print("📋 For structure details, see: NEW_STRUCTURE.md")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
