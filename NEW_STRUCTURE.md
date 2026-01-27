# Smart Coach Repository Restructuring Plan

## New Structure Overview

```
smart_coach_pose_estimation/
├── README.md
├── .github/
│   └── copilot-instructions.md
├── .gitignore
│
├── smart_coach/                    # Core library package
│   ├── __init__.py
│   ├── core/                       # Core processing modules
│   │   ├── __init__.py
│   │   ├── pipeline.py            # Main pipeline orchestrator
│   │   ├── video_processor.py     # Video I/O and frame processing
│   │   └── temporal_smoothing.py  # Temporal smoothing utilities
│   ├── models/                     # Model wrappers and loaders
│   │   ├── __init__.py
│   │   ├── pose_model.py          # YOLOv8 pose wrapper
│   │   ├── hand_model.py          # MediaPipe hands wrapper
│   │   ├── face_model.py          # YOLOv8 face + MediaPipe mesh wrapper
│   │   └── mask_model.py          # Mask R-CNN wrapper
│   ├── metrics/                    # Metric calculation logic
│   │   ├── __init__.py
│   │   ├── pose_metrics.py        # Body pose metrics
│   │   ├── hand_metrics.py        # Hand/trigger metrics
│   │   ├── gaze_metrics.py        # 3D gaze estimation
│   │   └── normalization.py       # Shoulder-width normalization
│   ├── visualization/              # Drawing and rendering
│   │   ├── __init__.py
│   │   ├── overlay.py             # Video overlay rendering
│   │   └── drawing_utils.py       # Drawing primitives
│   ├── utils/                      # General utilities
│   │   ├── __init__.py
│   │   ├── geometry.py            # Vector math, lerp, etc.
│   │   ├── config.py              # Configuration management
│   │   └── csv_export.py          # CSV output formatting
│   └── constants/                  # Constants and enums
│       ├── __init__.py
│       └── pose_landmarks.py      # Keypoint definitions
│
├── scripts/                        # Executable scripts
│   ├── processing/                 # Main processing scripts
│   │   ├── run_pipeline.py        # Main entry point (formerly yolo_pose_with_mediapipe_hands.py)
│   │   ├── pose_demo.py           # Simple pose demo
│   │   └── debug_gaze.py          # Gaze debugging script
│   ├── tools/                      # Utility scripts
│   │   ├── validate_output.py     # Output validation
│   │   └── benchmark_models.py    # Model performance testing
│   └── migration/                  # Migration scripts (temporary)
│       ├── migrate_files.py       # File relocation script
│       └── update_references.py   # Import path updater
│
├── data/                           # All data files
│   ├── input/                      # Input videos
│   ├── output/                     # Processed outputs
│   ├── datasets/                   # Training datasets
│   │   └── training/                 # Gunmen dataset
│   │       ├── classes.txt
│   │       ├── train/
│   │       └── val/
│   └── models/                     # Model weights
│       ├── yolov8m-pose.pt
│       ├── yolov8n-face.pt
│       └── hand_landmarker.task
│
├── config/                         # Configuration files
│   ├── default_config.yaml
│   └── training_dataset.yaml
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   ├── test_pipeline.py
│   ├── test_metrics.py
│   └── test_models.py
│
├── docs/                           # Documentation
│   ├── metrics_reference.md
│   ├── API.md
│   └── architecture.md
│
├── third_party/                    # External dependencies
│   └── detectron2/                 # Detectron2 submodule
│
├── runs/                           # Training/experiment runs
│   └── detect/
│
├── mediapipe_env/                  # Virtual environment (gitignored)
│
└── setup.py                        # Package installation
```

## Migration Mapping

### Files to Move:
1. `scripts/yolo_pose_with_mediapipe_hands.py` → `scripts/processing/run_pipeline.py`
2. `scripts/pose_demo.py` → `scripts/processing/pose_demo.py`
3. `scripts/debug_gaze.py` → `scripts/processing/debug_gaze.py`
4. `smart_coach/pose_landmarks.py` → `smart_coach/constants/pose_landmarks.py`
5. `models/*` → `data/models/*`
6. `input/*` → `data/input/*`
7. `output/*` → `data/output/*`
8. `Training_Dataset/*` → `data/datasets/training/*`
9. `training_dataset.yaml` → `config/training_dataset.yaml`
10. `detectron2/*` → `third_party/detectron2/*`

### Directories to Create:
- `smart_coach/core/`
- `smart_coach/models/`
- `smart_coach/metrics/`
- `smart_coach/visualization/`
- `smart_coach/utils/`
- `smart_coach/constants/`
- `scripts/processing/`
- `scripts/tools/`
- `scripts/migration/`
- `data/`
- `data/input/`
- `data/output/`
- `data/datasets/training/`
- `data/models/`
- `config/`
- `tests/`
- `third_party/`

### Import Changes Required:
- `from smart_coach.pose_landmarks import ...` → `from smart_coach.constants.pose_landmarks import ...`
- Model paths: `models/...` → `data/models/...`
- Input paths: `input/...` → `data/input/...`
- Output paths: `output/...` → `data/output/...`

## Benefits of New Structure

1. **Clear Separation**: Core library vs. scripts vs. data
2. **Modularity**: Each component has its own directory
3. **Scalability**: Easy to add new models, metrics, or processing scripts
4. **Professional**: Standard Python package structure
5. **Testability**: Clear tests/ directory for unit tests
6. **Portability**: smart_coach/ can be pip installed as a package
7. **Collaboration**: Easier for multiple developers to work on different components
8. **Third-party Isolation**: External deps like detectron2 clearly separated

## Migration Steps

1. **Run scaffold script** - Creates all new directories
2. **Run migration script** - Moves files to new locations (creates copies)
3. **Run reference update script** - Updates all import paths and file references
4. **Manual verification** - Test that everything still works
5. **Clean up old files** - Remove original files once verified
