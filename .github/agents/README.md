# Custom Agents for Smart Coach

This directory contains custom agent configurations designed specifically for the Smart Coach Pose Estimation project. These agents are specialized AI assistants with deep knowledge of the codebase and development practices.

## Available Agents

### 1. Computer Vision Pipeline Specialist (`cv_pipeline_specialist.md`)

**Expertise:**
- Multi-model computer vision integration (YOLOv8, MediaPipe, Mask R-CNN)
- Video processing and frame-by-frame analytics
- Pose estimation and biomechanical tracking
- Temporal smoothing and noise reduction
- Model optimization and performance tuning

**Use this agent for:**
- Modifying the main pipeline (`scripts/processing/run_pipeline.py`)
- Adding new pose/hand/face detection features
- Implementing new metrics or calculations
- Optimizing frame processing performance
- Fixing detection or tracking issues
- Integrating new computer vision models

**Example tasks:**
- "Add a new metric to track wrist rotation"
- "Improve temporal smoothing for hand landmarks"
- "Integrate YOLOv8n-pose model as an alternative"
- "Fix gaze detection when face is partially occluded"

---

### 2. Python Testing & Code Quality Expert (`python_testing_expert.md`)

**Expertise:**
- Writing comprehensive unit and integration tests
- Python debugging and optimization
- CI/CD pipeline setup
- Code quality and maintainability
- Dependency management

**Use this agent for:**
- Writing tests for new features
- Debugging Python import or runtime errors
- Setting up pytest, coverage, and linting
- Optimizing Python code performance
- Managing requirements.txt and virtual environments
- Fixing CI/CD issues

**Example tasks:**
- "Write tests for the new shoulder angle metric"
- "Fix the failing test in test_maskrcnn_cache.py"
- "Set up GitHub Actions for automated testing"
- "Profile the pipeline and identify performance bottlenecks"

---

### 3. Documentation & Setup Specialist (`documentation_specialist.md`)

**Expertise:**
- Technical writing and documentation
- Setup guides and troubleshooting
- Onboarding new contributors
- Environment configuration
- Creating examples and tutorials

**Use this agent for:**
- Writing or updating documentation
- Creating setup guides for different platforms
- Troubleshooting installation issues
- Writing tutorials or examples
- Improving README clarity
- Documenting new features

**Example tasks:**
- "Create a tutorial for adding custom metrics"
- "Update the README with the new firearm detection feature"
- "Write a troubleshooting guide for MediaPipe errors"
- "Create a contributor onboarding guide"

---

## How to Use Custom Agents

### With GitHub Copilot Chat

When working with GitHub Copilot, you can reference these agents in your prompts:

```
As the Computer Vision Pipeline Specialist, help me add elbow angle tracking to the pipeline.
```

```
As the Python Testing Expert, write comprehensive tests for the new gaze detection feature.
```

```
As the Documentation Specialist, create a setup guide for Windows users.
```

### Benefits of Custom Agents

1. **Deep Context**: Each agent has comprehensive knowledge of the codebase, conventions, and best practices
2. **Specialized Skills**: Agents are experts in their domain (CV, testing, or docs)
3. **Consistency**: Ensures code follows established patterns and principles
4. **Efficiency**: Faster, more accurate assistance for domain-specific tasks

### Choosing the Right Agent

| Task Type | Recommended Agent |
|-----------|------------------|
| Modify pipeline logic | CV Pipeline Specialist |
| Add new detection models | CV Pipeline Specialist |
| Write or fix tests | Python Testing Expert |
| Debug Python errors | Python Testing Expert |
| Write documentation | Documentation Specialist |
| Setup troubleshooting | Documentation Specialist |
| Performance optimization | CV Pipeline or Python Expert |
| New metric calculations | CV Pipeline Specialist |

---

## Agent Development Guidelines

Each agent follows these principles:

### 1. Minimal Changes
Agents make surgical, focused modifications rather than large rewrites.

### 2. Testing First
Changes are validated with appropriate tests before finalization.

### 3. Documentation
Code changes are accompanied by clear comments and documentation updates.

### 4. Preserve Patterns
Agents maintain existing code patterns and conventions:
- Temporal smoothing for all detections
- Normalization by body measurements
- Graceful degradation on failures
- CSV schema consistency

### 5. Domain Expertise
Each agent leverages deep knowledge of their specialty:
- CV Pipeline: Knows pose estimation, temporal filtering, multi-model fusion
- Testing: Knows pytest patterns, mocking, performance benchmarks
- Documentation: Knows technical writing, markdown, setup workflows

---

## Maintaining Custom Agents

### When to Update Agents

Update agent configurations when:
- Major architectural changes occur
- New patterns or conventions are established
- Dependencies are upgraded significantly
- Common issues or solutions are discovered

### How to Update Agents

1. Edit the relevant `.md` file in this directory
2. Update the context, examples, or guidelines
3. Test the agent with representative tasks
4. Document the changes in this README

### Agent Configuration Format

Each agent file includes:
- **Agent Identity**: Role and expertise areas
- **Repository Context**: Project overview and architecture
- **Critical Patterns**: Must-follow conventions
- **Known Issues**: Common problems and solutions
- **Development Workflow**: How to work effectively
- **Success Criteria**: What defines successful work

---

## Feedback and Improvements

If you discover:
- Missing information that would help agents work better
- Outdated patterns or conventions
- New common issues that should be documented
- Better ways to structure agent knowledge

Please update the relevant agent file or create an issue to discuss improvements.

---

## Agent Responsibilities Summary

### Computer Vision Pipeline Specialist
✅ Pipeline modifications and feature additions  
✅ Model integration and optimization  
✅ Metric calculations and spatial reasoning  
❌ Testing infrastructure  
❌ Documentation writing  

### Python Testing & Code Quality Expert
✅ Test writing and debugging  
✅ CI/CD setup and maintenance  
✅ Performance profiling and optimization  
❌ Computer vision algorithms  
❌ Documentation writing  

### Documentation & Setup Specialist
✅ Writing guides and tutorials  
✅ Setup troubleshooting  
✅ Onboarding materials  
❌ Pipeline implementation  
❌ Test infrastructure  

---

## Related Resources

- **Main Documentation**: `/README.md`
- **Copilot Instructions**: `/.github/copilot-instructions.md`
- **Contributing Guide**: `/CONTRIBUTING.md`
- **Setup Guide**: `/docs/guides/SETUP.md`

---

Last Updated: 2026-01-29
