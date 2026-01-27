# Git Ignore Updates for New Structure

Add these lines to your .gitignore file after migration:

```gitignore
# Data directories (new structure)
data/input/*.mp4
data/input/*.avi
data/input/*.mov
data/output/*.mp4
data/output/*.avi
data/output/*.csv
data/models/*.pt
data/models/*.task
data/models/*.onnx
data/datasets/*/train/
data/datasets/*/val/

# Keep directory structure
!data/input/.gitkeep
!data/output/.gitkeep
!data/models/.gitkeep

# Third party (if not using git submodules)
third_party/detectron2/

# Migration scripts (temporary - remove after migration)
# scripts/migration/
```

These replace the old paths:
- `input/` → `data/input/`
- `output/` → `data/output/`
- `models/` → `data/models/`
- `Training_Dataset/` → `data/datasets/training/`
- `detectron2/` → `third_party/detectron2/`
