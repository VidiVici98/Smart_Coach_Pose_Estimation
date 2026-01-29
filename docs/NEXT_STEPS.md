# Next Steps — Quick Action Guide

**Purpose:** This document provides immediate, actionable next steps for contributors and users of Smart Coach. For the comprehensive roadmap, see [ROADMAP.md](ROADMAP.md).

**Last Updated:** January 2026

---

## 🚀 For Users: Get Started Today

### 1. Run Your First Analysis (10 minutes)

```bash
# Activate environment
source mediapipe_env/bin/activate

# Place your video in data/input/
cp your_video.mp4 data/input/test_video.mp4

# Run the pipeline
python scripts/processing/run_pipeline.py

# Check outputs
ls data/output/
# → output_full.mp4 (annotated video)
# → analytics.csv (285 metrics per frame)
```

### 2. Validate Your Output (2 minutes)

```bash
python scripts/tools/validate_metrics.py data/output/analytics.csv
```

Expected: ✅ 285 fields validated

### 3. Analyze Your Data (15 minutes)

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load your metrics
df = pd.read_csv('data/output/analytics.csv')

# Plot stance width over time
plt.figure(figsize=(12, 4))
plt.plot(df['timestamp'], df['stance_width'])
plt.xlabel('Time (seconds)')
plt.ylabel('Stance Width (pixels)')
plt.title('Stance Consistency Analysis')
plt.savefig('stance_analysis.png')
plt.show()

# Check draw times (if you have multiple presentations)
# Find frames where arms extend
df['total_arm_ext'] = df['L_arm_extension'] + df['R_arm_extension']
presentation_frames = df[df['total_arm_ext'] > 1.5]
print(f"Detected {len(presentation_frames)} presentation frames")
```

### 4. Review Performance (5 minutes)

```bash
# Check processing performance
python scripts/tools/performance_profiler.py --analyze

# Estimate time for longer video
python scripts/tools/performance_profiler.py --estimate --video your_long_video.mp4
```

---

## 👨‍💻 For Contributors: Make an Impact Today

### Quick Wins (1-2 hours each)

#### Option A: Improve Documentation
**What:** Add usage examples to existing docs  
**Why:** Help new users get started faster  
**How:**
1. Pick a doc from `docs/` directory
2. Add a "Quick Example" section
3. Include code snippet + expected output
4. Submit PR

**Files to improve:**
- `docs/USAGE_GUIDE.md` — Add more analysis examples
- `docs/metrics_reference.md` — Add metric interpretation guide
- `docs/DETECTION_ENHANCEMENTS.md` — Add troubleshooting section

#### Option B: Add Unit Tests
**What:** Test metric calculation functions  
**Why:** Prevent regressions, increase confidence  
**How:**
1. Choose a metric calculation (e.g., joint angle)
2. Write test with known inputs/outputs
3. Add to `tests/` directory
4. Run with `pytest`

**Example:**
```python
# tests/test_metrics.py
import numpy as np
from smart_coach.metrics.joint_angles import calculate_elbow_angle

def test_elbow_angle_straight():
    shoulder = np.array([0, 0])
    elbow = np.array([1, 0])
    wrist = np.array([2, 0])
    
    angle = calculate_elbow_angle(shoulder, elbow, wrist)
    assert abs(angle - 180.0) < 1.0, "Straight arm should be ~180°"

def test_elbow_angle_right_angle():
    shoulder = np.array([0, 0])
    elbow = np.array([1, 0])
    wrist = np.array([1, 1])
    
    angle = calculate_elbow_angle(shoulder, elbow, wrist)
    assert abs(angle - 90.0) < 1.0, "Right angle should be ~90°"
```

#### Option C: Add Type Hints
**What:** Add Python type annotations to functions  
**Why:** Improve code clarity and IDE support  
**How:**
1. Pick a Python file in `smart_coach/`
2. Add type hints to function signatures
3. Add return type annotations
4. Submit PR

**Example:**
```python
# Before
def calculate_distance(point1, point2):
    return np.linalg.norm(point1 - point2)

# After
import numpy as np
from numpy.typing import NDArray

def calculate_distance(
    point1: NDArray[np.float64], 
    point2: NDArray[np.float64]
) -> float:
    """Calculate Euclidean distance between two points.
    
    Args:
        point1: First point coordinates (x, y)
        point2: Second point coordinates (x, y)
    
    Returns:
        Distance in pixels
    """
    return float(np.linalg.norm(point1 - point2))
```

---

### Weekend Projects (1-2 days each)

#### Option A: Implement Mask R-CNN Caching ⚡ *HIGH IMPACT*
**What:** Cache body mask for 5-10 frames instead of re-computing every frame  
**Why:** 4x speedup for entire pipeline (Mask R-CNN is bottleneck)  
**How:**
1. Modify `run_pipeline.py` around line 550-600 (Mask R-CNN section)
2. Add frame counter and cache variable
3. Re-use mask for N frames, then refresh
4. Test that output quality is preserved

**Pseudocode:**
```python
# Global variables
mask_cache = None
mask_cache_counter = 0
MASK_CACHE_FRAMES = 5

# In main loop
if mask_cache is None or mask_cache_counter >= MASK_CACHE_FRAMES:
    # Run Mask R-CNN
    mask = run_maskrcnn(frame)
    mask_cache = mask
    mask_cache_counter = 0
else:
    # Reuse cached mask
    mask = mask_cache
    mask_cache_counter += 1
```

**Validation:**
- Compare output CSV with/without caching
- Ensure metrics differ by < 2%
- Measure processing time improvement

#### Option B: Build Draw Detection Algorithm 📊 *HIGH IMPACT*
**What:** Automatically detect draw events (holster → presentation)  
**Why:** Enable automatic drill analysis and draw time measurement  
**How:**
1. Analyze `L_arm_extension` and `R_arm_extension` time series
2. Detect transition from low extension (< 0.5) to high (> 1.0)
3. Measure frames between states
4. Export segment boundaries to CSV

**Pseudocode:**
```python
def detect_draws(df, threshold_low=0.5, threshold_high=1.0):
    """Detect draw events from arm extension data."""
    draws = []
    in_draw = False
    draw_start = None
    
    total_ext = df['L_arm_extension'] + df['R_arm_extension']
    
    for i, ext in enumerate(total_ext):
        if not in_draw and ext > threshold_high:
            # Draw started
            in_draw = True
            draw_start = i
        elif in_draw and ext < threshold_low:
            # Draw ended (returned to holster)
            draws.append({
                'start_frame': draw_start,
                'end_frame': i,
                'duration_frames': i - draw_start,
                'duration_seconds': (i - draw_start) / 30.0  # Assuming 30 FPS
            })
            in_draw = False
    
    return pd.DataFrame(draws)

# Usage
draws = detect_draws(df)
draws.to_csv('data/output/draws.csv', index=False)
print(f"Detected {len(draws)} draw events")
print(f"Average draw time: {draws['duration_seconds'].mean():.2f}s")
```

**Validation:**
- Test on multiple videos with known draw counts
- Manually verify start/end frames are accurate
- Handle edge cases (video starts mid-draw)

#### Option C: Create Coaching Rule Engine 🎓 *HIGH IMPACT*
**What:** Rule-based system that generates coaching feedback from metrics  
**Why:** Make metrics actionable for users  
**How:**
1. Define thresholds for "good" vs "needs improvement"
2. Scan metrics for violations
3. Generate human-readable feedback
4. Export to text or HTML report

**Example:**
```python
# coaching_rules.py
class CoachingRule:
    def __init__(self, name, description, metric, threshold, comparison):
        self.name = name
        self.description = description
        self.metric = metric
        self.threshold = threshold
        self.comparison = comparison
    
    def check(self, df):
        """Check if rule is violated in dataframe."""
        if self.comparison == 'greater':
            violations = df[df[self.metric] > self.threshold]
        elif self.comparison == 'less':
            violations = df[df[self.metric] < self.threshold]
        elif self.comparison == 'abs_greater':
            violations = df[abs(df[self.metric]) > self.threshold]
        
        return violations

# Define rules
RULES = [
    CoachingRule(
        name="Stance Too Narrow",
        description="Your stance is narrower than recommended. Widen your feet to ~shoulder-width for better stability.",
        metric='stance_width',
        threshold=50,  # pixels, adjust based on camera distance
        comparison='less'
    ),
    CoachingRule(
        name="Arm Extension Asymmetry",
        description="Your arms are extending unevenly. Both arms should reach approximately the same distance.",
        metric='arm_extension_diff',  # Need to calculate this
        threshold=0.2,  # 20% difference
        comparison='abs_greater'
    ),
    CoachingRule(
        name="Head Position Inconsistent",
        description="Your head position varies significantly. Focus on consistent head placement for sight alignment.",
        metric='head_pitch',
        threshold=15,  # degrees
        comparison='abs_greater'
    ),
]

def generate_coaching_report(df, rules=RULES):
    """Generate coaching report from metrics."""
    report = []
    
    for rule in rules:
        violations = rule.check(df)
        
        if len(violations) > 0:
            pct = len(violations) / len(df) * 100
            report.append({
                'issue': rule.name,
                'description': rule.description,
                'frequency': f"{pct:.1f}% of frames",
                'example_frames': violations.index[:3].tolist()
            })
    
    return report

# Usage
df = pd.read_csv('data/output/analytics.csv')
df['arm_extension_diff'] = abs(df['L_arm_extension'] - df['R_arm_extension'])

coaching_feedback = generate_coaching_report(df)
for item in coaching_feedback:
    print(f"\n⚠️ {item['issue']}")
    print(f"   {item['description']}")
    print(f"   Occurred: {item['frequency']}")
    print(f"   Example frames: {item['example_frames']}")
```

**Validation:**
- Test on videos with known issues
- Verify feedback matches expert coaching
- Adjust thresholds based on user feedback

---

### Multi-Week Projects (1-4 weeks)

#### Project A: Firearm Detection Integration 🎯
**Goal:** Integrate YOLOv8 firearm detection model  
**Timeline:** 2-3 weeks  
**Skills Needed:** Python, YOLO, OpenCV

**Milestones:**
1. Week 1: Train/fine-tune YOLOv8 on firearm dataset
2. Week 2: Integrate into pipeline, extract bounding box
3. Week 3: Calculate muzzle direction from box + orientation

**Resources:**
- YOLOv8 documentation
- Firearm detection datasets (Roboflow, Open Images)
- Existing `run_pipeline.py` structure

#### Project B: Web Dashboard MVP 📱
**Goal:** Simple web interface for video upload + result viewing  
**Timeline:** 3-4 weeks  
**Skills Needed:** React, Flask/FastAPI, basic backend

**Milestones:**
1. Week 1: Backend API (upload video, trigger processing)
2. Week 2: Frontend (upload form, processing status)
3. Week 3: Result viewer (download CSV, view annotated video)
4. Week 4: Basic visualization (plot key metrics)

**Tech Stack:**
- Backend: Flask or FastAPI
- Frontend: React or Vue.js
- Storage: Local filesystem (for MVP)
- Processing: Trigger `run_pipeline.py` via subprocess

#### Project C: ML Model Training Pipeline 🤖
**Goal:** Train ML models for stance/skill classification  
**Timeline:** 3-4 weeks  
**Skills Needed:** ML (scikit-learn or PyTorch), Python

**Milestones:**
1. Week 1: Collect/label training data (20-50 videos)
2. Week 2: Feature engineering from CSV metrics
3. Week 3: Train classifiers (stance type, skill level)
4. Week 4: Integrate into pipeline, validate accuracy

**Resources:**
- Existing analytics.csv format
- scikit-learn for quick prototyping
- PyTorch for more complex models

---

## 🎯 Priority Recommendations

### If You Have 1 Hour
→ **Add type hints** to one file in `smart_coach/`

### If You Have 4 Hours
→ **Write unit tests** for metric calculations

### If You Have 1 Day
→ **Implement Mask R-CNN caching** (4x speedup!)

### If You Have 1 Week
→ **Build draw detection** or **coaching rule engine**

### If You Have 1 Month
→ **Integrate firearm detection** or **build web dashboard MVP**

---

## 🤝 How to Contribute

1. **Choose a task** from above (or propose your own)
2. **Check existing issues/PRs** to avoid duplication
3. **Create an issue** to discuss your approach
4. **Fork and create a branch** for your work
5. **Submit a PR** with clear description and tests
6. **Iterate based on review** feedback

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📊 Current Status & Gaps

### ✅ What We Have
- Multi-model pose detection pipeline
- 285 comprehensive metrics per frame
- Visualization overlays
- CSV export format
- Basic documentation

### ⏳ What We're Working On
- Performance optimization (Mask R-CNN caching)
- Firearm detection integration
- Coaching insights engine

### 🎯 What We Need Next
- Automatic event segmentation (draws, reloads)
- ML model training data
- Web dashboard for easier access
- Real-time processing prototype
- Mobile application

---

## 📞 Getting Help

- **Questions:** Open a GitHub Discussion
- **Bugs:** Create an Issue with reproduction steps
- **Feature ideas:** Create an Issue tagged "enhancement"
- **Contribution help:** Comment on an Issue or reach out

---

## 📚 Key Documentation

- **[ROADMAP.md](ROADMAP.md)** — Comprehensive development plan
- **[README.md](README.md)** — Project overview and methodology
- **[ENHANCEMENTS_QUICKSTART.md](ENHANCEMENTS_QUICKSTART.md)** — Pipeline enhancements guide
- **[docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)** — How to use the pipeline
- **[docs/metrics_reference.md](docs/metrics_reference.md)** — Metric definitions
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Contribution guidelines

---

**Ready to contribute? Pick a task and let's make Smart Coach better! 🚀**
