# Archived Migration Scripts - README

## Purpose

This directory contains the migration scripts that were used to restructure the Smart Coach Pose Estimation repository. These scripts have been archived for historical reference and documentation purposes.

## ⚠️ Important Note

**These scripts are archived and should NOT be executed.**

The migration has already been completed successfully. These scripts are preserved only for:
- Historical documentation
- Understanding the migration process
- Reference for future restructuring efforts

## Known Issues

Since these scripts were archived (moved from `scripts/migration/` to `scripts/archive/migration/`), they contain path calculations that assume their original location. **Do not run these scripts** - they would fail due to incorrect path references.

If you need to reference the migration logic, consult:
- `docs/MIGRATION_COMPLETE.md` - Migration completion report
- `docs/NEW_STRUCTURE.md` - Structure documentation
- `docs/REORGANIZATION_SUMMARY.md` - Reorganization summary

## Scripts Included

- `00_validate_ready.py` - Pre-migration validation
- `00_visualize_structure.py` - Structure visualization
- `01_scaffold_structure.py` - Directory creation
- `02_migrate_files.py` - File migration
- `03_update_references.py` - Import path updates
- `04_cleanup_old_files.py` - Old file cleanup
- `run_migration.sh` - Automated migration runner

## Migration Status

✅ **COMPLETE** - The repository structure has been successfully reorganized.

See `docs/REORGANIZATION_SUMMARY.md` for details about what was accomplished.

## Current Structure

For the current repository structure, see:
- `docs/REPOSITORY_STRUCTURE.md` - Comprehensive structure guide
- Root `README.md` - Quick structure overview
- `scripts/tools/verify_structure.py` - Structure validation tool
