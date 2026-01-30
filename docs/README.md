# Smart Coach Documentation

Complete documentation for the Smart Coach Pose Estimation pipeline.

---

## 📚 Documentation Files

| Document | Purpose |
|----------|---------|
| **[SETUP_AND_TROUBLESHOOTING.md](SETUP_AND_TROUBLESHOOTING.md)** | Setup instructions, mobile workflows, troubleshooting |
| **[USAGE_GUIDE.md](USAGE_GUIDE.md)** | How to use the pipeline, configuration options |
| **[TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)** | Architecture, detection systems, advanced features |
| **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** | Current implementation status and capabilities |
| **[metrics_reference.md](metrics_reference.md)** | Complete metrics specification (303 fields) |
| **[ROADMAP.md](ROADMAP.md)** | Future development plans and timeline |

---

## 🚀 Quick Start

**New users:** Start with [SETUP_AND_TROUBLESHOOTING.md](SETUP_AND_TROUBLESHOOTING.md)

**Quick run:**
```bash
# Clone repository
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation

# Install dependencies
pip install -r requirements.txt

# Run pipeline on test video
python scripts/processing/run_pipeline.py
```

---

## 🎯 Find What You Need

### I want to...

**Set up the project**
→ [SETUP_AND_TROUBLESHOOTING.md](SETUP_AND_TROUBLESHOOTING.md)

**Run the pipeline**
→ [USAGE_GUIDE.md](USAGE_GUIDE.md)

**Understand the metrics**
→ [metrics_reference.md](metrics_reference.md)

**Fix a problem**
→ [SETUP_AND_TROUBLESHOOTING.md#troubleshooting](SETUP_AND_TROUBLESHOOTING.md#troubleshooting)

**Work on mobile/codespace**
→ [SETUP_AND_TROUBLESHOOTING.md#mobilecodespace-workflow](SETUP_AND_TROUBLESHOOTING.md#mobilecodespace-workflow)

**Understand the architecture**
→ [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)

**See what's implemented**
→ [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)

**Check the roadmap**
→ [ROADMAP.md](ROADMAP.md)

---

## 📦 What is Smart Coach?

Smart Coach is a **computer vision analytics pipeline** for shooter training video analysis:

**Input:** Training video (MP4)  
**Output:** 
- Annotated video with pose/gaze overlays
- CSV with 303 metrics per frame

**Features:**
- ✅ Full-body pose tracking (17 keypoints)
- ✅ Hand landmark detection (21 points × 2)
- ✅ 3D gaze estimation
- ✅ Body segmentation
- ✅ 303 metrics per frame

---

## 🔧 System Requirements

**Minimum:**
- Python 3.8+
- 8GB RAM
- 5GB disk space

**Recommended:**
- Python 3.10+
- 16GB RAM
- GPU (optional, faster processing)

---

## 📱 Mobile Users

GitHub Codespaces is recommended for mobile workflow (60 hours/month free).

See [Mobile/Codespace Workflow](SETUP_AND_TROUBLESHOOTING.md#mobilecodespace-workflow) for details.

---

## 🐛 Troubleshooting

Common issues and solutions in [SETUP_AND_TROUBLESHOOTING.md#troubleshooting](SETUP_AND_TROUBLESHOOTING.md#troubleshooting)

**Quick fixes:**
- Out of memory → Set `MAX_FRAMES = 30` in script
- libGL error → Use `opencv-python-headless`
- Slow processing → Reduce video resolution

---

## 📊 Project Status

**Current Version:** 1.0  
**Status:** Stable for offline processing  
**Last Updated:** 2026-01-30

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for detailed status.

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## 📞 Getting Help

1. Check documentation (start here!)
2. Search [GitHub Issues](https://github.com/VidiVici98/Smart_Coach_Pose_Estimation/issues)
3. Open new issue if not resolved

---

**Happy Coaching! 🎯**
