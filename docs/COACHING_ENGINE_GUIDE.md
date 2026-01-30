# Coaching Insights Engine - User Guide

## Overview

The **Coaching Insights Engine** is a rule-based feedback system that analyzes pose metrics from Smart Coach and generates actionable coaching recommendations. It converts raw biomechanical data into human-readable feedback that shooters can use to improve their form and technique.

## What It Does

The coaching engine:
- ✅ **Evaluates metrics** against evidence-based thresholds
- ✅ **Identifies form issues** automatically (stance, grip, presentation, head position)
- ✅ **Prioritizes feedback** by severity (Critical → High → Medium → Low)
- ✅ **Generates reports** in multiple formats (text, Markdown, HTML)
- ✅ **Provides actionable advice** with specific recommendations

## What It Does NOT Do

- ❌ Replace human coaching or instruction
- ❌ Provide real-time feedback during live fire
- ❌ Detect firearm-specific issues (trigger control, sight picture) - requires additional sensors
- ❌ Generate training plans or progression tracking (coming in future updates)

---

## Quick Start

### 1. Run the Pipeline

First, process your training video to generate metrics:

```bash
python scripts/processing/run_pipeline.py
# Output: data/output/analytics.csv
```

### 2. Generate Coaching Report

```bash
# Text report (console)
python scripts/tools/generate_coaching_report.py data/output/analytics.csv

# HTML report (file)
python scripts/tools/generate_coaching_report.py data/output/analytics.csv \
    --format html --output coaching_report.html

# Markdown report
python scripts/tools/generate_coaching_report.py data/output/analytics.csv \
    --format markdown --output report.md
```

### 3. Review Feedback

Open the generated report and focus on:
1. **High Priority** issues first (major form problems)
2. **Example frames** to see when issues occur
3. **Frequency percentage** to gauge severity

---

## Command Line Usage

### Basic Usage

```bash
python scripts/tools/generate_coaching_report.py [CSV_FILE]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--format` | `-f` | Output format: `text`, `markdown`, or `html` | `text` |
| `--output` | `-o` | Save report to file instead of console | (stdout) |
| `--verbose` | `-v` | Show detailed analysis statistics | (off) |

### Examples

```bash
# Simple text report
python scripts/tools/generate_coaching_report.py data/output/analytics.csv

# HTML report with verbose output
python scripts/tools/generate_coaching_report.py data/output/analytics.csv \
    -f html -o report.html -v

# Markdown for documentation
python scripts/tools/generate_coaching_report.py data/output/analytics.csv \
    -f markdown -o session_notes.md
```

---

## Python API Usage

You can also use the coaching engine programmatically:

### Basic Example

```python
import pandas as pd
from smart_coach.analysis.coaching_engine import CoachingEngine

# Load your analytics CSV
df = pd.read_csv('data/output/analytics.csv')

# Create coaching engine (uses default rules)
engine = CoachingEngine()

# Generate report
report = engine.generate_report(df, output_format='text')
print(report)
```

### Advanced: Custom Rules

```python
from smart_coach.analysis.coaching_engine import (
    CoachingEngine, CoachingRule, Severity, MetricComparison
)

# Define a custom rule
custom_rule = CoachingRule(
    name="custom_stance_check",
    title="Custom Stance Check",
    description="Your custom coaching advice here.",
    metric="stance_width",
    threshold=1.5,
    comparison=MetricComparison.GREATER,
    severity=Severity.LOW,
    min_frames=10,
    frame_percentage=0.15
)

# Create engine with custom rules
engine = CoachingEngine(rules=[custom_rule])
violations = engine.evaluate_all_rules(df)

for v in violations:
    print(f"{v['title']}: {v['percentage']:.1f}% of frames")
```

---

## Coaching Rules Explained

The engine includes **10 default rules** organized by category:

### Safety Rules (Critical Severity)

*Currently placeholder - will be activated when firearm detection is integrated*

- **Muzzle Sweeping Body**: Detects if muzzle direction crosses body mask

### Stance Rules

| Rule | Metric | Threshold | Description |
|------|--------|-----------|-------------|
| **Stance Too Narrow** | `stance_width` | < 0.8 × shoulder width | Feet too close together |
| **Stance Too Wide** | `stance_width` | > 2.0 × shoulder width | Feet too far apart |
| **Excessive Body Lean** | `body_lean_angle` | > ±15 degrees | Forward/backward lean too much |

### Arm Extension & Presentation

| Rule | Metric | Threshold | Description |
|------|--------|-----------|-------------|
| **Incomplete Arm Extension** | `L_arm_extension` | < 0.7 (70%) | Arms not fully extended |
| **Arm Extension Asymmetry** | `arm_extension_diff` | > 0.15 (15%) | Left/right arm extension mismatch |

### Head Position

| Rule | Metric | Threshold | Description |
|------|--------|-----------|-------------|
| **Head Position Inconsistent** | `head_pitch` | > ±12 degrees | Head angle varies too much |

### Joint Angles

| Rule | Metric | Threshold | Description |
|------|--------|-----------|-------------|
| **Elbow Not Locked** | `L_elbow_angle` | < 140 degrees | Excessive elbow bend during presentation |

### Center of Mass

| Rule | Metric | Threshold | Description |
|------|--------|-----------|-------------|
| **COM Drift** | `com_velocity` | > 5 px/frame | Body swaying or unstable |

---

## Severity Levels

Rules are classified by severity to prioritize feedback:

### 🔴 Critical (Red)
**Safety-related issues** that could lead to injury or accidents.
- *Example:* Muzzle sweeping body parts

### 🟠 High (Orange)
**Major form problems** that significantly affect performance or safety.
- *Example:* Incomplete arm extension, inconsistent head position

### 🟡 Medium (Yellow)
**Moderate issues** that reduce effectiveness but aren't dangerous.
- *Example:* Stance too narrow, asymmetric arm extension

### 🟢 Low (Green)
**Minor refinements** that can improve consistency.
- *Example:* Slight COM drift, stance too wide

---

## Understanding Report Output

### Text Report Format

```
================================================================================
SMART COACH - COACHING INSIGHTS REPORT
================================================================================

Video: 150 frames analyzed
Issues Found: 3

🔴 HIGH PRIORITY: 1
🟡 MEDIUM PRIORITY: 2

--------------------------------------------------------------------------------
1. 🔴 Incomplete Arm Extension

   Your arms are not fully extended during presentation. Full extension provides 
   better control, reduces muzzle rise, and improves sight alignment. Focus on 
   pushing the gun out to full extension before breaking the first shot.

   Frequency: 30.0% of frames (45/150)
   Example frames: [0, 1, 2]
--------------------------------------------------------------------------------
```

### Key Sections

1. **Summary**: Total frames and number of issues
2. **Severity Breakdown**: Count by priority level
3. **Detailed Issues**:
   - Title and severity badge
   - Detailed coaching advice
   - Frequency (% of frames affected)
   - Example frame numbers for review

4. **Next Steps**: Actionable recommendations

---

## Customizing Rules

### Rule Parameters

Each rule has the following configurable parameters:

```python
CoachingRule(
    name="rule_identifier",           # Unique ID
    title="User-Facing Title",         # Display name
    description="Detailed advice...",  # Coaching feedback
    metric="csv_column_name",          # Which metric to evaluate
    threshold=1.0,                     # Comparison value
    comparison=MetricComparison.LESS,  # How to compare
    severity=Severity.MEDIUM,          # Priority level
    min_frames=10,                     # Minimum violations to trigger
    frame_percentage=0.15              # Minimum 15% of frames
)
```

### Comparison Types

- `MetricComparison.GREATER`: metric > threshold
- `MetricComparison.LESS`: metric < threshold
- `MetricComparison.ABS_GREATER`: |metric| > threshold
- `MetricComparison.ABS_LESS`: |metric| < threshold
- `MetricComparison.BETWEEN`: low ≤ metric ≤ high
- `MetricComparison.OUTSIDE`: metric < low OR metric > high

### Example: Add a Custom Rule

```python
from smart_coach.analysis.coaching_engine import (
    CoachingEngine, CoachingRule, Severity, MetricComparison
)

# Define new rule for rapid head movement
rapid_head_movement = CoachingRule(
    name="rapid_head_movement",
    title="Head Moving Too Fast",
    description=(
        "Your head is moving rapidly between presentations. "
        "Keep your head still and bring the gun up to your eye level. "
        "This improves target acquisition and sight alignment."
    ),
    metric="head_pitch",  # Or create a "head_velocity" derived metric
    threshold=20.0,
    comparison=MetricComparison.ABS_GREATER,
    severity=Severity.HIGH,
    min_frames=5,
    frame_percentage=0.10
)

# Load default rules and add yours
engine = CoachingEngine()
engine.rules.append(rapid_head_movement)

# Evaluate
df = pd.read_csv('data/output/analytics.csv')
violations = engine.evaluate_all_rules(df)
```

---

## Troubleshooting

### Issue: "No significant issues detected" but I see problems in video

**Possible causes:**
1. Thresholds too lenient - adjust rule thresholds
2. `min_frames` or `frame_percentage` too high - lower these values
3. Missing metrics - check CSV has required columns

**Solution:**
```python
# Lower thresholds for stricter evaluation
engine = CoachingEngine()
for rule in engine.rules:
    if rule.name == "stance_too_narrow":
        rule.threshold = 1.0  # More strict (was 0.8)
        rule.frame_percentage = 0.10  # Lower requirement (was 0.15)
```

### Issue: Too many false positives

**Solution:**
Increase `min_frames` and `frame_percentage` to require more consistent violations:

```python
for rule in engine.rules:
    rule.min_frames = 20  # Require 20+ frames
    rule.frame_percentage = 0.25  # Require 25%+ of video
```

### Issue: Missing metrics in CSV

**Solution:**
Check which columns are in your analytics CSV:

```python
import pandas as pd
df = pd.read_csv('data/output/analytics.csv')
print(df.columns.tolist())
```

If metrics are missing, re-run the pipeline with the latest version.

---

## Best Practices

### 1. Start with Default Rules
Use the default rules first to get familiar with the system before customizing.

### 2. Review Example Frames
Always check the example frames in the annotated video to verify the feedback is accurate.

### 3. Focus on High Priority First
Address critical and high-severity issues before worrying about minor refinements.

### 4. Track Progress Over Time
Save reports for each training session to track improvement:

```bash
# Name reports by date
python scripts/tools/generate_coaching_report.py data/output/analytics.csv \
    -f html -o reports/session_2026-01-30.html
```

### 5. Combine with Expert Coaching
Use the engine as a **supplement** to human instruction, not a replacement. 
Discuss automated feedback with a qualified instructor.

---

## Limitations & Future Improvements

### Current Limitations

1. **No firearm detection** - Cannot directly measure muzzle direction yet
2. **No trigger control analysis** - Requires additional sensors
3. **Camera-dependent** - Some metrics sensitive to camera angle
4. **No temporal patterns** - Doesn't detect draw-to-shot timing yet

### Planned Enhancements

- [ ] Firearm detection integration for actual muzzle direction
- [ ] Event segmentation (per-draw analysis instead of whole video)
- [ ] Trend analysis across multiple sessions
- [ ] ML-based form classification (beginner/intermediate/advanced)
- [ ] Comparative analysis (compare to expert benchmarks)

See [ROADMAP.md](../../ROADMAP.md) for full development plan.

---

## Contributing

Want to add new rules or improve existing ones?

1. Fork the repository
2. Add your rule to `smart_coach/analysis/coaching_engine.py`
3. Test with sample data
4. Submit a pull request with:
   - Rule definition
   - Justification (biomechanics or safety principle)
   - Example violations
   - Test cases

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

---

## FAQ

**Q: Can I use this for competition scoring?**  
A: No. The engine provides training feedback, not objective scoring. Competition scoring requires sanctioned judges.

**Q: How accurate are the recommendations?**  
A: Rules are based on general shooting principles. Individual shooters may have valid reasons for variations (body type, shooting style, etc.). Always consult a qualified instructor.

**Q: Can I disable certain rules?**  
A: Yes. Filter rules before evaluation:
```python
engine = CoachingEngine()
engine.rules = [r for r in engine.rules if r.name != "stance_too_wide"]
```

**Q: Does this work for all shooting disciplines?**  
A: Currently optimized for defensive handgun shooting. Other disciplines may require different thresholds.

**Q: Can I export raw violation data for my own analysis?**  
A: Yes:
```python
violations = engine.evaluate_all_rules(df)
import json
with open('violations.json', 'w') as f:
    json.dump(violations, f, indent=2, default=str)
```

---

## Related Documentation

- **[README.md](../../README.md)** - Project overview
- **[NEXT_STEPS.md](../NEXT_STEPS.md)** - Development roadmap
- **[USAGE_GUIDE.md](./USAGE_GUIDE.md)** - Pipeline usage
- **[TWO_PASS_PROCESSING.md](./TWO_PASS_PROCESSING.md)** - Advanced processing

---

**Questions or feedback?** Open an issue on GitHub!
