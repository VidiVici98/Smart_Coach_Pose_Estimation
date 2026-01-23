#!/bin/bash
# Quick Migration Runner
# Runs all migration steps in sequence with user confirmation

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/../.."

echo "======================================================================"
echo "Smart Coach Repository Restructuring - Automated Migration"
echo "======================================================================"
echo ""
echo "This script will run all migration steps in sequence."
echo "You'll be prompted before each step."
echo ""
echo "Steps:"
echo "  1. Validate readiness"
echo "  2. Migrate files (copy to new locations)"
echo "  3. Update references (fix import paths)"
echo "  4. Cleanup (remove old files - OPTIONAL)"
echo ""
read -p "Press ENTER to start or Ctrl+C to cancel..."

echo ""
echo "======================================================================"
echo "Step 1: Validation"
echo "======================================================================"
python3 scripts/migration/00_validate_ready.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Validation failed. Please fix issues before continuing."
    exit 1
fi

echo ""
read -p "Continue with file migration? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration cancelled."
    exit 0
fi

echo ""
echo "======================================================================"
echo "Step 2: File Migration"
echo "======================================================================"
python3 scripts/migration/02_migrate_files.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ File migration failed."
    exit 1
fi

echo ""
read -p "Continue with reference updates? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping after file migration."
    exit 0
fi

echo ""
echo "======================================================================"
echo "Step 3: Update References"
echo "======================================================================"
python3 scripts/migration/03_update_references.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Reference update failed."
    exit 1
fi

echo ""
echo "======================================================================"
echo "Step 4: Testing"
echo "======================================================================"
echo ""
echo "Please test the new structure before cleanup:"
echo "  python scripts/processing/run_pipeline.py"
echo ""
echo "Verify:"
echo "  - No import errors"
echo "  - Models load correctly"
echo "  - Output generated successfully"
echo ""
read -p "Have you tested and verified everything works? (y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "⏸️  Migration paused."
    echo "Test your setup, then run cleanup manually:"
    echo "  python scripts/migration/04_cleanup_old_files.py"
    exit 0
fi

echo ""
read -p "Proceed with cleanup (removes old files)? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "✅ Migration complete (without cleanup)."
    echo "Old files remain in place."
    echo "Run cleanup later: python scripts/migration/04_cleanup_old_files.py"
    exit 0
fi

echo ""
echo "======================================================================"
echo "Step 5: Cleanup"
echo "======================================================================"
python3 scripts/migration/04_cleanup_old_files.py

echo ""
echo "======================================================================"
echo "Migration Complete! 🎉"
echo "======================================================================"
echo ""
echo "Your repository has been successfully reorganized!"
echo ""
echo "Next steps:"
echo "  1. Update .gitignore (see GITIGNORE_UPDATES.md)"
echo "  2. Commit changes to version control"
echo "  3. Consider breaking up monolithic scripts into modules"
echo ""
