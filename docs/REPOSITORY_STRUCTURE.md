# Smart Coach Repository Structure

This document describes the current, clean structure of the Smart Coach Pose Estimation repository.

## Directory Structure

```
smart_coach_pose_estimation/
│
├── README.md                    # Main project documentation
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                      # Project license
├── .gitignore                   # Git ignore rules
│
├── .github/                     # GitHub configuration
│   └── copilot-instructions.md  # AI coding assistant instructions
│
├── smart_coach/                 # Core library package
│   ├── __init__.py
│   ├── constants/               # Constants and definitions
│   │   ├── __init__.py
│   │   └── pose_landmarks.py    # YOLOv8 pose keypoint definitions
│   ├── core/                    # Core processing modules
│   │   └── __init__.py
│   ├── models/                  # Model wrappers and loaders
│   │   └── __init__.py
│   ├── metrics/                 # Metric calculation logic
│   │   └── __init__.py
│   ├── visualization/           # Drawing and rendering
│   │   └── __init__.py
│   └── utils/                   # General utilities
│       └── __init__.py
│
├── scripts/                     # Executable scripts
│   ├── processing/              # Main processing scripts
│   │   ├── run_pipeline.py      # Main entry point for video processing
│   │   ├── pose_demo.py         # Simple pose detection demo
│   │   └── debug_gaze.py        # Gaze estimation debugging script
│   ├── tools/                   # Utility scripts
│   │   └── .gitkeep
│   └── archive/                 # Archived scripts (for reference)
│       └── migration/           # Migration scripts from restructuring
│
├── data/                        # All data files
│   ├── README.md
│   ├── input/                   # Input videos (gitignored)
│   ├── output/                  # Processed outputs (gitignored)
│   ├── models/                  # Model weights (gitignored, add with LFS)
│   │   ├── yolov8m-pose.pt
│   │   ├── yolov8n-face.pt
│   │   └── hand_landmarker.task
│   └── datasets/                # Training datasets
│       └── training/            # Training data (e.g., Gunmen dataset)
│
├── config/                      # Configuration files
│   ├── README.md
│   └── training_dataset.yaml    # Dataset configuration
│
├── tests/                       # Unit tests
│   ├── README.md
│   └── __init__.py
│
├── docs/                        # Documentation
│   ├── metrics_reference.md     # Metrics documentation
│   ├── MIGRATION_COMPLETE.md    # Migration completion notes
│   ├── NEW_STRUCTURE.md         # New structure documentation
│   ├── RESTRUCTURING_INDEX.md   # Restructuring index
│   ├── MIGRATION_GUIDE.md       # Migration guide
│   ├── RESTRUCTURE_SUMMARY.md   # Restructure summary
│   └── GITIGNORE_UPDATES.md     # .gitignore updates
│
├── third_party/                 # External dependencies
│   ├── README.md
│   └── (detectron2 would go here if needed)
│
├── runs/                        # Training/experiment runs (gitignored)
│   └── detect/
│
└── mediapipe_env/               # Virtual environment (gitignored)
```

## Key Design Principles

### 1. Separation of Concerns
- **Library code** (`smart_coach/`) - Reusable modules for pose processing
- **Scripts** (`scripts/`) - Entry points and executable tools
- **Data** (`data/`) - All data files, models, inputs, outputs
- **Configuration** (`config/`) - Configuration files
- **Documentation** (`docs/`) - All documentation files
- **Tests** (`tests/`) - Unit and integration tests

### 2. Python Package Structure
The `smart_coach/` directory follows standard Python package conventions:
- Can be imported as a module: `from smart_coach.constants import pose_landmarks`
- Ready for pip installation with a `setup.py` (future enhancement)
- Clear separation of responsibilities across submodules

### 3. Data Organization
All data files are under `data/`:
- **models/** - ML model weights (YOLOv8, MediaPipe, etc.)
- **input/** - Input videos for processing
- **output/** - Processed videos and CSV analytics
- **datasets/** - Training datasets for model fine-tuning

Large files are gitignored, with placeholders (`.gitkeep`) to maintain structure.

### 4. Scripts Organization
- **processing/** - Main processing scripts (run_pipeline.py, demos)
- **tools/** - Utility scripts for validation, benchmarking, etc.
- **archive/** - Archived scripts kept for reference only

## Usage

### Running the Main Pipeline
```bash
# Activate virtual environment
source mediapipe_env/bin/activate

# Run the main processing pipeline
python scripts/processing/run_pipeline.py
```

### Adding New Components

**New Model:**
Create wrapper in `smart_coach/models/` and add model weights to `data/models/`.

**New Metric:**
Add calculation logic to `smart_coach/metrics/`.

**New Script:**
Add to `scripts/processing/` for processing scripts or `scripts/tools/` for utilities.

**New Test:**
Add to `tests/` directory.

## Benefits of This Structure

1. **Clarity** - Clear location for every type of file
2. **Scalability** - Easy to add new models, metrics, or scripts
3. **Maintainability** - Modular structure simplifies debugging and testing
4. **Collaboration** - Multiple developers can work on different components
5. **Professional** - Follows Python community best practices
6. **Future-proof** - Ready for pip packaging and distribution

## Migration History

This structure was established through a migration process documented in `docs/MIGRATION_COMPLETE.md`. The old flat structure has been reorganized into this modular layout, with all scripts and paths updated accordingly.

Migration artifacts are preserved in:
- `docs/` - Migration documentation
- `scripts/archive/migration/` - Migration scripts (for reference)

## Next Steps

Recommended improvements:
1. Add `setup.py` for pip installation
2. Expand test coverage in `tests/`
3. Break up monolithic `run_pipeline.py` into smaller modules
4. Add CI/CD configuration
5. Consider adding type hints throughout codebase
