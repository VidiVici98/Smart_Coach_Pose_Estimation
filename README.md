# Smart Coach – Pose Detection & Metrics Pipeline

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
  ├─ core/                      # Pipeline orchestration
  ├─ models/                    # Model wrappers
  ├─ metrics/                   # Metric calculations
  ├─ visualization/             # Rendering overlays
  └─ utils/                     # Helper utilities

scripts/
  ├─ processing/                # Main executable scripts
  │   ├─ run_pipeline.py        # Main entry point
  │   ├─ pose_demo.py           # Simple pose demo
  │   └─ debug_gaze.py          # Gaze debugging
  ├─ tools/                     # Utility scripts
  └─ migration/                 # Migration tools

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
third_party/                    # External dependencies
  └─ detectron2/
```

(Structure will evolve as components are separated further.)

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

## Future Directions

* Improved firearm orientation estimation
* Multi-person disambiguation
* Camera calibration support
* Depth approximation
* Automatic segment detection (draw, presentation, trigger press, etc.)

---

## License & Use

This repository is intended for **research, development, and training analysis** purposes.
