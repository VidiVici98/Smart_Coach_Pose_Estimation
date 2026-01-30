#!/bin/bash
# Verify all screenshots are properly committed

echo "=========================================="
echo "Screenshot Verification Report"
echo "=========================================="
echo ""

# Count PNG files
PNG_COUNT=$(ls -1 *.png 2>/dev/null | wc -l)
echo "📁 Total PNG files in root: $PNG_COUNT"

# Check tracked files
TRACKED_COUNT=$(git ls-files "*.png" | wc -l)
echo "✓ PNG files tracked by git: $TRACKED_COUNT"

# Check untracked
UNTRACKED=$(git ls-files --others --exclude-standard "*.png" | wc -l)
echo "✗ Untracked PNG files: $UNTRACKED"

echo ""
echo "=========================================="
echo "Git Status Check"
echo "=========================================="
if git diff-index --quiet HEAD -- *.png 2>/dev/null; then
    echo "✅ All PNG files committed (no changes)"
else
    echo "⚠️  Some PNG files have uncommitted changes"
fi

echo ""
echo "=========================================="
echo ".gitignore Check"
echo "=========================================="
if grep -q "^\*.png" .gitignore 2>/dev/null; then
    echo "❌ WARNING: *.png is in .gitignore!"
else
    echo "✅ *.png is NOT in .gitignore (good)"
fi

if grep -q "^.*\.png" .gitignore 2>/dev/null; then
    echo "❌ WARNING: Pattern blocking .png files found in .gitignore"
else
    echo "✅ No pattern blocking .png files in .gitignore"
fi

echo ""
echo "=========================================="
echo "Sample Files Check"
echo "=========================================="
echo "Checking key screenshot files..."

KEY_FILES=(
    "improved_gaze_frame_120.png"
    "annotated_feature_demo_030.png"
    "feature_demo_frame_010.png"
    "complete_feature_showcase.png"
)

for file in "${KEY_FILES[@]}"; do
    if [ -f "$file" ]; then
        if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
            SIZE=$(ls -lh "$file" | awk '{print $5}')
            echo "  ✓ $file ($SIZE) - tracked"
        else
            echo "  ✗ $file - EXISTS but NOT tracked!"
        fi
    else
        echo "  ✗ $file - MISSING"
    fi
done

echo ""
echo "=========================================="
echo "Remote Sync Check"
echo "=========================================="
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"

# Check if branch exists on remote
if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
    echo "✓ Branch exists on remote"
    
    # Check if we're up to date
    git fetch origin "$BRANCH" 2>/dev/null
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")
    
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo "✅ Local and remote are in sync"
    else
        echo "⚠️  Local and remote are out of sync"
    fi
else
    echo "⚠️  Branch not found on remote"
fi

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
if [ $PNG_COUNT -eq $TRACKED_COUNT ] && [ $UNTRACKED -eq 0 ]; then
    echo "✅ All $PNG_COUNT PNG files are tracked and committed"
    echo "✅ Screenshots are ready for PR display"
else
    echo "⚠️  Issue detected:"
    echo "   Total: $PNG_COUNT, Tracked: $TRACKED_COUNT, Untracked: $UNTRACKED"
fi

echo ""
echo "Run 'git add *.png' to track any untracked PNG files"
echo "Run 'git commit' to commit any changes"
echo "Run 'git push' to sync with remote"
