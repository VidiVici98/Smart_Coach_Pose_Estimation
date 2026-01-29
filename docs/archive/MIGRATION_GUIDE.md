# Smart Coach Repository Migration Guide

## Overview
This guide walks you through reorganizing the Smart Coach repository into a professional, scalable structure.

## Why Reorganize?
1. **Separation of Concerns**: Clear boundaries between library code, scripts, and data
2. **Scalability**: Easier to add new models, metrics, and features
3. **Collaboration**: Multiple developers can work on different components
4. **Professional**: Follows Python packaging best practices
5. **Maintainability**: Logic is organized into focused modules

## Migration Process

### Phase 1: Scaffold (Safe - Run Anytime) ✅

Create the new directory structure without touching existing files:

```bash
# Run in a fresh terminal (won't interfere with running scripts)
python scripts/migration/01_scaffold_structure.py
```

This creates:
- New `smart_coach/` package structure (core, models, metrics, visualization, utils, constants)
- `data/` hierarchy (input, output, models, datasets)
- `scripts/processing/` and `scripts/tools/` directories
- `config/` directory
- `third_party/` for external dependencies
- All necessary `__init__.py` files

**Safe to run now** - creates directories only, no files moved.

---

### Phase 2: Migrate Files (Creates Copies) ⚠️

Copy files to their new locations (originals remain intact):

```bash
python scripts/migration/02_migrate_files.py
```

This script:
1. Prompts for confirmation
2. Copies scripts to `scripts/processing/`
3. Copies `pose_landmarks.py` to `smart_coach/constants/`
4. Optionally copies large directories (models, datasets, detectron2)
5. Leaves originals untouched for safety

**What gets copied:**
- Scripts → `scripts/processing/`
- `smart_coach/pose_landmarks.py` → `smart_coach/constants/pose_landmarks.py`
- `models/` → `data/models/`
- `input/` → `data/input/`
- `output/` → `data/output/`
- `Training_Dataset/` → `data/datasets/training/`
- `detectron2/` → `third_party/detectron2/`
- `training_dataset.yaml` → `config/training_dataset.yaml`

---

### Phase 3: Update References (Modifies New Files Only) 🔧

Update import statements and paths in the NEW file locations:

```bash
python scripts/migration/03_update_references.py
```

This automatically updates:
- Import paths: `from smart_coach.pose_landmarks` → `from smart_coach.constants.pose_landmarks`
- Model paths: `models/` → `data/models/`
- Input paths: `input/` → `data/input/`
- Output paths: `output/` → `data/output/`
- Dataset paths in YAML configs

Also creates `smart_coach/utils/paths.py` for centralized path management.

---

### Phase 4: Test Everything ✅

**Critical step** - verify the new structure works:

```bash
# Navigate to project root
cd /home/jon/Desktop/Smart_Coach_Pose_Estimation

# Activate your environment
source mediapipe_env/bin/activate

# Test the main pipeline
python scripts/processing/run_pipeline.py
```

**Verification checklist:**
- [ ] Pipeline runs without import errors
- [ ] Models load correctly from `data/models/`
- [ ] Input video found in `data/input/`
- [ ] Output generated in `data/output/`
- [ ] CSV analytics exported correctly
- [ ] No path-related errors

---

### Phase 5: Cleanup (IRREVERSIBLE) 🗑️

**Only run after successful testing!**

```bash
python scripts/migration/04_cleanup_old_files.py
```

This script:
1. Verifies new structure is complete
2. Shows dry run of what will be deleted
3. Requires typing "DELETE" to confirm
4. Removes original files and directories

**What gets deleted:**
- `scripts/yolo_pose_with_mediapipe_hands.py` (now `scripts/processing/run_pipeline.py`)
- `scripts/pose_demo.py` (now `scripts/processing/pose_demo.py`)
- `scripts/debug_gaze.py` (now `scripts/processing/debug_gaze.py`)
- Old `smart_coach/pose_landmarks.py` (now in `constants/`)
- `models/` directory (now `data/models/`)
- `input/` directory (now `data/input/`)
- `output/` directory (now `data/output/`)
- `Training_Dataset/` (now `data/datasets/training/`)
- `detectron2/` (now `third_party/detectron2/`)

---

## New Structure Reference

```
smart_coach_pose_estimation/
├── smart_coach/                    # Core library (pip installable)
│   ├── core/                       # Pipeline orchestration
│   ├── models/                     # Model wrappers
│   ├── metrics/                    # Metric calculations
│   ├── visualization/              # Rendering overlays
│   ├── utils/                      # Helper utilities
│   └── constants/                  # Enums and definitions
│
├── scripts/
│   ├── processing/                 # Main executable scripts
│   └── tools/                      # Utility scripts
│
├── data/                           # All data files (gitignored)
│   ├── input/                      # Videos to process
│   ├── output/                     # Results
│   ├── models/                     # Model weights
│   └── datasets/                   # Training data
│
├── config/                         # YAML configs
├── tests/                          # Unit tests
├── docs/                           # Documentation
└── third_party/                    # External dependencies
```

---

## Rollback Plan

If something goes wrong:

1. **Before cleanup**: Just delete the new directories, originals are intact
2. **After cleanup**: Restore from Git history or backup
3. **Import errors**: Check paths.py and verify all references updated

---

## Future Improvements

Once migration is complete:

1. **Break up monolithic script**: Extract components from `run_pipeline.py` into:
   - `smart_coach/core/pipeline.py`
   - `smart_coach/models/*.py` 
   - `smart_coach/metrics/*.py`

2. **Add setup.py**: Make smart_coach pip installable
3. **Write tests**: Add unit tests in `tests/`
4. **Update .gitignore**: Adjust for new structure
5. **CI/CD**: Set up automated testing

---

## Timeline for Your Use Case

Since your script is running for 30 minutes:

**Now (while script runs):**
- ✅ Run Phase 1 (scaffold) - completely safe
- ✅ Review NEW_STRUCTURE.md
- ✅ Read this migration guide

**After script finishes:**
- Run Phase 2 (migrate files)
- Run Phase 3 (update references)
- Test thoroughly (Phase 4)
- Clean up (Phase 5)

**Total time estimate**: 10-15 minutes once you start Phase 2

---

## Questions & Troubleshooting

### "Import errors after migration?"
Run `03_update_references.py` again, it's idempotent.

### "Want to migrate only some directories?"
Edit `02_migrate_files.py` and comment out entries in `DIRECTORY_MIGRATIONS`.

### "Need to customize paths?"
Edit `smart_coach/utils/paths.py` after running `03_update_references.py`.

### "Made a mistake?"
Before cleanup: delete new directories, start over.
After cleanup: restore from Git.

---

## Need Help?

All migration scripts include:
- Dry run previews
- Confirmation prompts  
- Detailed logging
- Error handling

Safe to run multiple times!
