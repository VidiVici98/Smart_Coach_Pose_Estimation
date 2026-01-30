# Smart Coach Output Visualization Guide

## What You'll See When Pipeline Runs

### Output Video Overlays

The processed video will have multiple overlays showing detected features:

```
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUT VIDEO                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  [Frame: 42/150]                           [30 FPS]   │    │
│  │                                                         │    │
│  │              ●  ← Head (red circle)                    │    │
│  │              │                                          │    │
│  │         ●────┼────●  ← Shoulders (green)              │    │
│  │              │                                          │    │
│  │      ●───────●───────●  ← Arms extended               │    │
│  │    (green)   │   (green)                              │    │
│  │     │        │        │                                │    │
│  │     ●        │        ●  ← Elbows                     │    │
│  │              │                                          │    │
│  │         ●────┴────●  ← Hips (blue)                    │    │
│  │         │         │                                     │    │
│  │         ●         ●  ← Knees (blue)                   │    │
│  │         │         │                                     │    │
│  │         ●         ●  ← Ankles (blue)                  │    │
│  │                                                         │    │
│  │  HAND LANDMARKS:                                       │    │
│  │    ● ● ● ● ●  ← Left hand (21 points)                │    │
│  │    ● ● ● ● ●  ← Right hand (21 points)               │    │
│  │                                                         │    │
│  │  FIREARM DETECTION:                                    │    │
│  │    ┌─────────────┐  ← Yellow bounding box             │    │
│  │    │   [M] ────→ │  ← Muzzle point (red) + arrow     │    │
│  │    │    [G]      │  ← Grip point (green)             │    │
│  │    └─────────────┘                                     │    │
│  │    Conf: 0.85                                          │    │
│  │                                                         │    │
│  │  GAZE DIRECTION:                                       │    │
│  │    ●──────→  ← Head with gaze cone (purple)          │    │
│  │                                                         │    │
│  │  BODY MASK: [Light blue overlay on body]             │    │
│  │                                                         │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Legend

**Color Coding:**
- 🔴 **Red:** Head, nose, muzzle point
- 🟢 **Green:** Arms, shoulders, grip point
- 🔵 **Blue:** Legs, hips, body
- 🟡 **Yellow:** Firearm bounding box
- 🟣 **Purple:** Gaze direction, arrows
- 💙 **Light Blue:** Body mask (semi-transparent)

**Labels:**
- `[M]` - Muzzle point
- `[G]` - Grip point
- `Frame: X/Y` - Current frame / total frames
- `Conf: 0.XX` - Detection confidence

### CSV Output Sample

The analytics.csv will have ~295 columns per frame:

```csv
frame,nose_x,nose_y,L_shoulder_x,L_shoulder_y,...,firearm_detected,firearm_confidence,muzzle_point_x,muzzle_point_y,...
0,320.5,150.2,280.1,180.5,...,1,0.85,420.3,175.8,...
1,320.7,150.3,280.2,180.6,...,1,0.87,421.1,175.9,...
2,321.0,150.5,280.3,180.7,...,1,0.84,421.8,176.0,...
...
```

**Key Columns:**

**Pose (17 keypoints × 4 values = 68 columns):**
- nose_x, nose_y, nose_vx, nose_vy
- L_shoulder_x, L_shoulder_y, L_shoulder_vx, L_shoulder_vy
- ... (15 more keypoints)

**Hands (42 landmarks × 4 values = 168 columns):**
- L_hand_0_x, L_hand_0_y, L_hand_0_vx, L_hand_0_vy
- ... (20 more per hand)

**Gaze (4 columns):**
- gaze_dir_x, gaze_dir_y
- gaze_on_body
- head_orientation_angle

**Firearm (14 columns):**
- firearm_detected
- firearm_confidence
- firearm_bbox_x1, y1, x2, y2
- muzzle_point_x, muzzle_point_y
- L_muzzle_direction_x, y
- R_muzzle_direction_x, y
- L_muzzle_elevation
- R_muzzle_elevation
- L_muzzle_source, R_muzzle_source
- muzzle_on_body
- muzzle_body_distance

**Advanced Metrics (40+ columns):**
- stance_width
- body_lean_angle
- center_of_mass_x, y
- L_arm_extension, R_arm_extension
- L_elbow_angle, R_elbow_angle
- draw_detected, recoil_detected
- grip_symmetry
- ... and more

### Coaching Report Sample

#### Text Format:
```
================================================================================
SMART COACH - COACHING REPORT
================================================================================
Session: test_video.mp4
Total Frames: 150 (5.0 seconds @ 30 fps)
Generated: 2026-01-30 10:00:00

================================================================================
SUMMARY
================================================================================
Issues Detected: 3
  🔴 Critical: 1
  🟡 Medium: 2
  
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
⚠️  CRITICAL SAFETY ISSUES DETECTED: 1
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

IMMEDIATE ACTION REQUIRED!
These issues represent serious safety violations.

================================================================================
CRITICAL ISSUES
================================================================================

1. 🔴 🔴 CRITICAL: Muzzle Sweeping Body
   Occurred in 3.3% of frames (5 frames)
   Example frames: [45, 67, 89, 101, 123]
   
   → DESCRIPTION:
   Your firearm muzzle is pointing at or very close to your body. This is
   a CRITICAL safety violation that must be addressed immediately.
   
   → RECOMMENDATION:
   • STOP - Do not continue live-fire training
   • Review muzzle discipline with a certified instructor
   • Practice muzzle awareness with dry fire
   • Ensure muzzle always points in a safe direction
   • Review the four rules of firearm safety

================================================================================
HIGH PRIORITY ISSUES
================================================================================

(None detected)

================================================================================
MEDIUM PRIORITY ISSUES
================================================================================

2. 🟡 Incomplete Arm Extension
   Frequency: 45.0% of frames (68 frames)
   Average extension: 0.72 (target: > 0.85)
   
   → DESCRIPTION:
   Your arms are not fully extending during presentation. Full extension
   provides better recoil control and more consistent accuracy.
   
   → RECOMMENDATION:
   • Focus on pushing the gun out to full arm extension
   • Practice dry fire with emphasis on complete extension
   • Check for proper grip that allows full extension
   • Ensure shooting stance allows natural extension

3. 🟡 Excessive Body Lean
   Frequency: 30.0% of frames (45 frames)
   Average lean: 12.5° (target: < 10°)
   
   → RECOMMENDATION:
   • Focus on maintaining an upright, balanced stance
   • Distribute weight evenly between both feet
   • Engage core muscles for stability

================================================================================
NEXT STEPS
================================================================================

CRITICAL ACTION REQUIRED:
⚠️  Address all CRITICAL safety issues immediately before continuing training.
   Work with a certified instructor to review safety protocols.

For medium priority issues:
  • Practice recommended drills
  • Film yourself and compare to proper form
  • Work with a coach for detailed feedback
  • Reassess after focused practice

================================================================================
```

#### HTML Format:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Smart Coach - Coaching Report</title>
    <style>
        .critical-alert {
            background: #ffebee;
            border: 3px solid #c62828;
            padding: 20px;
            margin: 20px 0;
        }
        .critical-badge {
            background: #c62828;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>🏋️ Smart Coach - Coaching Report</h1>
    
    <div class="critical-alert">
        <h2>⚠️ CRITICAL SAFETY ISSUES DETECTED: 1</h2>
        <p><strong>IMMEDIATE ACTION REQUIRED!</strong></p>
        <p>These issues represent serious safety violations.</p>
    </div>
    
    <h2>Critical Issues</h2>
    <div class="issue-card critical">
        <h3><span class="critical-badge">CRITICAL</span> Muzzle Sweeping Body</h3>
        <p><strong>Occurred in:</strong> 3.3% of frames (5 frames)</p>
        <p><strong>Example frames:</strong> 45, 67, 89, 101, 123</p>
        
        <h4>Description:</h4>
        <p>Your firearm muzzle is pointing at or very close to your body...</p>
        
        <h4>Recommendations:</h4>
        <ul>
            <li>STOP - Do not continue live-fire training</li>
            <li>Review muzzle discipline with certified instructor</li>
            <li>Practice muzzle awareness with dry fire</li>
        </ul>
    </div>
    
    <!-- More issues... -->
</body>
</html>
```

### Expected Screenshot

When you run the pipeline and extract a frame, you should see:

**Frame Components:**
1. ✅ Original video frame
2. ✅ Skeleton overlay (17 keypoints connected)
3. ✅ Hand landmarks (42 points, both hands)
4. ✅ Head pose/gaze direction (cone)
5. ✅ Firearm detection box (yellow rectangle)
6. ✅ Muzzle point marker (red dot labeled "M")
7. ✅ Grip point marker (green dot labeled "G")
8. ✅ Direction arrow (purple)
9. ✅ Body mask (light blue overlay)
10. ✅ Frame counter and metadata

**Screenshot Location:**
After running pipeline:
```bash
ffmpeg -i data/output/output_full.mp4 -vframes 1 -ss 00:00:02 \
  data/output/screenshot.png
```

Or use any video player to view and screenshot the output video.

### File Sizes (Typical)

**For 1 minute video @ 1080p, 30fps:**
- Input: ~100 MB
- Output video: ~150 MB (with overlays)
- CSV: ~2-3 MB
- HTML report: ~50 KB

**For 10 second test:**
- Input: ~15 MB
- Output video: ~25 MB
- CSV: ~400 KB
- HTML report: ~10 KB

---

## How to View Results

### 1. Video Player
```bash
# Linux
ffplay data/output/output_full.mp4

# Mac
open data/output/output_full.mp4

# Windows
start data/output/output_full.mp4
```

### 2. Extract Screenshots
```bash
# Extract frame at 2 seconds
ffmpeg -i data/output/output_full.mp4 -vframes 1 -ss 00:00:02 \
  data/output/screenshot_2s.png

# Extract frame at 5 seconds
ffmpeg -i data/output/output_full.mp4 -vframes 1 -ss 00:00:05 \
  data/output/screenshot_5s.png

# Extract multiple frames (every 1 second)
ffmpeg -i data/output/output_full.mp4 -vf fps=1 \
  data/output/screenshot_%03d.png
```

### 3. View CSV
```bash
# View first few rows
head -n 5 data/output/analytics.csv

# Open in spreadsheet
# Excel, LibreOffice, Google Sheets can all open CSV files
```

### 4. View Report
```bash
# Text report (console)
cat coaching_report.txt

# HTML report (browser)
open coaching_report.html  # Mac
xdg-open coaching_report.html  # Linux
start coaching_report.html  # Windows
```

---

## Summary

**When pipeline runs successfully, you will have:**

1. ✅ **Annotated video** with all overlays
2. ✅ **CSV file** with 295 metrics per frame
3. ✅ **Coaching report** with actionable feedback
4. ✅ **Screenshots** showing detected features

**All outputs will be in:**
- `data/output/output_full.mp4`
- `data/output/analytics.csv`
- `data/output/coaching_report.html` (after generating report)

**Ready to test!** Just add your video to `data/input/test_video.mp4` and run the pipeline.
