# Using Custom Agents with Smart Coach

## Quick Start

The Smart Coach repository now has **three specialized AI agents** that can help you work more effectively with the codebase.

## Agent Overview

### 🎯 Computer Vision Pipeline Specialist
**File:** `.github/agents/cv_pipeline_specialist.md`

Your go-to expert for anything related to the pose estimation pipeline, model integration, and metric calculations.

**When to use:**
```
"As the Computer Vision Pipeline Specialist, add elbow angle tracking to the pipeline"
"Help me integrate a new YOLOv8 model variant"
"Fix the temporal smoothing for hand landmarks"
"Optimize the frame processing speed"
```

---

### 🧪 Python Testing & Code Quality Expert
**File:** `.github/agents/python_testing_expert.md`

Your testing and code quality specialist who ensures robust, well-tested code.

**When to use:**
```
"As the Python Testing Expert, write comprehensive tests for the gaze detection"
"Debug the import error in test_maskrcnn_cache.py"
"Set up GitHub Actions CI/CD for this repo"
"Profile the pipeline and identify bottlenecks"
```

---

### 📖 Documentation & Setup Specialist
**File:** `.github/agents/documentation_specialist.md`

Your documentation expert who makes complex setup and usage crystal clear.

**When to use:**
```
"As the Documentation Specialist, update the README with the new features"
"Create a troubleshooting guide for MediaPipe errors"
"Write a tutorial for adding custom metrics"
"Help me set up the development environment on Windows"
```

---

## Example Workflows

### Adding a New Feature

1. **Design Phase** (Documentation Specialist)
   ```
   "As the Documentation Specialist, outline what documentation 
   would be needed for an elbow angle tracking feature"
   ```

2. **Implementation Phase** (CV Pipeline Specialist)
   ```
   "As the Computer Vision Pipeline Specialist, implement elbow angle 
   tracking in run_pipeline.py with proper temporal smoothing and 
   normalization"
   ```

3. **Testing Phase** (Python Testing Expert)
   ```
   "As the Python Testing Expert, write comprehensive tests for 
   the elbow angle tracking feature"
   ```

4. **Documentation Phase** (Documentation Specialist)
   ```
   "As the Documentation Specialist, document the new elbow angle 
   feature in the README and add usage examples"
   ```

---

### Debugging an Issue

1. **Reproduce** (Python Testing Expert)
   ```
   "As the Python Testing Expert, help me create a minimal test case 
   that reproduces the pose detection failure"
   ```

2. **Fix** (CV Pipeline Specialist)
   ```
   "As the Computer Vision Pipeline Specialist, fix the pose detection 
   failure when the subject is partially out of frame"
   ```

3. **Verify** (Python Testing Expert)
   ```
   "As the Python Testing Expert, verify the fix works and add a 
   regression test"
   ```

---

### Onboarding New Contributors

1. **Setup** (Documentation Specialist)
   ```
   "As the Documentation Specialist, help me set up the development 
   environment on Ubuntu 22.04"
   ```

2. **Code Review** (Python Testing Expert)
   ```
   "As the Python Testing Expert, review this pull request for code 
   quality and test coverage"
   ```

3. **Feature Guidance** (CV Pipeline Specialist)
   ```
   "As the Computer Vision Pipeline Specialist, explain how temporal 
   smoothing works in the pipeline and why it's critical"
   ```

---

## Best Practices

### 1. Choose the Right Agent
Match your task to the agent's expertise:
- Pipeline code changes → CV Pipeline Specialist
- Writing tests → Python Testing Expert  
- Documentation → Documentation Specialist

### 2. Be Specific
Good prompts get better results:
- ❌ "Fix the bug"
- ✅ "As the CV Pipeline Specialist, fix the gaze detection failing when face landmarks are missing"

### 3. Follow Agent Guidance
Agents know the codebase patterns:
- They enforce temporal smoothing for all metrics
- They ensure normalization by body measurements
- They maintain CSV schema consistency

### 4. Iterate with Agents
Don't hesitate to ask follow-up questions:
```
"That looks good. Now add visualization for the elbow angle in the output video"
```

---

## Agent Capabilities Summary

| Capability | CV Pipeline | Testing | Documentation |
|-----------|------------|---------|---------------|
| Modify pipeline code | ✅ Expert | ⚠️ Basic | ❌ No |
| Add CV models | ✅ Expert | ❌ No | ❌ No |
| Write tests | ⚠️ Basic | ✅ Expert | ❌ No |
| Debug Python | ⚠️ Basic | ✅ Expert | ⚠️ Basic |
| Write docs | ⚠️ Basic | ⚠️ Basic | ✅ Expert |
| Setup help | ⚠️ Basic | ⚠️ Basic | ✅ Expert |
| Performance tuning | ✅ Expert | ✅ Expert | ❌ No |
| Code review | ⚠️ Basic | ✅ Expert | ⚠️ Basic |

---

## Tips for Maximum Effectiveness

### 1. Reference the Agent Explicitly
Start your prompt with the agent identity:
```
"As the Computer Vision Pipeline Specialist, ..."
```

### 2. Provide Context
If working on a specific task:
```
"As the CV Pipeline Specialist, I'm trying to add hand gesture recognition. 
I've already added the model loading code. Now I need to integrate it into 
the frame processing loop with proper temporal smoothing."
```

### 3. Ask for Explanations
Agents can teach you the codebase:
```
"As the CV Pipeline Specialist, explain how the 3D gaze estimation works 
and why we blend head and torso directions"
```

### 4. Request Best Practices
Agents enforce repository conventions:
```
"As the Python Testing Expert, what's the best way to test the temporal 
smoothing function?"
```

---

## Common Scenarios

### Scenario: Adding a New Metric

**Step 1 - Design**
```
As the Computer Vision Pipeline Specialist, I want to add a metric that 
tracks the angle between the firearm barrel and the horizontal plane. 
What keypoints should I use and how should I normalize this?
```

**Step 2 - Implement**
```
As the Computer Vision Pipeline Specialist, implement the firearm angle 
metric in run_pipeline.py following the existing patterns for temporal 
smoothing and CSV export.
```

**Step 3 - Test**
```
As the Python Testing Expert, write unit tests for the firearm angle 
calculation, including edge cases like vertical and horizontal orientations.
```

**Step 4 - Document**
```
As the Documentation Specialist, add documentation for the new firearm 
angle metric in the README and CSV schema documentation.
```

---

### Scenario: Performance Optimization

**Step 1 - Profile**
```
As the Python Testing Expert, profile the pipeline to identify performance 
bottlenecks in frame processing.
```

**Step 2 - Optimize**
```
As the Computer Vision Pipeline Specialist, optimize the identified 
bottlenecks while maintaining detection accuracy and temporal smoothing.
```

**Step 3 - Verify**
```
As the Python Testing Expert, create performance benchmarks to ensure 
the optimization improved speed without degrading quality.
```

---

### Scenario: Environment Setup Issue

**Step 1 - Diagnose**
```
As the Documentation Specialist, I'm getting "ModuleNotFoundError: No 
module named 'mediapipe.tasks'" when running the pipeline. Help me 
diagnose and fix this.
```

**Step 2 - Fix**
```
[Agent provides step-by-step solution]
```

**Step 3 - Document**
```
As the Documentation Specialist, add this MediaPipe import issue to 
the troubleshooting guide so others don't encounter it.
```

---

## Limitations

### What Agents CAN'T Do

- **Run commands**: Agents provide guidance but can't execute commands directly
- **Access external systems**: Agents work within the repository context
- **Make subjective decisions**: Agents follow established patterns but defer to you for design choices

### When to Ask Humans

- Architecture decisions: "Should we refactor the monolithic pipeline into modules?"
- Feature prioritization: "Should we focus on GPU optimization or adding new metrics?"
- Research questions: "What's the best algorithm for firearm orientation detection?"

---

## Getting Help

If you're unsure which agent to use:

1. **Start with any agent** - They can redirect you if needed
2. **Check the agent README** - `.github/agents/README.md` has a decision matrix
3. **Ask for clarification** - Agents can explain their capabilities

---

## Feedback

These agents are designed to evolve with the repository. If you find:
- Missing information that would help agents work better
- Outdated patterns or conventions
- New common issues that should be documented

Please update the agent files in `.github/agents/` or open an issue to discuss improvements.

---

**Remember:** These agents are your specialized teammates with deep knowledge of Smart Coach. Use them to work faster, maintain consistency, and build better code!
