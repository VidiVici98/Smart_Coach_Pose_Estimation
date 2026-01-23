# Smart Coach: AI Coding Instructions

## Project Purpose
Smart Coach is a **computer vision analytics pipeline** for extracting pose, hand, and safety metrics from training videos (shooter training focus). It converts raw video into structured, frame-indexed CSV data suitable for coaching feedback and ML analysis.

**NOT** a real-time system, coaching engine, or UX product—purely offline measurement and metric generation.

---

## Architecture Overview

### Core Pipeline (`scripts/yolo_pose_with_mediapipe_hands.py`)
Single-file monolithic processor orchestrating:
1. **YOLOv8 Pose** → Full-body skeleton (17 keypoints + velocities)
2. **MediaPipe Hands (Tasks API)** → Dual-hand landmarks (21 pts each side)
3. **Mask R-CNN** → Body segmentation mask
4. **YOLOv8 Face** + **MediaPipe Face Mesh** → 3D head pose estimation
5. **Custom gaze logic** → 3D-to-2D head-torso blended gaze vector

### Data Flow
```
Video → Frame decomposition → Multi-model inference
    → Temporal smoothing (exponential lerp) → Skeleton + hand pose
    → Body mask + 3D face → Head-torso gaze blend
    → CSV row export (frame-indexed) + MP4 visualization overlay
```

### Key Modules
- [smart_coach/pose_landmarks.py](smart_coach/pose_landmarks.py) – Defines YOLOv8 pose skeleton (17 points) and MediaPipe pose enums
- [scripts/yolo_pose_with_mediapipe_hands.py](scripts/yolo_pose_with_mediapipe_hands.py) – Main pipeline; imports from smart_coach
- Detectron2 embedded for Mask R-CNN body mask inference

---

## Critical Patterns & Conventions

### 1. Temporal Smoothing
**All detections are noisy.** Apply exponential lerp to stabilize:
```python
TEMP_ALPHA = 0.7  # Blending factor (0.7 = 70% prev, 30% new)
# Apply to pose keypoints, hand landmarks, gaze vectors
p = lerp(prev_pose[i], new_p, TEMP_ALPHA)
```
This trades responsiveness for jitter reduction—tune per-metric if needed.

### 2. Normalization by Shoulder Width
**All spatial metrics are relative, never absolute pixel space:**
```python
shoulder_width = norm(pts[5] - pts[6])  # Right shoulder - left shoulder
# Used to scale 3D face model: model_points = FACE_3D_POINTS * shoulder_width / 100.0
```
Ensures metrics transfer across subjects and camera distances.

### 3. 3D Gaze Estimation (Head + Torso Blending)
- Head forward direction via `cv2.solvePnP()` (6-point 2D-to-3D mapping)
- Torso forward via perpendicular to shoulder vector
- **Blend:** `(1 - TORSO_BLEND) * head + TORSO_BLEND * torso` → more robust to head tilt
- **Smooth:** Buffer last 5 frames, clamp rotation per frame, flip if dot product < 0
- **Output:** 2D gaze vector + "gaze_on_body" flag (ray-cast against body mask)

### 4. Trigger Pull Detection
Simple heuristic, not semantic:
```python
row[f"{side}_trigger_pull"] = int(
    index_y < prev_index_y[side] and both_not_none
)
# Monitors middle-finger tip (keypoint 8) downward motion
```
**Limitation:** Detects any downward finger motion, not actual trigger engagement.

### 5. Model Asset Paths
All model files hardcoded in CONFIG section:
```python
POSE_MODEL_PATH = "models/yolov8m-pose.pt"
FACE_MODEL_PATH = "models/yolov8n-face.pt"
HAND_MODEL_PATH = "models/hand_landmarker.task"  # MediaPipe .task format
```
Must exist relative to script execution directory.

---

## CSV Output Schema
Frame-indexed structure (one row per frame):
- **Pose:** 17 keypoints × (x, y, vx, vy) + shoulder_width
- **Hands:** L/R, 21 points each × (x, y, vx, vy) + trigger_pull flag per side
- **Gaze:** gaze_dir_x, gaze_dir_y, gaze_on_body (binary)

Velocity (vx, vy) computed as delta from previous frame (normalized pixel space).

---

## Known Issues & Workarounds

### MediaPipe Tasks API Import Failures
**Problem:** `from mediapipe.tasks.python.vision import Image` → ImportError
- **Root:** MediaPipe version misalignment or incomplete Tasks API installation
- **Workaround:** Use wrapper class:
  ```python
  import mediapipe as mp
  # Use mp.Image() directly instead of importing Image class
  mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
  ```

### HandLandmarker Missing HAND_CONNECTIONS Attribute
**Problem:** `mp.tasks.vision.HandLandmarker.HAND_CONNECTIONS` does not exist
- **Root:** MediaPipe Tasks API does not expose HAND_CONNECTIONS constant
- **Solution:** Define locally in script (lines 63–82 in main script)
  ```python
  HAND_CONNECTIONS = [
      (0,1),(1,2),(2,3),(3,4),  # thumb
      (0,5),(5,6),(6,7),(7,8),  # index
      # ... etc
  ]
  ```

### NNPACK Hardware Warnings
**Problem:** `[W119] NNPACK.cpp Could not initialize NNPACK! Reason: Unsupported hardware.`
- **Non-fatal** warning; CPU inference proceeds normally
- **Suppress:** Set `os.environ["PYTORCH_NO_NNPACK"] = "1"` before torch import

---

## Development Workflow

### Running the Pipeline
```bash
cd /home/jon/Desktop/Smart_Coach_Pose_Estimation
python scripts/yolo_pose_with_mediapipe_hands.py
# Reads from input/test_video.mp4
# Outputs: output/output_full.mp4 + output/analytics.csv
```

### Expected Output Files
- `output/output_full.mp4` – Input video with overlaid skeleton, hands, masks, gaze cone
- `output/analytics.csv` – Frame-indexed metrics (human-readable, ML-friendly)

### Configuration Tuning
Edit constants at top of main script:
- `CONF_THRES` – Model confidence threshold (0.3 default)
- `TEMP_ALPHA` – Temporal smoothing strength (0.7 = aggressive smoothing)
- `GAZE_CONE_RAD` – Gaze visualization cone angle
- Visualization overlays: `ALPHA_BODY`, `ALPHA_CONE` (opacity factors)

---

## Design Principles
1. **Separation of Concerns:** Detection ≠ interpretation; measurement ≠ coaching
2. **Graceful Degradation:** Partial metrics (e.g., no hand detection) continue processing
3. **Traceability:** Every metric explainable geometrically; no black-box heuristics
4. **Model Modularity:** Swap YOLOv8 versions or add new detectors without rewriting core loop

---

## Future Improvements (In README)
- Improved firearm orientation via explicit bounding-box detection + orientation fitting
- Multi-person disambiguation (currently max_det=1)
- Camera calibration support for better cross-subject normalization
- Automatic segment detection (draw, presentation, trigger events)

---

## External Dependencies
- **torch, torchvision** – YOLOv8, Mask R-CNN backbone
- **ultralytics (YOLO)** – YOLOv8 pose & face models
- **mediapipe** – Hand & face mesh tasks API
- **opencv (cv2)** – Video I/O, drawing, PnP solver
- **numpy** – Vector math & array ops
- **csv, time** – Standard library

**Environment:** `mediapipe_env/` (activated venv with pre-installed packages)

---

## Quick Reference: Keypoint Indices
**YOLOv8 Pose (17 points):** 0=nose, 5=left shoulder, 6=right shoulder, 11=left hip, 12=right hip, 15=left wrist, 16=right wrist
**MediaPipe Hand (21 points):** 0=wrist, 8=middle-finger-tip, [index for trigger heuristic]
**MediaPipe Face Mesh (468 points):** Only 6 used in PnP (eyes, nose, jaw landmarks)
