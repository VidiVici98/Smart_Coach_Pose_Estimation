# Repository Restructuring - Quick Reference

## ✅ What's Been Done (Safe - While Script Runs)

1. **Created new directory structure** ✓
   - `smart_coach/` package with submodules (core, models, metrics, visualization, utils, constants)
   - `scripts/processing/` and `scripts/tools/`
   - `data/` hierarchy (input, output, models, datasets)
   - `config/`, `tests/`, `third_party/`

2. **Created migration scripts** ✓
   - `00_visualize_structure.py` - Shows before/after comparison
   - `01_scaffold_structure.py` - Creates directories (DONE ✓)
   - `02_migrate_files.py` - Copies files to new locations
   - `03_update_references.py` - Updates import paths
   - `04_cleanup_old_files.py` - Removes old files (CAREFUL!)

3. **Created documentation** ✓
   - `NEW_STRUCTURE.md` - Detailed structure plan
   - `MIGRATION_GUIDE.md` - Step-by-step guide
   - `GITIGNORE_UPDATES.md` - .gitignore changes needed

## 🚀 What to Do Next (After Your Script Finishes)

### Step 1: Migrate Files (5 min)
```bash
python scripts/migration/02_migrate_files.py
```
- Copies files to new locations
- Originals remain intact
- Safe to run

### Step 2: Update References (2 min)
```bash
python scripts/migration/03_update_references.py
```
- Updates import paths in NEW files only
- Updates model/data paths
- Original files unchanged

### Step 3: Test Everything (5 min)
```bash
# Test main pipeline
python scripts/processing/run_pipeline.py

# Verify outputs
ls data/output/

# Check other scripts
python scripts/processing/pose_demo.py
```

### Step 4: Cleanup (1 min) ⚠️
**Only if tests pass!**
```bash
python scripts/migration/04_cleanup_old_files.py
```
Type "DELETE" to confirm removal of old files.

## 📁 File Location Changes

| Old Location | New Location |
|-------------|--------------|
| `scripts/yolo_pose_with_mediapipe_hands.py` | `scripts/processing/run_pipeline.py` |
| `scripts/pose_demo.py` | `scripts/processing/pose_demo.py` |
| `scripts/debug_gaze.py` | `scripts/processing/debug_gaze.py` |
| `smart_coach/pose_landmarks.py` | `smart_coach/constants/pose_landmarks.py` |
| `models/` | `data/models/` |
| `input/` | `data/input/` |
| `output/` | `data/output/` |
| `Training_Dataset/` | `data/datasets/training/` |
| `training_dataset.yaml` | `config/training_dataset.yaml` |
| `detectron2/` | `third_party/detectron2/` |

## 🔧 Automatic Changes

The migration scripts will automatically update:
- ✓ Import paths: `from smart_coach.pose_landmarks` → `from smart_coach.constants.pose_landmarks`
- ✓ Model paths: `models/` → `data/models/`
- ✓ Input paths: `input/` → `data/input/`
- ✓ Output paths: `output/` → `data/output/`
- ✓ Dataset paths in YAML configs

## 🎯 Benefits You'll Get

1. **Clear Organization**
   - Library code in `smart_coach/`
   - Scripts in `scripts/`
   - Data in `data/`
   - Configs in `config/`

2. **Scalability**
   - Easy to add new models, metrics, features
   - Modular structure for collaboration

3. **Professional**
   - Standard Python package layout
   - Ready for pip installation
   - Better for version control

4. **Maintainability**
   - Logic separated into focused modules
   - Easier testing and debugging

## ⏱️ Timeline

- **Now (while script runs)**: ✅ Structure created, scripts ready
- **After script finishes**: 
  - 5 min → Migrate files
  - 2 min → Update references
  - 5 min → Test
  - 1 min → Cleanup
- **Total**: ~15 minutes

## 🆘 Troubleshooting

**"Import errors after migration?"**
→ Run `03_update_references.py` again (idempotent)

**"Want to rollback?"**
→ Before cleanup: just delete new directories
→ After cleanup: restore from Git

**"Tests fail?"**
→ DON'T run cleanup script
→ Check paths in run_pipeline.py
→ Verify models copied correctly

## 📖 Full Documentation

- `NEW_STRUCTURE.md` - Complete structure overview
- `MIGRATION_GUIDE.md` - Detailed step-by-step guide
- `GITIGNORE_UPDATES.md` - Git ignore changes

## 🎬 Quick Commands

```bash
# Visualize changes
python scripts/migration/00_visualize_structure.py

# Run full migration (after script finishes)
python scripts/migration/02_migrate_files.py
python scripts/migration/03_update_references.py

# Test
python scripts/processing/run_pipeline.py

# Cleanup (careful!)
python scripts/migration/04_cleanup_old_files.py
```

---

**Current Status**: ✅ Ready to migrate once your script finishes!
**Risk Level**: 🟢 Low (copies, not moves - originals stay intact)
**Reversible**: ✅ Yes (until cleanup step)
