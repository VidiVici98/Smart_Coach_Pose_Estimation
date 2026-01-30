# Firearm Detection Guide

## Overview

The **Firearm Detection Module** provides accurate muzzle direction tracking by detecting firearms directly in video frames, rather than relying solely on arm kinematics as a fallback heuristic.

## What It Does

- ✅ **Detects firearms** in video frames using YOLOv8 object detection
- ✅ **Estimates muzzle direction** from bounding box orientation
- ✅ **Fuses with arm kinematics** for robust hybrid approach
- ✅ **Temporal smoothing** for stable detection
- ✅ **Safety checking** (muzzle-body intersection detection)
- ✅ **Visualization overlays** for debugging

## Architecture

### Components

1. **FirearmDetector Class** (`smart_coach/models/firearm_detector.py`)
   - Main detector using YOLOv8
   - Temporal smoothing and buffering
   - Muzzle/grip point estimation
   - Orientation calculation

2. **Fusion Logic**
   - Combines firearm detection with arm kinematics
   - Confidence-based selection
   - Blending for moderate confidence

3. **Safety Checking**
   - Ray-casting from muzzle point
   - Body mask intersection detection
   - Distance-to-body measurement

---

## Quick Start

### 1. Model Setup

**Option A: Use Pre-trained Model (MVP)**

The standard YOLOv8 model can detect some generic weapons:

```bash
# Already included if you ran download_models.py
ls data/models/yolov8n.pt
```

**Option B: Fine-tune on Firearm Dataset (Recommended)**

For better accuracy, fine-tune YOLOv8 on a firearms-specific dataset:

```bash
# Coming soon: training script
python scripts/ml/train_firearm_detector.py
```

### 2. Basic Usage

```python
from smart_coach.models import FirearmDetector
from ultralytics import YOLO

# Initialize
model = YOLO('data/models/yolov8n.pt')
detector = FirearmDetector(
    model=model,
    confidence_threshold=0.4,
    target_classes=['gun', 'handgun', 'pistol', 'firearm', 'weapon']
)

# Detect in frame
detection = detector.detect(frame)

if detection:
    print(f"Detected {detection.class_name} with {detection.confidence:.2f} confidence")
    print(f"Muzzle point: {detection.muzzle_point}")
    print(f"Orientation: {detection.orientation_angle:.1f}°")
    
    # Get muzzle direction vector
    direction = detector.get_muzzle_direction_vector(detection)
    print(f"Direction: {direction}")
```

### 3. Integration with Pipeline

```python
from smart_coach.models import (
    FirearmDetector,
    fuse_firearm_and_arm_estimates,
    check_muzzle_body_intersection
)

# In your processing loop:
for frame in video:
    # 1. Detect firearm
    firearm_detection = firearm_detector.detect(frame)
    firearm_direction = firearm_detector.get_muzzle_direction_vector(firearm_detection)
    
    # 2. Calculate arm-based estimate (existing code)
    arm_direction = calculate_muzzle_vector_from_arms(wrist, elbow, shoulder)
    
    # 3. Fuse estimates
    firearm_conf = firearm_detection.confidence if firearm_detection else 0.0
    muzzle_direction, source = fuse_firearm_and_arm_estimates(
        firearm_direction,
        arm_direction,
        firearm_conf,
        confidence_threshold=0.6
    )
    
    # 4. Check safety
    if muzzle_direction is not None and firearm_detection:
        intersects, distance = check_muzzle_body_intersection(
            firearm_detection.muzzle_point,
            muzzle_direction,
            body_mask
        )
        
        if intersects:
            print(f"⚠️ SAFETY: Muzzle pointing at body (distance: {distance}px)")
    
    # 5. Add to CSV
    csv_row['firearm_detected'] = 1 if firearm_detection else 0
    csv_row['firearm_confidence'] = firearm_conf
    csv_row['muzzle_dir_x'] = muzzle_direction[0] if muzzle_direction else 0
    csv_row['muzzle_dir_y'] = muzzle_direction[1] if muzzle_direction else 0
    csv_row['muzzle_source'] = source  # 'firearm', 'blended', or 'arms'
```

---

## Configuration

### Detector Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `confidence_threshold` | 0.4 | Minimum detection confidence (0-1) |
| `target_classes` | ['gun', 'handgun', ...] | Class names to detect |
| `smoothing_alpha` | 0.7 | Temporal smoothing (0=no smoothing, 1=max smoothing) |
| `buffer_size` | 5 | Number of recent detections to buffer |

### Fusion Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `confidence_threshold` | 0.6 | Use firearm when confidence above this |
| `blend_weight` | 0.7 | Weight for firearm vs arms when blending (0-1) |

### Example Configurations

**High Precision (fewer false positives):**
```python
detector = FirearmDetector(
    model=model,
    confidence_threshold=0.6,  # Higher threshold
    smoothing_alpha=0.8,       # More smoothing
)
```

**High Recall (catch more detections):**
```python
detector = FirearmDetector(
    model=model,
    confidence_threshold=0.3,  # Lower threshold
    smoothing_alpha=0.5,       # Less smoothing
)
```

---

## Fusion Strategy

The system uses a **hybrid approach** to combine firearm detection and arm kinematics:

### Decision Logic

```
If firearm confidence >= 0.6:
    Use firearm direction (high confidence)
Else if firearm confidence >= 0.3:
    Blend firearm (70%) + arms (30%)
Else:
    Use arm kinematics (low/no detection)
```

### Benefits

- ✅ **Robust**: Falls back to arms when firearm detection fails
- ✅ **Accurate**: Uses firearm when confidence is high
- ✅ **Smooth**: Blends during transitions

---

## Muzzle Direction Estimation

### From Bounding Box

The detector estimates muzzle and grip points from the bounding box:

1. **Determine orientation**: Compare width vs height
2. **Identify ends**: 
   - Horizontal: Right end = muzzle, Left end = grip
   - Vertical: Top end = muzzle, Bottom end = grip
3. **Calculate direction**: Vector from grip to muzzle
4. **Normalize**: Convert to unit vector

### Limitations

- Assumes firearm is aligned with bounding box edges
- May be inaccurate for angled firearms
- Future: Use rotated bounding boxes or keypoint detection

---

## Safety Checking

### Muzzle-Body Intersection

The system can detect when the muzzle is pointing at or near the body:

```python
intersects, distance = check_muzzle_body_intersection(
    muzzle_point,
    muzzle_direction,
    body_mask,
    ray_length=200
)

if intersects:
    # Trigger safety warning
    coaching_rule.trigger_critical_safety_issue()
```

**How it works:**
1. Cast ray from muzzle point along direction vector
2. Check intersection with body segmentation mask
3. Return intersection status and distance

**Use in coaching:**
- Enable "muzzle sweeping body" rule
- Generate critical safety warnings
- Log safety violations

---

## Visualization

### Draw Detection Overlay

```python
from smart_coach.models import draw_firearm_detection

# Draw detection on frame
frame_with_overlay = draw_firearm_detection(
    frame,
    detection,
    color=(0, 255, 255),  # Yellow bounding box
    thickness=2
)
```

**Overlay includes:**
- Yellow bounding box around firearm
- Red dot at estimated muzzle point (labeled "M")
- Green dot at estimated grip point (labeled "G")
- Purple arrow showing direction
- Confidence label

---

## CSV Metrics Added

When firearm detection is integrated, these columns are added to analytics.csv:

| Column | Type | Description |
|--------|------|-------------|
| `firearm_detected` | bool | Whether firearm was detected this frame |
| `firearm_confidence` | float | Detection confidence (0-1) |
| `firearm_bbox_x1` | float | Bounding box top-left x |
| `firearm_bbox_y1` | float | Bounding box top-left y |
| `firearm_bbox_x2` | float | Bounding box bottom-right x |
| `firearm_bbox_y2` | float | Bounding box bottom-right y |
| `muzzle_point_x` | float | Estimated muzzle x coordinate |
| `muzzle_point_y` | float | Estimated muzzle y coordinate |
| `muzzle_dir_x` | float | Muzzle direction vector x component |
| `muzzle_dir_y` | float | Muzzle direction vector y component |
| `muzzle_source` | str | 'firearm', 'blended', or 'arms' |
| `muzzle_elevation_deg` | float | Elevation angle from horizontal |
| `muzzle_on_body` | bool | Whether muzzle is pointing at body (safety) |
| `muzzle_body_distance` | float | Distance to body along muzzle ray (if intersecting) |

---

## Training Custom Model

### Option 1: Use Existing Datasets

Public firearm detection datasets:
- **Roboflow**: Search for "gun detection" or "weapon detection"
- **Open Images**: Filter for weapon-related classes
- **Custom**: Collect and label your own training footage

### Option 2: Fine-tune YOLOv8

```python
from ultralytics import YOLO

# Load pre-trained model
model = YOLO('yolov8n.pt')

# Train on your dataset
model.train(
    data='config/firearm_dataset.yaml',  # Dataset config
    epochs=100,
    imgsz=640,
    batch=16,
    name='firearm_detector'
)

# Export for inference
model.export(format='onnx')
```

### Dataset YAML Format

```yaml
train: data/datasets/firearms/train
val: data/datasets/firearms/val

nc: 3  # Number of classes
names: ['handgun', 'rifle', 'shotgun']
```

---

## Troubleshooting

### Issue: No detections found

**Possible causes:**
1. Model doesn't have firearm classes trained
2. Confidence threshold too high
3. Firearms are too small or occluded in video

**Solutions:**
```python
# Lower confidence threshold
detector = FirearmDetector(model, confidence_threshold=0.2)

# Add more target classes
detector.target_classes = ['gun', 'handgun', 'pistol', 'weapon', 
                           'rifle', 'firearm', 'shotgun', 'revolver']

# Check model classes
print(model.names)
```

### Issue: Muzzle direction is inaccurate

**Possible causes:**
1. Bounding box doesn't align with firearm orientation
2. Firearm is angled relative to frame
3. Temporal smoothing too aggressive

**Solutions:**
```python
# Reduce smoothing for faster response
detector.smoothing_alpha = 0.5

# Use fusion with arms to improve accuracy
direction, source = fuse_firearm_and_arm_estimates(
    firearm_dir, arm_dir, confidence, blend_weight=0.6
)
```

### Issue: Too many false positives

**Possible causes:**
1. Confidence threshold too low
2. Model detecting non-firearm objects

**Solutions:**
```python
# Increase confidence threshold
detector.confidence_threshold = 0.6

# Check detection stability
if detector.is_detection_stable(min_consecutive=5):
    # Use detection only if stable for 5+ frames
    process_detection(detection)
```

---

## Performance

### Speed

- **YOLOv8n**: ~1-2ms per frame (GPU), ~10-20ms (CPU)
- **YOLOv8m**: ~3-5ms per frame (GPU), ~30-50ms (CPU)
- **Total pipeline impact**: < 5% with GPU, ~10-15% with CPU

### Optimization Tips

1. **Use smaller model**: YOLOv8n vs YOLOv8m
2. **Lower resolution**: Resize frames before detection
3. **Skip frames**: Detect every N frames, interpolate between
4. **Batch processing**: Process multiple frames at once

```python
# Skip-frame optimization
frame_counter = 0
last_detection = None

for frame in video:
    if frame_counter % 3 == 0:  # Detect every 3rd frame
        last_detection = detector.detect(frame)
    
    # Use last_detection for this frame
    process(last_detection)
    frame_counter += 1
```

---

## Future Enhancements

### Planned Features

- [ ] Rotated bounding box support for angled firearms
- [ ] Firearm keypoint detection (muzzle, grip, sights)
- [ ] Multi-firearm tracking (primary vs secondary weapon)
- [ ] Firearm type classification (handgun, rifle, shotgun)
- [ ] Magazine detection (reload analysis)
- [ ] Slide position tracking (shot detection)

### Integration Opportunities

- **Recoil analysis**: Correlate with firearm detection
- **Draw timing**: Start when firearm first detected
- **Holster detection**: Detect when firearm returns to holster
- **Safety auditing**: Comprehensive muzzle discipline scoring

---

## Related Documentation

- **[README.md](../../README.md)** - Project overview
- **[COACHING_ENGINE_GUIDE.md](./COACHING_ENGINE_GUIDE.md)** - Coaching system
- **[NEXT_STEPS_IMPLEMENTATION.md](../NEXT_STEPS_IMPLEMENTATION.md)** - Development roadmap

---

**Questions or issues?** Open a GitHub issue or refer to the troubleshooting section above.
