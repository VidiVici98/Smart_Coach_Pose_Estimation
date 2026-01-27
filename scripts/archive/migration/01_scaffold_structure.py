#!/usr/bin/env python3
"""
Scaffold New Repository Structure
Creates all necessary directories for the reorganized Smart Coach project.
This script is safe to run while other scripts are executing.
"""

import os
from pathlib import Path

# Base directory (parent of scripts/migration/)
BASE_DIR = Path(__file__).parent.parent.parent

# New directory structure to create
NEW_DIRECTORIES = [
    # Smart Coach core library
    "smart_coach/core",
    "smart_coach/models",
    "smart_coach/metrics",
    "smart_coach/visualization",
    "smart_coach/utils",
    "smart_coach/constants",
    
    # Scripts organization
    "scripts/processing",
    "scripts/tools",
    
    # Data hierarchy
    "data",
    "data/input",
    "data/output",
    "data/datasets",
    "data/datasets/gunmen",
    "data/models",
    
    # Configuration
    "config",
    
    # Tests
    "tests",
    
    # Third-party dependencies
    "third_party",
]

# __init__.py files to create
INIT_FILES = [
    "smart_coach/__init__.py",
    "smart_coach/core/__init__.py",
    "smart_coach/models/__init__.py",
    "smart_coach/metrics/__init__.py",
    "smart_coach/visualization/__init__.py",
    "smart_coach/utils/__init__.py",
    "smart_coach/constants/__init__.py",
    "tests/__init__.py",
]

def create_directories():
    """Create all new directories."""
    print("Creating new directory structure...")
    created_count = 0
    skipped_count = 0
    
    for dir_path in NEW_DIRECTORIES:
        full_path = BASE_DIR / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {dir_path}")
            created_count += 1
        else:
            print(f"⊘ Exists:  {dir_path}")
            skipped_count += 1
    
    print(f"\nDirectories: {created_count} created, {skipped_count} already existed")
    return created_count

def create_init_files():
    """Create __init__.py files for Python packages."""
    print("\nCreating __init__.py files...")
    created_count = 0
    skipped_count = 0
    
    for init_file in INIT_FILES:
        full_path = BASE_DIR / init_file
        if not full_path.exists():
            with open(full_path, 'w') as f:
                # Add docstring based on module
                module_name = init_file.split('/')[-2]
                f.write(f'"""{module_name.capitalize()} module for Smart Coach."""\n')
            print(f"✓ Created: {init_file}")
            created_count += 1
        else:
            print(f"⊘ Exists:  {init_file}")
            skipped_count += 1
    
    print(f"\nInit files: {created_count} created, {skipped_count} already existed")
    return created_count

def create_placeholder_readme():
    """Create placeholder README in key directories."""
    print("\nCreating placeholder README files...")
    
    readmes = {
        "data/README.md": """# Data Directory

This directory contains all data files for the Smart Coach project.

- `input/` - Input videos for processing
- `output/` - Processed results (videos + CSV analytics)
- `datasets/` - Training datasets for model fine-tuning
- `models/` - Pre-trained model weights

**Note:** Large files should be gitignored.
""",
        "config/README.md": """# Configuration Files

YAML and JSON configuration files for various pipelines and datasets.
""",
        "tests/README.md": """# Tests

Unit and integration tests for Smart Coach components.

Run tests with:
```bash
pytest tests/
```
""",
        "third_party/README.md": """# Third-Party Dependencies

External dependencies and submodules that are bundled with the project.

- `detectron2/` - Facebook's Detectron2 for Mask R-CNN
""",
    }
    
    created_count = 0
    for readme_path, content in readmes.items():
        full_path = BASE_DIR / readme_path
        if not full_path.exists():
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"✓ Created: {readme_path}")
            created_count += 1
    
    print(f"\nREADME files: {created_count} created")
    return created_count

def main():
    """Main execution."""
    print("="*60)
    print("Smart Coach Repository Structure Scaffolding")
    print("="*60)
    print(f"\nBase directory: {BASE_DIR}")
    print("\nThis script will create new directories without moving any files.")
    print("Your current scripts will continue running unaffected.\n")
    
    total_created = 0
    total_created += create_directories()
    total_created += create_init_files()
    total_created += create_placeholder_readme()
    
    print("\n" + "="*60)
    print(f"Scaffolding complete! {total_created} items created.")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the NEW_STRUCTURE.md file")
    print("2. When ready, run: python scripts/migration/02_migrate_files.py")
    print("3. Then run: python scripts/migration/03_update_references.py")
    print("4. Test everything works")
    print("5. Clean up old files")

if __name__ == "__main__":
    main()
