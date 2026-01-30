# Technical Reference

Advanced technical documentation for Smart Coach Pose Estimation pipeline internals, enhancements, and architecture.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Detection Systems](#detection-systems)
3. [Metrics and Analytics](#metrics-and-analytics)
4. [Advanced Features](#advanced-features)
5. [Repository Structure](#repository-structure)

---

## Architecture Overview

### Core Pipeline

The Smart Coach pipeline is a **multi-model computer vision system** for analyzing shooter training videos:

```
Input Video → Frame Extraction
           ↓
    Multi-Model Inference:
    - YOLOv8 Pose (17 keypoints)
    - YOLOv8 Face Detection
    - MediaPipe Face Mesh (468 landmarks)
    - MediaPipe Hands (21 landmarks × 2)
    - Mask R-CNN Body Segmentation
           ↓
    Temporal Smoothing (exponential lerp)
           ↓
    Metric Calculation (303 fields)
           ↓
    Output: Video + CSV
```

### Key Design Principles

1. **Temporal Stability** - Exponential smoothing reduces jitter
2. **Scale Invariance** - All metrics normalized by shoulder width
3. **Graceful Degradation** - Partial detections don't crash pipeline
4. **Traceability** - Every metric geometrically explainable

---

## Detection Systems

### 1. Pose Detection (YOLOv8)

**Model:** YOLOv8m-pose (51MB)  
**Output:** 17 keypoints with confidence scores

**Keypoint Indices:**
- 0: Nose
- 5-6: Shoulders (L/R)
- 7-8: Elbows (L/R)
- 9-10: Wrists (L/R)
- 11-12: Hips (L/R)
- 13-14: Knees (L/R)
- 15-16: Ankles (L/R)

**Temporal Smoothing:**
```python
TEMP_ALPHA = 0.7  # 70% previous, 30% new
p_smooth = lerp(prev_pose[i], new_p, TEMP_ALPHA)
```

### 2. Hand Detection (MediaPipe)

**Model:** Hand Landmarker Task (26MB or 0.3MB lightweight)  
**Output:** 21 landmarks per hand

**Key Landmarks:**
- 0: Wrist
- 8: Index finger tip (trigger detection)
- 4, 8, 12, 16, 20: Fingertips

**Trigger Pull Heuristic:**
```python
trigger_pull = index_tip_y < prev_index_tip_y
```

### 3. Face & Gaze (MediaPipe + solvePnP)

**Models:**
- YOLOv8n-face for detection
- MediaPipe Face Mesh for 3D landmarks

**Gaze Calculation:**
1. Extract 6 key facial landmarks
2. Solve 3D head pose via cv2.solvePnP()
3. Calculate torso forward direction (perpendicular to shoulders)
4. Blend: `gaze = (1 - α) * head + α * torso` (α=0.3)
5. Project to 2D screen space

**Gaze-on-Body Check:**
Ray cast from head center along gaze direction → intersect body mask

### 4. Body Segmentation (Mask R-CNN)

**Model:** ResNet-50 FPN backbone  
**Output:** Per-pixel body mask

**Usage:**
- Gaze intersection detection
- Body region isolation
- Background removal (future)

---

## Metrics and Analytics

### Metric Categories (303 Total Fields)

1. **Pose Keypoints** (17 × 5 = 85 fields)
   - x, y coordinates
   - vx, vy velocities
   - confidence scores

2. **Hand Landmarks** (2 hands × 21 × 4 = 168 fields)
   - L/R hand × (x, y, vx, vy)
   - Plus 2 trigger_pull flags

3. **Angles** (10 fields)
   - Joint angles: elbows, shoulders, hips, knees
   - Body lean angle

4. **Gaze** (5 fields)
   - gaze_dir_x, gaze_dir_y
   - gaze_on_body flag
   - head_pitch, head_yaw, head_roll

5. **Derived Metrics** (33 fields)
   - shoulder_width, hip_width, stance_width
   - arm_extension (L/R)
   - hand_distance, grip_symmetry
   - center_of_mass (x, y)
   - wrist/elbow elevations

### Scale Normalization

**All spatial metrics relative to shoulder width:**
```python
shoulder_width = norm(left_shoulder - right_shoulder)
normalized_distance = actual_distance / shoulder_width
```

This ensures metrics transfer across:
- Different subjects
- Different camera distances
- Different resolutions

### CSV Output Format

```csv
frame,timestamp,shoulder_width,kps_0_x,kps_0_y,...,gaze_dir_x,gaze_dir_y,...
0,0.0,183.59,1143.2,308.8,...,0.8,0.6,...
1,0.033,186.18,1143.7,307.1,...,0.82,0.58,...
```

**Frame-indexed** for easy temporal analysis.

---

## Advanced Features

### Firearm Detection

**Status:** Experimental  
**Method:** Bounding box detection + orientation fitting

**Challenges:**
- Occlusion by hands/body
- Small object in frame
- Various firearm types

**Future Work:**
- Dedicated firearm detector
- Muzzle flash detection
- Magazine tracking

### Two-Pass Processing

**Concept:** Process video twice for better temporal consistency

**Pass 1:** Forward pass
- Standard processing
- Store all detections

**Pass 2:** Backward refinement
- Smooth trajectories bidirectionally
- Fill detection gaps
- Reduce jitter further

**Trade-off:** 2× processing time for higher quality

### Coaching Engine (Future)

**Goal:** Automated feedback generation

**Components:**
1. **Segment Detector** - Identify draw/aim/fire phases
2. **Rule Engine** - Check technique rules
3. **Feedback Generator** - Human-readable coaching tips

**Example Rules:**
- "Eyes should track threat before weapon reaches target"
- "Grip should establish by frame X of draw"
- "Muzzle should not cross support hand"

### Model Fine-Tuning (Phase 4)

**Current:** Pre-trained models on generic datasets  
**Goal:** Domain-specific fine-tuning

**Dataset Needs:**
- 1000+ annotated shooter training videos
- Diverse conditions (indoor/outdoor, lighting, backgrounds)
- Multiple shooter types (beginner to expert)

**Fine-Tuning Targets:**
1. YOLOv8 Pose - Better wrist/hand detection with firearms
2. Hand Detector - Grip-specific landmark refinement
3. Face/Gaze - Robust to head turn during draw

---

## Repository Structure

```
Smart_Coach_Pose_Estimation/
├── smart_coach/               # Core library
│   ├── constants/            # Keypoint definitions, configs
│   │   └── pose_landmarks.py # YOLOv8 skeleton structure
│   ├── utils/                # Utility functions
│   └── ...
│
├── scripts/                  # Executable scripts
│   ├── processing/           # Pipeline variants
│   │   ├── run_pipeline.py  # Main pipeline
│   │   ├── run_pipeline_enhanced.py
│   │   └── ...
│   ├── tools/               # Utility scripts
│   └── setup/               # Setup helpers
│
├── data/                    # Data directory (gitignored)
│   ├── input/              # Input videos (test_video.mp4)
│   ├── output/             # Output videos + CSVs
│   ├── models/             # Model files (YOLOv8, MediaPipe)
│   └── datasets/           # Training data (future)
│
├── docs/                    # Documentation
│   ├── README.md
│   ├── SETUP_AND_TROUBLESHOOTING.md
│   ├── TECHNICAL_REFERENCE.md (this file)
│   ├── USAGE_GUIDE.md
│   ├── IMPLEMENTATION_STATUS.md
│   ├── metrics_reference.md
│   └── ROADMAP.md
│
├── tests/                   # Unit tests
├── config/                  # Configuration files
└── requirements.txt         # Python dependencies
```

### Key Files

**smart_coach/constants/pose_landmarks.py**
- Defines YOLOv8 keypoint indices
- Skeleton edge connections for visualization
- MediaPipe compatibility mappings

**scripts/processing/run_pipeline.py**
- Main pipeline script (1076 lines)
- Single-file monolithic design for simplicity
- Imports from smart_coach for constants

**Configuration:**
- All hardcoded at top of run_pipeline.py
- No external config files (for now)
- Future: YAML-based configuration

---

## Performance Characteristics

### Processing Speed

**Hardware Dependent:**
- **CPU (4 cores):** ~1-2 FPS
- **CPU (8 cores):** ~3-4 FPS
- **GPU (CUDA):** ~10-15 FPS

**Bottlenecks:**
1. YOLOv8 Pose inference (~600ms/frame on CPU)
2. Mask R-CNN inference (~400ms/frame on CPU)
3. Face mesh processing (~100ms/frame)

### Accuracy Metrics

**Detection Success Rate:**
- Pose: >95% on well-lit videos
- Hands: ~85% (improves with contrast)
- Gaze: ~80% (sensitive to head angle)

**Temporal Stability:**
- Jitter: <5px after smoothing
- Lost tracks: <1% of frames

---

## Known Limitations

1. **Single Person Only** - max_det=1 in YOLOv8
2. **Trigger Detection is Heuristic** - not semantic understanding
3. **No Firearm Orientation** - bounding box only, not precise angle
4. **Gaze Requires Front/Side View** - fails on back view
5. **Memory Intensive** - 5-6GB RAM minimum

---

## Development Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed timeline.

**Near-Term (Q1 2026):**
- Multi-person support
- Improved trigger detection
- Firearm orientation estimation

**Mid-Term (Q2 2026):**
- Two-pass processing
- Coaching rule engine
- Real-time mode

**Long-Term (Q3+ 2026):**
- Model fine-tuning
- Mobile app
- Cloud API service

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

**Areas Needing Help:**
- Dataset annotation
- Model fine-tuning
- Performance optimization
- Documentation improvements

---

**Last Updated:** 2026-01-30  
**Version:** 1.0  
**For setup instructions, see [SETUP_AND_TROUBLESHOOTING.md](SETUP_AND_TROUBLESHOOTING.md)**
