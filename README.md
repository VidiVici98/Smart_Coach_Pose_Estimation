# Smart Coach – Pose Detection & Metrics Pipeline

## 🚀 Quick Start

**New to this repo or setting up a fresh environment?** Start here:

```bash
# 1. Clone and navigate
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation

# 2. Set up virtual environment
python3 -m venv mediapipe_env
source mediapipe_env/bin/activate  # On Windows: mediapipe_env\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Download model files
python scripts/tools/download_models.py

# 5. Create test video (or use your own)
python scripts/tools/create_test_video.py
# OR copy your own: cp your_video.mp4 data/input/test_video.mp4

# 6. Verify setup
python scripts/tools/verify_setup.py

# 7. Run the pipeline!
python scripts/processing/run_pipeline.py
```

**Results will be in:**
- `data/output/output_full.mp4` - Annotated video with pose overlays
- `data/output/analytics.csv` - Frame-by-frame metrics (285 fields per frame)

**📖 For detailed setup instructions, see [SETUP.md](SETUP.md)**  
**📱 Working on mobile? See [MOBILE_WORKFLOW.md](MOBILE_WORKFLOW.md)**

---

## Overview

This repository contains the **computer vision and analytics pipeline** responsible for extracting biomechanical, spatial, and safety-related metrics from training video. It is a **foundational, model-agnostic processing layer** designed to turn raw video into structured, time-series data suitable for downstream analysis, coaching feedback, and machine learning.

**This repo does NOT perform interpretation, coaching logic, scoring, or user-facing feedback.**
It focuses exclusively on:

* Detecting bodies, hands, and relevant objects in video
* Tracking pose and motion over time
* Normalizing measurements across subjects and camera setups
* Exporting high-quality, frame-accurate analytics data

---

## High-Level Goals

1. **Robust pose tracking from consumer video**

   * Handle varied camera angles, distances, lighting, and shooter physiques
   * Maintain temporal stability via smoothing and continuity logic

2. **Accurate, normalized metric extraction**

   * Produce measurements that are *comparable across people and recordings*
   * Avoid raw pixel-space assumptions wherever possible

3. **Safety-critical spatial awareness**

   * Detect body occupancy, muzzle orientation, and potential safety violations
   * Enable downstream logic to reason about unsafe conditions

4. **Extensible and modular design**

   * Allow object detection models (e.g., firearm detection) to be swapped or upgraded
   * Support future sensors, models, or metrics without rewrites

---

## What This Repo Is (and Is Not)

### ✅ This Repo *Is*

* A **video → structured data** transformation pipeline
* Focused on **pose, motion, geometry, and spatial relationships**
* Designed for **offline processing** of recorded training footage
* A data producer for:

  * Coaching systems
  * Analytics dashboards
  * ML model training
  * Safety audits

### ❌ This Repo Is *Not*

* A mobile or web application
* A real-time inference system (though parts may run near-real-time)
* A coaching or scoring engine
* A UX or visualization product (overlays are diagnostic only)

---

## Core Methodology

### 1. Multi-Model Vision Stack

The system intentionally combines **best-in-class models for specific tasks** rather than relying on a single monolithic network.

| Task                       | Model                       |
| -------------------------- | --------------------------- |
| Full-body pose estimation  | YOLOv8 Pose                 |
| Hand landmark detection    | MediaPipe Hands (Tasks API) |
| Body segmentation          | Mask R-CNN                  |
| Object detection (firearm) | Fine-tuned YOLOv5 / YOLOv8  |

This hybrid approach allows each subsystem to be upgraded independently.

---

### 2. Temporal Consistency & Smoothing

Raw detections are inherently noisy. To mitigate jitter and dropout:

* **Exponential smoothing** is applied to pose and hand landmarks
* Previous valid detections are reused when confidence drops
* Velocity is derived from normalized deltas, not raw pixels

This produces cleaner motion signals without over-filtering meaningful movement.

---

### 3. Normalization Strategy

Raw pixel coordinates are **never treated as absolute truth**.

Key normalization principles:

* **Body-relative scaling**

  * Most distances are normalized using shoulder width or other stable body measures
* **Camera-distance invariance**

  * Metrics remain comparable whether the subject is close or far from the camera
* **Left vs Right symmetry support**

  * Metrics are computed independently per side when applicable

This allows analytics to generalize across recordings and shooters.

---

### 4. Metric Categories

The pipeline produces metrics in several categories:

#### A. Pose & Kinematics

* Normalized joint positions
* Per-joint velocity vectors
* Joint-to-joint distances and angles

#### B. Hand & Finger Metrics

* Full 21-point hand landmarks
* Relative finger motion
* Simple trigger-pull heuristics (motion-based, not semantic)

#### C. Spatial & Safety Metrics

* Body occupancy mask
* Muzzle direction vector
* Muzzle cone intersection with body mask
* Binary and continuous safety indicators

#### D. Object-Relative Metrics (Planned / In Progress)

* Firearm bounding box
* Grip alignment
* Muzzle vs wrist orientation delta
* Slide / barrel vector estimation

---

## Muzzle Orientation Philosophy

Early versions estimate muzzle direction using **arm kinematics** (elbow → wrist vector).
This is a **fallback heuristic**, not a final solution.

The long-term approach is:

1. Detect the firearm explicitly (YOLO detection)
2. Identify muzzle-side orientation using:

   * Bounding box geometry
   * Aspect ratio and orientation
   * Temporal consistency
3. Fuse:

   * Gun orientation
   * Wrist alignment
   * Hand pose
4. Use kinematics only when object detection confidence is low

This layered strategy avoids over-trusting any single signal.

---

## Output Data

### CSV Analytics Export

Each processed video produces a frame-indexed CSV containing:

* Frame number
* Normalized body keypoints + velocities
* Normalized hand landmarks + velocities
* Derived metrics (e.g., shoulder width)
* Safety flags (e.g., muzzle_safe)

This format is intentionally:

* Human-readable
* ML-friendly
* Easy to ingest into Pandas, NumPy, or time-series databases

---

## Repository Structure

```
smart_coach/                    # Core library package
  ├─ constants/                 # Keypoint definitions
  ├─ core/                      # Pipeline orchestration (future)
  ├─ models/                    # Model wrappers (future)
  ├─ metrics/                   # Metric calculations (future)
  ├─ visualization/             # Rendering overlays (future)
  └─ utils/                     # Helper utilities (future)

scripts/
  ├─ processing/                # Main executable scripts
  │   ├─ run_pipeline.py        # Main entry point
  │   ├─ pose_demo.py           # Simple pose demo
  │   └─ debug_gaze.py          # Gaze debugging
  ├─ tools/                     # Utility scripts
  └─ archive/                   # Archived scripts (for reference)

data/
  ├─ input/                     # Input videos
  ├─ output/                    # Processed outputs
  ├─ models/                    # Model weights
  │   ├─ yolov8m-pose.pt
  │   ├─ yolov8n-face.pt
  │   └─ hand_landmarker.task
  └─ datasets/                  # Training datasets

config/                         # Configuration files
  └─ training_dataset.yaml

tests/                          # Unit tests
docs/                           # Documentation
  └─ REPOSITORY_STRUCTURE.md    # Detailed structure guide
third_party/                    # External dependencies
```

For a complete structure overview, see [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md).

---

## Design Principles

* **Separation of concerns**

  * Detection ≠ interpretation
  * Measurement ≠ coaching
* **Fail gracefully**

  * Partial data is better than no data
* **Traceability**

  * Every metric should be explainable geometrically
* **Future-proofing**

  * Expect better models, not perfect ones today

---

## Current Limitations

* CPU-only training and inference is slow
* Gun orientation is still improving
* No semantic understanding (e.g., “this is a reload”)
* No real-time guarantees

These are intentional trade-offs at this stage.

---

## Roadmap & Future Development

For comprehensive development plans, priorities, and timelines, see **[ROADMAP.md](ROADMAP.md)**.

### Immediate Priorities (0-3 months)
* ⚡ **Pipeline performance optimization** — 4-20x speedup via GPU + caching
* 🎯 **Firearm detection & orientation** — Explicit firearm detection for accurate muzzle direction
* 🎓 **Coaching insights engine** — Rule-based coaching feedback from metrics
* 📊 **Automatic event segmentation** — Detect draws, presentations, reloads

### Medium-Term Goals (3-6 months)
* 🤖 **Machine learning integration** — Stance classification, form quality scoring
* 📱 **Web dashboard** — Interactive visualization and reporting
* 🧬 **Advanced biomechanics** — Recoil analysis, sight alignment, balance metrics
* 🚀 **Real-time processing** — Low-latency pipeline for live coaching

### Long-Term Vision (6-12+ months)
* 📱 Mobile application for range use
* 🏆 Competition and certification support
* 🔗 Integration with training platforms and equipment
* 🎯 Adaptive training recommendations

See [ROADMAP.md](ROADMAP.md) for detailed plans, AI coaching opportunities, and contribution ideas.

---

## License & Use

This repository is intended for **research, development, and training analysis** purposes.
