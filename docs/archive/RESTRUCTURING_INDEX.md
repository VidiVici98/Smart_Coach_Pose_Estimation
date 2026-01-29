# 🏗️ Smart Coach Repository Restructuring

## ✅ STATUS: Ready to Migrate

The groundwork is complete! New directory structure scaffolded, migration scripts ready, and documentation written.

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **[RESTRUCTURE_SUMMARY.md](RESTRUCTURE_SUMMARY.md)** | ⭐ **START HERE** - Quick reference with timeline |
| **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** | Detailed step-by-step guide |
| **[NEW_STRUCTURE.md](NEW_STRUCTURE.md)** | Complete structure documentation |
| **[GITIGNORE_UPDATES.md](GITIGNORE_UPDATES.md)** | Git ignore changes needed |

---

## 🛠️ Migration Tools

### Visual Tools
```bash
# See before/after comparison
python scripts/migration/00_visualize_structure.py

# Validate you're ready to migrate
python scripts/migration/00_validate_ready.py
```

### Migration Scripts
```bash
# 1. Scaffold structure (✅ DONE)
python scripts/migration/01_scaffold_structure.py

# 2. Copy files to new locations
python scripts/migration/02_migrate_files.py

# 3. Update import paths
python scripts/migration/03_update_references.py

# 4. Remove old files (CAREFUL!)
python scripts/migration/04_cleanup_old_files.py
```

### Automated Migration
```bash
# Run all steps with prompts
./scripts/migration/run_migration.sh
```

---

## 🎯 Quick Start (After Your Script Finishes)

### Option A: Automated (Recommended)
```bash
./scripts/migration/run_migration.sh
```
Walks you through each step with confirmations.

### Option B: Manual (Step-by-Step)
```bash
# Validate
python scripts/migration/00_validate_ready.py

# Migrate
python scripts/migration/02_migrate_files.py
python scripts/migration/03_update_references.py

# Test
python scripts/processing/run_pipeline.py

# Cleanup (if tests pass)
python scripts/migration/04_cleanup_old_files.py
```

---

## 📁 What Changes?

### Before → After

```
OLD:                                NEW:
scripts/                            scripts/
├── yolo_pose...py         →         ├── processing/
├── pose_demo.py                     │   ├── run_pipeline.py
└── debug_gaze.py                    │   ├── pose_demo.py
                                     │   └── debug_gaze.py
                                     └── tools/

smart_coach/                        smart_coach/
└── pose_landmarks.py      →         ├── core/
                                     ├── models/
                                     ├── metrics/
                                     ├── visualization/
                                     ├── utils/
                                     └── constants/
                                         └── pose_landmarks.py

models/                    →        data/
input/                              ├── models/
output/                             ├── input/
Gunmen_Dataset/                     ├── output/
detectron2/                         └── datasets/
training_dataset.yaml                        └── training/

                                    config/
                                    └── training_dataset.yaml

                                    third_party/
                                    └── detectron2/
```

---

## 🔄 What Gets Updated Automatically?

The migration scripts handle:
- ✅ Import paths: `from smart_coach.pose_landmarks` → `from smart_coach.constants.pose_landmarks`
- ✅ Model paths: `"models/"` → `"data/models/"`
- ✅ Input paths: `"input/"` → `"data/input/"`
- ✅ Output paths: `"output/"` → `"data/output/"`
- ✅ Config paths in YAML files
- ✅ Creates path management utilities

---

## ⚡ Key Features

### Safety First
- ✅ Copies files (doesn't move) until you confirm
- ✅ Originals stay intact until final cleanup
- ✅ Validation checks before migration
- ✅ Dry-run previews for cleanup

### Professional Structure
- ✅ Proper Python package layout
- ✅ Clear separation: library / scripts / data / config
- ✅ Modular and scalable
- ✅ Ready for pip installation (future)

### Developer Friendly
- ✅ Comprehensive documentation
- ✅ Automated migration option
- ✅ Step-by-step manual option
- ✅ Rollback instructions

---

## ⏱️ Time Estimate

| Phase | Time | Risk |
|-------|------|------|
| Scaffold | ✅ Done | None |
| Migrate files | 5 min | Low (copies only) |
| Update references | 2 min | None (new files only) |
| Testing | 5 min | None |
| Cleanup | 1 min | Medium (removes files) |
| **Total** | **~15 min** | **Low** |

---

## 🚨 Important Notes

1. **Your running script is safe** - Scaffold phase didn't touch any existing files
2. **Wait to migrate** - Let your current script finish first (30 min)
3. **Test before cleanup** - Verify new structure works before removing old files
4. **Originals preserved** - Migration copies files, originals stay until cleanup

---

## 🆘 Need Help?

### Common Questions

**Q: Can I run migration while my script is running?**
A: Scaffold is done (safe). Wait for script to finish before running `02_migrate_files.py`.

**Q: What if something breaks?**
A: Before cleanup: Delete new directories, start over. After cleanup: Restore from Git.

**Q: How do I rollback?**
A: See "Rollback Plan" in MIGRATION_GUIDE.md

**Q: Can I customize the structure?**
A: Yes! Edit the migration scripts before running them.

---

## 📈 Benefits You'll Get

1. **Immediate**
   - ✅ Clean, organized codebase
   - ✅ Clear file locations
   - ✅ Better collaboration

2. **Short-term**
   - ✅ Easier to add features
   - ✅ Simpler testing
   - ✅ Better documentation

3. **Long-term**
   - ✅ Scalable architecture
   - ✅ Professional structure
   - ✅ pip installable package
   - ✅ CI/CD ready

---

## 🎓 After Migration

### Recommended Next Steps

1. **Update .gitignore** (see GITIGNORE_UPDATES.md)
2. **Commit to version control**
3. **Break up monolithic scripts** into modules
4. **Add unit tests** in tests/
5. **Create setup.py** for pip installation
6. **Add CI/CD** for automated testing

---

## 📞 Support

All scripts include:
- ✅ Detailed logging
- ✅ Confirmation prompts
- ✅ Error handling
- ✅ Progress reporting

**Safe to run multiple times!**

---

## 🎉 Ready to Go!

When your script finishes:
```bash
# Quick start
./scripts/migration/run_migration.sh

# Or step-by-step
python scripts/migration/00_validate_ready.py
```

Good luck with your migration! 🚀
