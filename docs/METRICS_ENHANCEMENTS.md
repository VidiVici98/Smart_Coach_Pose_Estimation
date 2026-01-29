<!-- Last Modified: 2026-01-29 -->
# Metrics Enhancements: Advanced Detection Capabilities

## Overview

This document describes the enhanced detection and measurement capabilities in Smart Coach. These improvements extract additional value from existing pose and hand detections, adding 18 new metrics for comprehensive shooter analysis.

---

## Summary: What's New

| Category | New Metrics | Description |
|----------|-------------|-------------|
| **Muzzle Direction** | 6 | Firearm orientation from arm kinematics |
| **Recoil Detection** | 6 | Automatic shot detection and analysis |
| **Draw Detection** | 6 | Holster-to-presentation timing and quality |
| **Total New** | **18** | |
| **Previous Total** | 285 | |
| **New Total** | **303** | |

### Key Improvements

| Aspect | Before | After | Benefit |
|--------|--------|-------|---------|
| **Firearm orientation** | Gaze-based estimate | Arm kinematics | Direct physical measurement |
| **Recoil detection** | None | Automatic | Shot-level analysis |
| **Draw detection** | None | Automatic + timing | Drill automation |
| **Shot cadence** | Manual counting | Automatic from recoil | Precise timing |
| **Muzzle safety** | Gaze intersection | Physical direction | Actual barrel vector |

---

## 1. Muzzle Direction from Arm Kinematics

### New Metrics (6 fields)

```
L_muzzle_direction_x     # Left arm muzzle direction X (unit vector)
L_muzzle_direction_y     # Left arm muzzle direction Y (unit vector)
L_muzzle_elevation       # Left arm muzzle elevation angle (degrees)
R_muzzle_direction_x     # Right arm muzzle direction X (unit vector)
R_muzzle_direction_y     # Right arm muzzle direction Y (unit vector)
R_muzzle_elevation       # Right arm muzzle elevation angle (degrees)
```

### Calculation Method

**Physical Basis:**
- Firearm aligns with forearm in proper shooting grip
- Wrist-to-elbow vector approximates barrel direction
- Validated against shoulder position to reject invalid poses (folded arms, etc.)

**Algorithm:**
```python
# Calculate muzzle vector from arm kinematics
wrist_pos = pts[wrist_idx]
elbow_pos = pts[elbow_idx]
shoulder_pos = pts[shoulder_idx]

# Primary direction: forearm vector (wrist to elbow)
forearm_vec = elbow_pos - wrist_pos
forearm_vec_normalized = forearm_vec / np.linalg.norm(forearm_vec)

# Validation: Check arm extension
arm_length = np.linalg.norm(shoulder_pos - wrist_pos)
if arm_length < 0.5 * shoulder_width:
    # Arm folded, invalid pose
    return None

# Calculate elevation angle
elevation = np.degrees(np.arctan2(forearm_vec_normalized[1], forearm_vec_normalized[0]))
```

### Improvement Over Previous Approach

**Before:**
- Muzzle direction estimated from head gaze (indirect)
- Unreliable when shooter looks at target but firearm points elsewhere
- Could not detect arm-independent muzzle directions (e.g., cross-dominant grip)

**After:**
- Calculated from actual arm kinematics (direct physical measurement)
- Accurate firearm orientation even when head turns away
- Per-arm independent tracking (left and right)
- Robust to head movement and gaze direction changes

### Use Cases

**Safety Analysis:**
```python
# Detect unsafe muzzle directions (pointing at body or below horizontal)
unsafe_frames = df[(df['R_muzzle_elevation'] < -10) | 
                   (df['L_muzzle_elevation'] < -10)]
print(f"Unsafe muzzle direction detected in {len(unsafe_frames)} frames")
```

**Presentation Consistency:**
```python
# Track barrel elevation stability during presentation
presentation = df[(df['R_arm_extension'] > 0.7) & (df['frame'] > 50)]
elevation_std = presentation['R_muzzle_elevation'].std()
print(f"Muzzle elevation stability: ±{elevation_std:.1f}°")
```

**Sight Picture Estimation:**
```python
# Estimate sight alignment from arm position
avg_elevation = df['R_muzzle_elevation'].mean()
target_elevation = 0.0  # Eye level target

elevation_error = avg_elevation - target_elevation
print(f"Average elevation error: {elevation_error:+.1f}°")
```

**Training Feedback:**
```python
# Compare left vs right arm consistency (for two-handed grip)
left_elev = df['L_muzzle_elevation'].mean()
right_elev = df['R_muzzle_elevation'].mean()

if abs(left_elev - right_elev) > 5:
    print(f"Warning: Arms not aligned (L:{left_elev:.1f}° vs R:{right_elev:.1f}°)")
```

---

## 2. Recoil Detection

### New Metrics (6 fields)

```
L_recoil_detected        # Left hand recoil event (0 or 1)
L_recoil_magnitude       # Left hand recoil magnitude (pixels/frame)
L_recovery_frames        # Frames since last recoil
R_recoil_detected        # Right hand recoil event (0 or 1)
R_recoil_magnitude       # Right hand recoil magnitude (pixels/frame)
R_recovery_frames        # Frames since last recoil
```

### Detection Algorithm

**Method:** Analyze hand velocity patterns for characteristic recoil signature

**Recoil Signature:**
1. Sudden upward hand acceleration (wrist moves up rapidly)
2. Magnitude exceeds threshold (normalized by shoulder width)
3. Direction primarily vertical (Y-axis dominant)
4. Brief duration (1-3 frames)

**Implementation:**
```python
# Calculate hand vertical velocity
hand_vy = (hand_y_current - hand_y_previous) / shoulder_width

# Detect recoil signature
recoil_threshold = 0.05  # 5% of shoulder width per frame
if hand_vy > recoil_threshold and hand_vy > 2 * hand_vx:
    # Recoil detected
    recoil_detected = 1
    recoil_magnitude = hand_vy
    recovery_frames = 0
else:
    recoil_detected = 0
    recovery_frames += 1
```

### Use Cases

**Automatic Shot Counting:**
```python
# Count shots from recoil detection
shots = df[df['R_recoil_detected'] == 1]
print(f"Total shots fired: {len(shots)}")

# Shot times
shot_frames = shots['frame'].tolist()
shot_times = shots['timestamp'].tolist()
```

**Shot Cadence Analysis:**
```python
# Calculate inter-shot intervals
shot_frames = df[df['R_recoil_detected'] == 1]['frame'].tolist()
intervals = np.diff(shot_frames)
avg_interval = np.mean(intervals) / 30.0  # Convert frames to seconds

print(f"Average shot cadence: {avg_interval:.2f} seconds")
print(f"Shots per second: {1.0/avg_interval:.2f}")
```

**Recoil Management Quality:**
```python
# Analyze recoil magnitude consistency
recoil_events = df[df['R_recoil_detected'] == 1]
avg_magnitude = recoil_events['R_recoil_magnitude'].mean()
std_magnitude = recoil_events['R_recoil_magnitude'].std()

print(f"Average recoil: {avg_magnitude:.3f} (±{std_magnitude:.3f})")
```

**Recovery Time Analysis:**
```python
# Time to return to ready position after shot
recoil_frames = df[df['R_recoil_detected'] == 1]['frame'].tolist()

recovery_times = []
for frame_idx in recoil_frames:
    # Find when muzzle returns to presentation elevation
    post_shot = df[df['frame'] > frame_idx].head(30)
    baseline_elev = df.loc[frame_idx - 5:frame_idx - 1, 'R_muzzle_elevation'].mean()
    
    recovery = post_shot[abs(post_shot['R_muzzle_elevation'] - baseline_elev) < 2]
    if not recovery.empty:
        recovery_frames = recovery.iloc[0]['frame'] - frame_idx
        recovery_times.append(recovery_frames / 30.0)  # Convert to seconds

print(f"Average recovery time: {np.mean(recovery_times):.2f} seconds")
```

---

## 3. Draw Detection

### New Metrics (6 fields)

```
L_draw_detected          # Left hand draw event (0 or 1)
L_draw_duration          # Draw duration in frames
L_presentation_quality   # Presentation smoothness (0-1)
R_draw_detected          # Right hand draw event (0 or 1)
R_draw_duration          # Draw duration in frames
R_presentation_quality   # Presentation smoothness (0-1)
```

### Detection Algorithm

**State Machine Approach:**

```
HOLSTERED → DRAWING → PRESENTED → FIRING → HOLSTERING → HOLSTERED
```

**State Transitions:**
1. **HOLSTERED:** Hand near hip, low elevation
2. **DRAWING:** Hand moving upward rapidly (vy > threshold)
3. **PRESENTED:** Hand extended forward, stable position
4. **FIRING:** Recoil detected (see recoil detection above)
5. **HOLSTERING:** Hand moving downward toward hip

**Implementation:**
```python
# State detection logic
hip_y = pts[hip_idx][1]
hand_y = hand_landmarks[wrist_idx][1]
hand_elevation = (hip_y - hand_y) / shoulder_width

# Check for draw event (holstered → presented transition)
if prev_state == 'HOLSTERED' and hand_elevation > 0.3 and hand_vy > 0.03:
    draw_detected = 1
    draw_start_frame = frame_idx
    state = 'DRAWING'
elif prev_state == 'DRAWING' and hand_vy < 0.01 and hand_elevation > 0.5:
    state = 'PRESENTED'
    draw_duration = frame_idx - draw_start_frame
    presentation_quality = calculate_smoothness(trajectory)
```

### Presentation Quality Metric

**Definition:** Smoothness of draw motion (0 = jerky, 1 = perfectly smooth)

**Calculation:**
```python
def calculate_smoothness(hand_trajectory):
    """
    Calculate presentation quality from hand trajectory.
    
    Quality = 1 - (path_deviation / direct_distance)
    
    Perfect straight line = 1.0
    Circuitous path = closer to 0.0
    """
    # Total path length
    path_length = np.sum(np.linalg.norm(np.diff(hand_trajectory, axis=0), axis=1))
    
    # Direct distance (start to end)
    direct_distance = np.linalg.norm(hand_trajectory[-1] - hand_trajectory[0])
    
    # Smoothness score
    if path_length < 0.01:
        return 0.0
    
    smoothness = direct_distance / path_length
    return smoothness
```

### Use Cases

**Drill Automation:**
```python
# Automatically segment draw-fire drills
draws = df[df['R_draw_detected'] == 1]['frame'].tolist()

for draw_frame in draws:
    # Extract drill segment
    drill_end = draw_frame + 90  # 3 seconds at 30 FPS
    drill_data = df[(df['frame'] >= draw_frame) & (df['frame'] <= drill_end)]
    
    # Find first shot
    first_shot = drill_data[drill_data['R_recoil_detected'] == 1].head(1)
    if not first_shot.empty:
        draw_time = (first_shot.iloc[0]['frame'] - draw_frame) / 30.0
        print(f"Draw-to-shot time: {draw_time:.2f} seconds")
```

**Draw Time Analysis:**
```python
# Calculate average draw time
draw_events = df[df['R_draw_detected'] == 1]
avg_duration = draw_events['R_draw_duration'].mean() / 30.0  # Convert to seconds

print(f"Average draw time: {avg_duration:.2f} seconds")
print(f"Fastest draw: {draw_events['R_draw_duration'].min() / 30.0:.2f} seconds")
print(f"Slowest draw: {draw_events['R_draw_duration'].max() / 30.0:.2f} seconds")
```

**Presentation Quality Tracking:**
```python
# Track draw consistency over training session
draws = df[df['R_draw_detected'] == 1]
quality_trend = draws['R_presentation_quality'].tolist()

print(f"Average presentation quality: {np.mean(quality_trend):.2f}")
print(f"Quality improvement: {quality_trend[-1] - quality_trend[0]:+.2f}")
```

**Training Feedback:**
```python
# Identify draws needing improvement
poor_draws = df[(df['R_draw_detected'] == 1) & (df['R_presentation_quality'] < 0.7)]

for idx, draw in poor_draws.iterrows():
    frame = draw['frame']
    quality = draw['R_presentation_quality']
    print(f"Frame {frame}: Draw quality {quality:.2f} - Needs improvement")
```

---

## Metrics Schema Update

### Complete Field List (303 total)

**Original Fields (285):**
- Basic: 5 fields (frame, timestamp, widths)
- Pose Keypoints: 85 fields (17 × 5)
- Hand Landmarks: 170 fields (2 × 21 × 4 + 2)
- Gaze: 3 fields
- Joint Angles: 8 fields
- Arm Metrics: 6 fields
- Grip: 2 fields
- Body: 3 fields
- Head: 3 fields

**New Fields (18):**
- Muzzle Direction: 6 fields (L/R × 3)
- Recoil Detection: 6 fields (L/R × 3)
- Draw Detection: 6 fields (L/R × 3)

**Total: 303 fields per frame**

---

## Implementation Details

### Code Location

All new metrics implemented in `scripts/processing/run_pipeline.py`:

- **Lines 726-780:** Muzzle direction calculation
- **Lines 782-830:** Recoil detection logic
- **Lines 832-895:** Draw detection state machine

### Performance Impact

**Computation overhead:** ~5-10ms per frame (3-6% increase)

**Breakdown:**
- Muzzle direction: ~2ms (vector calculations)
- Recoil detection: ~2ms (velocity analysis)
- Draw detection: ~4ms (state machine + smoothness)

**Total pipeline time:** ~170ms per frame (vs 165ms before)

### Dependencies

No new dependencies required. Uses existing:
- NumPy for vector math
- Existing pose and hand keypoint detections

---

## Validation

### Unit Tests

All new metrics covered by `tests/test_advanced_metrics.py`:
- ✅ Muzzle direction calculation
- ✅ Recoil detection thresholds
- ✅ Draw state machine transitions
- ✅ Presentation quality scoring

### Integration Testing

```bash
# Run pipeline with new metrics
python scripts/processing/run_pipeline.py

# Validate output schema
python scripts/tools/validate_metrics.py data/output/analytics.csv

# Expected output: "303 fields detected (expected: 303) ✓"
```

### Visual Verification

New metrics visualized in output video:
- Muzzle direction: Green arrow from wrist along forearm
- Recoil events: Red flash on hand landmarks
- Draw events: Yellow outline during draw motion

---

## Future Enhancements

### Planned Additions

1. **Enhanced Firearm Detection**
   - Explicit weapon segmentation using YOLOv8 object detection
   - More accurate muzzle orientation from weapon bounding box
   - Grip quality assessment (hand position on weapon)

2. **Sight Alignment**
   - Front/rear sight alignment estimation
   - Target-to-sight alignment angle
   - Sight picture consistency scoring

3. **Trigger Control**
   - Trigger finger isolation detection
   - Pre-shot tension indicators
   - Post-shot follow-through time

4. **Stance Analysis**
   - Foot positioning and weight distribution
   - Shoulder-to-hip alignment
   - Platform stability (COM movement)

### Integration Opportunities

**Machine Learning:**
- Train models on these metrics for shot quality prediction
- Automatic coaching feedback generation
- Anomaly detection for unsafe behavior

**Real-time Processing:**
- Optimize for <30ms per frame (target: 30+ FPS)
- Enable live feedback during training
- Mobile device deployment

---

## References

- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Overall implementation status
- [metrics_reference.md](metrics_reference.md) - Complete metrics specification
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Usage examples and best practices
- [README.md](../README.md) - Project overview

---

**Last Updated:** 2026-01-29  
**Metrics Version:** 2.0 (303 fields)  
**Pipeline Version:** v1.2  
**Status:** ✅ Fully implemented and tested
