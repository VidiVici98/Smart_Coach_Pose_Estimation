#!/usr/bin/env python3
"""
Robust Reference Updater

Features:
- Repo-wide scan for candidate references
- Safe AST-based updates for Python files (imports + string literals + simple os.path.join)
- YAML-aware updates (uses PyYAML if available, falls back to safe regex)
- Dry-run mode that prints diffs and a summary report
- --apply flag to write changes

Use:
  python scripts/migration/03_update_references.py --dry-run
  python scripts/migration/03_update_references.py --apply

This operates on the NEW locations (files copied by the migration step).
Backups are created as `.bak` for any file written.
"""

import argparse
import ast
import io
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    # ast.unparse is available in Python 3.9+
    from ast import unparse as ast_unparse
except Exception:
    ast_unparse = None

try:
    import yaml
    YAML_AVAILABLE = True
except Exception:
    YAML_AVAILABLE = False

BASE_DIR = Path(__file__).parent.parent.parent

# Patterns to replace for filesystem paths and datasets
PATH_REPLACEMENTS: Dict[str, str] = {
    "models/": "data/models/",
    "input/": "data/input/",
    "output/": "data/output/",
    "Gunmen_Dataset": "data/datasets/gunmen",
}

# Module import replacements
IMPORT_REPLACEMENTS: Dict[str, str] = {
    "smart_coach.pose_landmarks": "smart_coach.constants.pose_landmarks",
}

EXCLUDE_DIRS = {"__pycache__", "scripts/migration", "mediapipe_env", "third_party/detectron2"}


def is_excluded(path: Path) -> bool:
    s = str(path)
    for ex in EXCLUDE_DIRS:
        if ex in s:
            return True
    return False


def find_candidate_files() -> List[Path]:
    files = []
    for p in BASE_DIR.rglob("*"):
        if p.is_file():
            if is_excluded(p):
                continue
            if p.suffix in {".py", ".yaml", ".yml", ".txt", ".md"}:
                files.append(p)
    return files


def contains_token(text: str, tokens: List[str]) -> bool:
    return any(t in text for t in tokens)


class ReferenceTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.changed = False
        self.replacements_made: List[str] = []

    def _maybe_replace_module(self, modulename: str) -> str:
        if not modulename:
            return modulename
        for old, new in IMPORT_REPLACEMENTS.items():
            if modulename == old or modulename.startswith(old + '.'):
                self.changed = True
                self.replacements_made.append(f"module:{old}->{new}")
                return modulename.replace(old, new, 1)
        return modulename

    def visit_Import(self, node: ast.Import) -> ast.AST:
        for alias in node.names:
            newname = self._maybe_replace_module(alias.name)
            if newname != alias.name:
                alias.name = newname
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        # node.module can be None for relative imports
        if node.module:
            new_module = self._maybe_replace_module(node.module)
            node.module = new_module
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        # replace string literals that contain path tokens
        if isinstance(node.value, str):
            s = node.value
            for old, new in PATH_REPLACEMENTS.items():
                if old in s:
                    ns = s.replace(old, new)
                    self.changed = True
                    self.replacements_made.append(f"string:{s}->{ns}")
                    return ast.copy_location(ast.Constant(value=ns), node)
        return node

    # For older versions of ast, Str nodes might be used - handle generically
    def visit_Str(self, node: ast.Str) -> ast.AST:  # type: ignore
        return self.visit_Constant(node)  # type: ignore

    def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.AST:
        # f-strings: update literal pieces
        changed = False
        for idx, value in enumerate(node.values):
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                s = value.value
                for old, new in PATH_REPLACEMENTS.items():
                    if old in s:
                        ns = s.replace(old, new)
                        node.values[idx] = ast.copy_location(ast.Constant(value=ns), value)
                        changed = True
                        self.replacements_made.append(f"fstring:{s}->{ns}")
        if changed:
            self.changed = True
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        # Handle os.path.join literal args -> replace with a single literal when safe
        try:
            # Identify os.path.join and literal-only args
            if isinstance(node.func, ast.Attribute):
                attr = node.func
                if isinstance(attr.value, ast.Attribute) and getattr(attr.value, 'attr', '') == 'path' and getattr(attr.value.value, 'id', '') == 'os' and attr.attr == 'join':
                    literal_parts = []
                    all_literal = True
                    for a in node.args:
                        if isinstance(a, ast.Constant) and isinstance(a.value, str):
                            literal_parts.append(a.value)
                        else:
                            all_literal = False
                            break
                    if all_literal and literal_parts:
                        joined = os.path.join(*literal_parts)
                        for old, new in PATH_REPLACEMENTS.items():
                            if old in joined:
                                newjoined = joined.replace(old, new)
                                self.changed = True
                                self.replacements_made.append(f"join:{joined}->{newjoined}")
                                return ast.copy_location(ast.Constant(value=newjoined), node)
        except Exception:
            pass
        return self.generic_visit(node)


def transform_python_file(path: Path) -> Tuple[bool, str]:
    """Return (changed, report)."""
    try:
        text = path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"ERROR reading {path}: {e}"

    # Quick skip if file doesn't contain any tokens
    tokens = list(PATH_REPLACEMENTS.keys()) + list(IMPORT_REPLACEMENTS.keys())
    if not contains_token(text, tokens):
        return False, "No candidate tokens"

    try:
        tree = ast.parse(text)
    except Exception as e:
        return False, f"ERROR parsing AST: {e}"

    transformer = ReferenceTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)

    if not transformer.changed:
        return False, "No changes via AST"

    # Unparse AST to source
    if ast_unparse:
        try:
            new_source = ast_unparse(new_tree)
        except Exception as e:
            return False, f"ERROR unparsing AST: {e}"
    else:
        return False, "ast.unparse not available in this Python; cannot write AST-edits"

    # Format: keep a conservative newline at end
    if not new_source.endswith('\n'):
        new_source += '\n'

    # Produce a unified diff-like report
    import difflib
    old_lines = text.splitlines(keepends=True)
    new_lines = new_source.splitlines(keepends=True)
    diff = ''.join(difflib.unified_diff(old_lines, new_lines, fromfile=str(path), tofile=str(path) + ' (updated)'))
    report_lines = [f"AST changes: {', '.join(transformer.replacements_made)}", diff]
    return True, '\n'.join(report_lines)


def update_yaml_file(path: Path) -> Tuple[bool, str]:
    try:
        text = path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"ERROR reading {path}: {e}"

    tokens = list(PATH_REPLACEMENTS.keys())
    if not contains_token(text, tokens):
        return False, "No candidate tokens"

    if YAML_AVAILABLE:
        try:
            data = yaml.safe_load(text)
        except Exception as e:
            return False, f"ERROR parsing YAML: {e}"

        changed = False

        def walk(obj):
            nonlocal changed
            if isinstance(obj, dict):
                for k, v in obj.items():
                    obj[k] = walk(v)
                return obj
            elif isinstance(obj, list):
                return [walk(x) for x in obj]
            elif isinstance(obj, str):
                s = obj
                for old, new in PATH_REPLACEMENTS.items():
                    if old in s:
                        s = s.replace(old, new)
                        changed = True
                return s
            else:
                return obj

        new_data = walk(data)
        if not changed:
            return False, "No YAML replacements needed"

        try:
            new_text = yaml.safe_dump(new_data, sort_keys=False)
        except Exception as e:
            return False, f"ERROR dumping YAML: {e}"

        import difflib
        diff = ''.join(difflib.unified_diff(text.splitlines(keepends=True), new_text.splitlines(keepends=True), fromfile=str(path), tofile=str(path) + ' (updated)'))
        report = f"YAML changes in {path}\n" + diff
        return True, report
    else:
        # Fallback: simple text replacements
        new_text = text
        changed = False
        for old, new in PATH_REPLACEMENTS.items():
            if old in new_text:
                new_text = new_text.replace(old, new)
                changed = True
        if not changed:
            return False, "No YAML replacements needed (fallback)"
        import difflib
        diff = ''.join(difflib.unified_diff(text.splitlines(keepends=True), new_text.splitlines(keepends=True), fromfile=str(path), tofile=str(path) + ' (updated)'))
        report = f"YAML-text changes in {path}\n" + diff
        return True, report


def write_backup_and_apply(path: Path, new_content: str) -> None:
    bak = path.with_suffix(path.suffix + '.bak')
    if not bak.exists():
        path.rename(bak)
        bak.write_text(bak.read_text(encoding='utf-8'), encoding='utf-8')
        # restore original file to write updated content
        path.write_text(new_content, encoding='utf-8')
    else:
        # bak exists, just overwrite target
        path.write_text(new_content, encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Write changes (default is dry-run)')
    parser.add_argument('--report', type=str, default=None, help='Write report to file')
    args = parser.parse_args(argv)

    files = find_candidate_files()
    py_files = [p for p in files if p.suffix == '.py']
    yaml_files = [p for p in files if p.suffix in {'.yaml', '.yml'}]
    other_files = [p for p in files if p.suffix not in {'.py', '.yaml', '.yml'}]

    reports: List[Tuple[Path, str]] = []

    print(f"Scanning {len(py_files)} Python files and {len(yaml_files)} YAML files for replacements...")

    # Python files
    for p in py_files:
        changed, report = transform_python_file(p)
        if changed:
            reports.append((p, report))

    # YAML files
    for p in yaml_files:
        changed, report = update_yaml_file(p)
        if changed:
            reports.append((p, report))

    # For other files (md, txt), do conservative text replacement (dry-run only)
    tokens = list(PATH_REPLACEMENTS.keys()) + list(IMPORT_REPLACEMENTS.keys())
    for p in other_files:
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        if contains_token(text, tokens):
            new_text = text
            for old, new in PATH_REPLACEMENTS.items():
                new_text = new_text.replace(old, new)
            for old, new in IMPORT_REPLACEMENTS.items():
                new_text = new_text.replace(old, new)
            if new_text != text:
                import difflib
                diff = ''.join(difflib.unified_diff(text.splitlines(keepends=True), new_text.splitlines(keepends=True), fromfile=str(p), tofile=str(p) + ' (updated)'))
                reports.append((p, "TEXT changes:\n" + diff))

    # Print summary
    if not reports:
        print("No replacements found.")
        return 0

    print(f"\nProposed changes for {len(reports)} files:")
    for path, rep in reports:
        print(f"\n--- {path} ---\n")
        # Limit preview size to avoid flooding terminal
        snippet = '\n'.join(rep.splitlines()[:200])
        print(snippet)
        if len(rep.splitlines()) > 200:
            print('\n... (output truncated)')

    # Optionally write report to file
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            for path, rep in reports:
                f.write(f"--- {path} ---\n")
                f.write(rep)
                f.write("\n\n")
        print(f"\nReport written to {args.report}")

    if not args.apply:
        print('\nDry-run complete. No files modified. Run with --apply to write changes.')
        return 0

    # Apply changes: for Python and YAML we need to regenerate content to write
    for path, rep in reports:
        if path.suffix == '.py':
            # Re-run transform to get new source (we know AST unparse exists because transform succeeded earlier)
            changed, report2 = transform_python_file(path)
            if not changed:
                print(f"Skipping {path}: couldn't re-generate updated source")
                continue
            # parse report2 to extract diff and new source using AST unparse step
            # We'll produce new source by reparsing and unparsing
            text = path.read_text(encoding='utf-8')
            tree = ast.parse(text)
            transformer = ReferenceTransformer()
            new_tree = transformer.visit(tree)
            ast.fix_missing_locations(new_tree)
            if ast_unparse is None:
                print(f"ERROR: cannot unparse AST for {path}; skipping")
                continue
            new_source = ast_unparse(new_tree)
            if not new_source.endswith('\n'):
                new_source += '\n'
            # Backup original and write
            bak = path.with_suffix(path.suffix + '.bak')
            if not bak.exists():
                # write backup
                bak.write_text(path.read_text(encoding='utf-8'), encoding='utf-8')
            path.write_text(new_source, encoding='utf-8')
            print(f"Wrote updated Python file: {path}")
        elif path.suffix in {'.yaml', '.yml'}:
            # Re-run YAML transform to get new text
            if YAML_AVAILABLE:
                text = path.read_text(encoding='utf-8')
                data = yaml.safe_load(text)
                def walk(obj):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            obj[k] = walk(v)
                        return obj
                    elif isinstance(obj, list):
                        return [walk(x) for x in obj]
                    elif isinstance(obj, str):
                        s = obj
                        for old, new in PATH_REPLACEMENTS.items():
                            if old in s:
                                s = s.replace(old, new)
                        return s
                    else:
                        return obj
                new_data = walk(data)
                new_text = yaml.safe_dump(new_data, sort_keys=False)
                bak = path.with_suffix(path.suffix + '.bak')
                if not bak.exists():
                    bak.write_text(path.read_text(encoding='utf-8'), encoding='utf-8')
                path.write_text(new_text, encoding='utf-8')
                print(f"Wrote updated YAML file: {path}")
            else:
                # fallback simple text replace
                text = path.read_text(encoding='utf-8')
                new_text = text
                for old, new in PATH_REPLACEMENTS.items():
                    new_text = new_text.replace(old, new)
                bak = path.with_suffix(path.suffix + '.bak')
                if not bak.exists():
                    bak.write_text(text, encoding='utf-8')
                path.write_text(new_text, encoding='utf-8')
                print(f"Wrote updated YAML (fallback) file: {path}")
        else:
            # Generic text replacement for markdown/txt
            text = path.read_text(encoding='utf-8')
            new_text = text
            for old, new in PATH_REPLACEMENTS.items():
                new_text = new_text.replace(old, new)
            for old, new in IMPORT_REPLACEMENTS.items():
                new_text = new_text.replace(old, new)
            bak = path.with_suffix(path.suffix + '.bak')
            if not bak.exists():
                bak.write_text(text, encoding='utf-8')
            path.write_text(new_text, encoding='utf-8')
            print(f"Wrote updated text file: {path}")

    print('\nAll changes applied. Backups saved with .bak suffix.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python3
"""
Update All References in Migrated Files
Updates import statements and file paths to match the new structure.
This script modifies files in the NEW locations (not originals).
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Files to update (in their NEW locations)
FILES_TO_UPDATE = [
    "scripts/processing/run_pipeline.py",
    "scripts/processing/pose_demo.py",
    "scripts/processing/debug_gaze.py",
    "config/gun_dataset.yaml",
]

# Reference updates: (pattern, replacement, description)
REFERENCE_UPDATES = [
    # Import paths
    (
        r'from smart_coach\.pose_landmarks import',
        'from smart_coach.constants.pose_landmarks import',
        'Update pose_landmarks import path'
    ),
    
    # Model paths
    (
        r'"models/yolov8m-pose\.pt"',
        '"data/models/yolov8m-pose.pt"',
        'Update pose model path'
    ),
    (
        r'"models/yolov8n-face\.pt"',
        '"data/models/yolov8n-face.pt"',
        'Update face model path'
    ),
    (
        r'"models/hand_landmarker\.task"',
        '"data/models/hand_landmarker.task"',
        'Update hand model path'
    ),
    
    # Input/Output paths
    (
        r'"input/',
        '"data/input/',
        'Update input directory path'
    ),
    (
        r'"output/',
        '"data/output/',
        'Update output directory path'
    ),
    
    # YAML dataset paths
    (
        r'path:\s*\./Gunmen_Dataset',
        'path: ./data/datasets/gunmen',
        'Update dataset path in YAML'
    ),
]

# Additional regex patterns for catching variations
FLEXIBLE_PATTERNS = [
    (r"'models/", "'data/models/", "Single-quoted model paths"),
    (r"'input/", "'data/input/", "Single-quoted input paths"),
    (r"'output/", "'data/output/", "Single-quoted output paths"),
]

def update_file_references(file_path: Path) -> Tuple[int, List[str]]:
    """
    Update all references in a single file.
    Returns: (number of changes, list of change descriptions)
    """
    if not file_path.exists():
        return 0, [f"File not found: {file_path}"]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 0, [f"Error reading file: {e}"]
    
    original_content = content
    changes = []
    change_count = 0
    
    # Apply all reference updates
    for pattern, replacement, description in REFERENCE_UPDATES + FLEXIBLE_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            change_count += len(matches)
            changes.append(f"  • {description}: {len(matches)} occurrence(s)")
    
    # Only write if changes were made
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return change_count, changes
        except Exception as e:
            return 0, [f"Error writing file: {e}"]
    
    return 0, []

def find_all_python_files(directory: Path) -> List[Path]:
    """Recursively find all Python files in directory."""
    python_files = []
    for item in directory.rglob("*.py"):
        # Skip __pycache__ and migration scripts
        if "__pycache__" not in str(item) and "migration" not in str(item):
            python_files.append(item)
    return python_files

def update_all_smart_coach_files():
    """Update all Python files in smart_coach package."""
    print("\n" + "="*60)
    print("Updating Smart Coach Package Files")
    print("="*60)
    
    smart_coach_dir = BASE_DIR / "smart_coach"
    if not smart_coach_dir.exists():
        print("Smart coach directory not found")
        return 0
    
    python_files = find_all_python_files(smart_coach_dir)
    print(f"\nFound {len(python_files)} Python files in smart_coach/")
    
    total_changes = 0
    for py_file in python_files:
        rel_path = py_file.relative_to(BASE_DIR)
        change_count, changes = update_file_references(py_file)
        if change_count > 0:
            print(f"\n✓ Updated: {rel_path}")
            for change in changes:
                print(change)
            total_changes += change_count
    
    return total_changes

def update_scripts():
    """Update script files."""
    print("\n" + "="*60)
    print("Updating Script Files")
    print("="*60)
    
    total_changes = 0
    for file_rel_path in FILES_TO_UPDATE:
        file_path = BASE_DIR / file_rel_path
        
        if not file_path.exists():
            print(f"\n⚠ Not found: {file_rel_path}")
            continue
        
        change_count, changes = update_file_references(file_path)
        
        if change_count > 0:
            print(f"\n✓ Updated: {file_rel_path}")
            for change in changes:
                print(change)
            total_changes += change_count
        else:
            print(f"\n⊘ No changes needed: {file_rel_path}")
    
    return total_changes

def create_path_compatibility_module():
    """Create a compatibility module for transitioning."""
    print("\n" + "="*60)
    print("Creating Path Compatibility Module")
    print("="*60)
    
    compat_content = '''"""
Path compatibility module for Smart Coach.
Provides centralized path management during and after migration.
"""

from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
DATASETS_DIR = DATA_DIR / "datasets"

# Model paths
POSE_MODEL_PATH = MODELS_DIR / "yolov8m-pose.pt"
FACE_MODEL_PATH = MODELS_DIR / "yolov8n-face.pt"
HAND_MODEL_PATH = MODELS_DIR / "hand_landmarker.task"

# Config directory
CONFIG_DIR = BASE_DIR / "config"

# Ensure directories exist
for directory in [DATA_DIR, MODELS_DIR, INPUT_DIR, OUTPUT_DIR, DATASETS_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def get_model_path(model_name: str) -> Path:
    """Get full path to a model file."""
    return MODELS_DIR / model_name

def get_input_path(filename: str) -> Path:
    """Get full path to an input file."""
    return INPUT_DIR / filename

def get_output_path(filename: str) -> Path:
    """Get full path to an output file."""
    return OUTPUT_DIR / filename

def get_dataset_path(dataset_name: str) -> Path:
    """Get full path to a dataset directory."""
    return DATASETS_DIR / dataset_name
'''
    
    compat_path = BASE_DIR / "smart_coach" / "utils" / "paths.py"
    
    try:
        with open(compat_path, 'w') as f:
            f.write(compat_content)
        print(f"✓ Created: smart_coach/utils/paths.py")
        print("  This module provides centralized path management")
        return True
    except Exception as e:
        print(f"✗ Failed to create paths.py: {e}")
        return False

def verify_updated_files():
    """Verify that key files have been updated."""
    print("\n" + "="*60)
    print("Verification")
    print("="*60)
    
    verification_checks = [
        ("scripts/processing/run_pipeline.py", b"data/models/yolov8m-pose.pt"),
        ("scripts/processing/run_pipeline.py", b"data/input/"),
        ("scripts/processing/run_pipeline.py", b"data/output/"),
        ("config/gun_dataset.yaml", b"data/datasets/gunmen"),
    ]
    
    all_pass = True
    for file_path, expected_content in verification_checks:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            with open(full_path, 'rb') as f:
                content = f.read()
            if expected_content in content:
                print(f"✓ {file_path} contains correct references")
            else:
                print(f"✗ {file_path} missing expected references")
                all_pass = False
        else:
            print(f"⚠ {file_path} not found")
            all_pass = False
    
    return all_pass

def main():
    """Main execution."""
    print("="*60)
    print("Smart Coach Reference Updater")
    print("="*60)
    print(f"\nBase directory: {BASE_DIR}")
    print("\nThis script updates import paths and file references")
    print("in the NEW file locations.\n")
    
    response = input("Proceed with updates? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Update cancelled.")
        return
    
    total_changes = 0
    
    # Update script files
    total_changes += update_scripts()
    
    # Update smart_coach package files
    total_changes += update_all_smart_coach_files()
    
    # Create compatibility module
    create_path_compatibility_module()
    
    # Verify updates
    verify_updated_files()
    
    print("\n" + "="*60)
    print("Update Complete!")
    print("="*60)
    print(f"\nTotal changes made: {total_changes}")
    print("\nNext steps:")
    print("1. Test the new structure:")
    print("   cd /home/jon/Desktop/Smart_Coach_Pose_Estimation")
    print("   python scripts/processing/run_pipeline.py")
    print("2. If tests pass, remove old files:")
    print("   - old scripts/yolo_pose_with_mediapipe_hands.py")
    print("   - old scripts/pose_demo.py")
    print("   - old scripts/debug_gaze.py")
    print("   - old smart_coach/pose_landmarks.py")
    print("3. Update .gitignore for new structure")

if __name__ == "__main__":
    main()
