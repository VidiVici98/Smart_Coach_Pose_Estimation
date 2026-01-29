<!-- Last Modified: 2026-01-29 -->
# Documentation Index

Welcome to the Smart Coach Pose Estimation documentation! This index helps you find the right documentation for your needs.

---

## 🚀 Getting Started

**First time here?** Start with these:

1. **[README.md](../README.md)** - Project overview and quick start
2. **[docs/guides/SETUP.md](guides/SETUP.md)** - Detailed setup instructions
3. **[docs/START_HERE.md](START_HERE.md)** - Navigation guide for all docs

---

## 📖 Documentation Structure

### User Guides (`docs/guides/`)

Complete guides for setup and usage:

- **[SETUP.md](guides/SETUP.md)** - Complete setup guide (desktop & codespace)
- **[MOBILE_WORKFLOW.md](guides/MOBILE_WORKFLOW.md)** - Mobile/GitHub Codespaces workflow
- **[QUICKSTART_MOBILE.md](guides/QUICKSTART_MOBILE.md)** - Quick mobile setup
- **[CODESPACE_RECOVERY.md](guides/CODESPACE_RECOVERY.md)** - Codespace troubleshooting
- **[ENHANCEMENTS_QUICKSTART.md](guides/ENHANCEMENTS_QUICKSTART.md)** - Enhanced features guide
- **[START_HERE_CODESPACE.md](guides/START_HERE_CODESPACE.md)** - Codespace-specific start guide

### Technical Documentation (`docs/`)

Implementation and API documentation:

- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Complete implementation status and features
- **[METRICS_ENHANCEMENTS.md](METRICS_ENHANCEMENTS.md)** - Enhanced metrics (303 fields) documentation
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Pipeline usage and best practices
- **[metrics_reference.md](metrics_reference.md)** - Complete metrics specification
- **[REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md)** - Repository organization
- **[DETECTION_ENHANCEMENTS.md](DETECTION_ENHANCEMENTS.md)** - Detection improvements
- **[GITIGNORE_UPDATES.md](GITIGNORE_UPDATES.md)** - Gitignore configuration

### Troubleshooting (`docs/troubleshooting/`)

Solutions to common problems:

- **[TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md)** - General troubleshooting guide
- **[TROUBLESHOOTING_EXIT15.md](troubleshooting/TROUBLESHOOTING_EXIT15.md)** - Memory/OOM issues
- **[MEMORY_FIX_GUIDE.md](troubleshooting/MEMORY_FIX_GUIDE.md)** - Memory optimization guide
- **[ACTUAL_FIX.md](troubleshooting/ACTUAL_FIX.md)** - Specific fix implementations
- **[RECOVERY_SUMMARY.md](troubleshooting/RECOVERY_SUMMARY.md)** - Recovery procedures
- **[RECOVERY_TOOLS_README.md](troubleshooting/RECOVERY_TOOLS_README.md)** - Recovery tools documentation

### Planning & Roadmap (`docs/`)

Project status and future plans:

- **[ROADMAP.md](ROADMAP.md)** - Long-term development roadmap
- **[NEXT_STEPS.md](NEXT_STEPS.md)** - Immediate action items
- **[PR_SUMMARY.md](PR_SUMMARY.md)** - Recent pull request summaries
- **[START_HERE.md](START_HERE.md)** - Quick navigation guide
- **[RUN_NOW.md](RUN_NOW.md)** - Quick run instructions
- **[RUN_THIS_NOW.md](RUN_THIS_NOW.md)** - Emergency run guide

### Tools & Utilities (`docs/tools/`)

Tool-specific documentation:

- **[ONE_LINE_FIX.txt](tools/ONE_LINE_FIX.txt)** - Quick fix commands

### Notebooks (`docs/notebooks/`)

Jupyter notebooks for interactive exploration:

- **[setup_and_run.ipynb](notebooks/setup_and_run.ipynb)** - Interactive setup notebook

### Archive (`docs/archive/`)

Historical documentation (completed migrations, old planning):

- **[MIGRATION_COMPLETE.md](archive/MIGRATION_COMPLETE.md)** - Migration completion notes
- **[MIGRATION_GUIDE.md](archive/MIGRATION_GUIDE.md)** - Historical migration guide
- **[REORGANIZATION_SUMMARY.md](archive/REORGANIZATION_SUMMARY.md)** - Reorganization summary
- **[RESTRUCTURE_SUMMARY.md](archive/RESTRUCTURE_SUMMARY.md)** - Restructure summary
- **[NEW_STRUCTURE.md](archive/NEW_STRUCTURE.md)** - Previous structure documentation
- **[PLANNING_SUMMARY.md](archive/PLANNING_SUMMARY.md)** - Planning notes
- **[RESTRUCTURING_INDEX.md](archive/RESTRUCTURING_INDEX.md)** - Restructuring index

---

## 🎯 Quick Navigation by Task

### I want to...

**Set up the project:**
1. [SETUP.md](guides/SETUP.md) - Complete setup guide
2. [README.md](../README.md) - Quick start commands

**Run the pipeline:**
1. [USAGE_GUIDE.md](USAGE_GUIDE.md) - Usage examples
2. [RUN_NOW.md](RUN_NOW.md) - Quick run instructions

**Understand the metrics:**
1. [METRICS_ENHANCEMENTS.md](METRICS_ENHANCEMENTS.md) - Enhanced metrics overview
2. [metrics_reference.md](metrics_reference.md) - Complete specification
3. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Current capabilities

**Fix a problem:**
1. [troubleshooting/TROUBLESHOOTING.md](troubleshooting/TROUBLESHOOTING.md) - General issues
2. [troubleshooting/MEMORY_FIX_GUIDE.md](troubleshooting/MEMORY_FIX_GUIDE.md) - Memory issues
3. [troubleshooting/TROUBLESHOOTING_EXIT15.md](troubleshooting/TROUBLESHOOTING_EXIT15.md) - OOM errors

**Work on mobile/codespace:**
1. [guides/MOBILE_WORKFLOW.md](guides/MOBILE_WORKFLOW.md) - Complete mobile guide
2. [guides/QUICKSTART_MOBILE.md](guides/QUICKSTART_MOBILE.md) - Quick mobile setup
3. [guides/CODESPACE_RECOVERY.md](guides/CODESPACE_RECOVERY.md) - Codespace issues

**Contribute to the project:**
1. [../CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
2. [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) - Repo organization

**Understand implementation:**
1. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Complete status
2. [DETECTION_ENHANCEMENTS.md](DETECTION_ENHANCEMENTS.md) - Detection improvements
3. [METRICS_ENHANCEMENTS.md](METRICS_ENHANCEMENTS.md) - Metrics enhancements

---

## 📁 Repository Structure

```
Smart_Coach_Pose_Estimation/
├── README.md                    # Project overview & quick start
├── CONTRIBUTING.md              # How to contribute
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Python project configuration
│
├── docs/                        # Documentation
│   ├── README.md               # This file
│   ├── guides/                 # User guides
│   ├── troubleshooting/        # Troubleshooting docs
│   ├── tools/                  # Tool documentation
│   ├── notebooks/              # Jupyter notebooks
│   └── archive/                # Historical docs
│
├── smart_coach/                # Core library code
│   ├── constants/              # Constants and configurations
│   ├── utils/                  # Utility functions
│   └── ...                     # Other modules
│
├── scripts/                    # Executable scripts
│   ├── processing/             # Main processing scripts
│   ├── tools/                  # Utility scripts
│   └── setup/                  # Setup and diagnostic scripts
│
├── data/                       # Data directory (gitignored)
│   ├── input/                  # Input videos
│   ├── output/                 # Output videos and CSVs
│   ├── models/                 # Model files
│   └── datasets/               # Training datasets
│
├── tests/                      # Unit tests
└── config/                     # Configuration files
```

---

## 🔗 External Resources

- **GitHub Repository:** [VidiVici98/Smart_Coach_Pose_Estimation](https://github.com/VidiVici98/Smart_Coach_Pose_Estimation)
- **YOLOv8 Documentation:** [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- **MediaPipe Docs:** [MediaPipe Solutions](https://developers.google.com/mediapipe)
- **Issue Tracker:** [GitHub Issues](https://github.com/VidiVici98/Smart_Coach_Pose_Estimation/issues)

---

## 📝 Document Status

**Last Updated:** 2026-01-29  
**Documentation Version:** 2.0  
**Repository Version:** Post-reorganization

---

## 💡 Tips

- **Searching:** Use `grep -r "search term" docs/` to search all documentation
- **Broken Links:** Report broken links as GitHub issues
- **Updates:** Documentation is updated with code changes
- **Questions:** Open an issue with the `documentation` label

---

**Need help?** Start with [START_HERE.md](START_HERE.md) or open a GitHub issue!
