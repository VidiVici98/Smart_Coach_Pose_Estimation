# Detection Pipeline Enhancements

## Overview
This document outlines enhancements made to the main detection pipeline (`scripts/processing/run_pipeline.py`) to improve robustness, performance, and maintainability.

## Implemented Enhancements

### 1. Comprehensive Logging System
**What**: Structured logging with multiple levels (INFO, WARNING, ERROR, DEBUG)
**Why**: Better observability, easier debugging, performance tracking
**Files**:
- Logs written to `data/output/pipeline.log`
- Console output remains for progress tracking
**Usage**:
```bash
python run_pipeline.py --verbose  # Enable debug logging
python run_pipeline.py --quiet    # Only show warnings/errors
```

### 2. Configuration Management
**What**: Centralized configuration with dataclass and command-line arguments
**Why**: No need to edit code to change parameters; supports experimentation
**Key Parameters**:
- `--temp-alpha`: Temporal smoothing (0-1, default 0.6)
- `--conf-thres`: Confidence threshold (0-1, default 0.2)
- `--enable-gpu`: Use GPU if available
- `--maskrcnn-cache`: Cache Mask R-CNN every N frames

**Example**:
```bash
python run_pipeline.py --input my_video.mp4 --temp-alpha 0.7 --enable-gpu
```

### 3. Error Handling & Robustness
**What**: Try-except blocks for model inference, graceful degradation
**Why**: Pipeline continues even if one model fails; better error messages
**Features**:
- Validates config paths at startup
- Handles frame read failures
- Catches model inference errors
- Resource cleanup on exit

### 4. Performance Tracking
**What**: PerformanceTracker class monitors inference times and success rates
**Why**: Identify bottlenecks, optimize slow models
**Metrics Tracked**:
- Average/max inference time per model (pose, face, hands, maskrcnn, facemesh)
- Detection success rates
- Frames with gaze computed
**Usage**:
```bash
python run_pipeline.py --log-performance
```

### 5. GPU Support Detection
**What**: Automatically detect and use GPU if available
**Why**: 5-10x speedup for Mask R-CNN and YOLO models
**Features**:
- Checks `torch.cuda.is_available()`
- Logs device name
- Falls back to CPU if GPU unavailable

### 6. Input Validation
**What**: Validate all config paths and parameters before processing
**Why**: Catch errors early with clear messages
**Validations**:
- Video file exists
- Model files exist
- Parameter ranges (temp_alpha ∈ [0,1], etc.)
- Output directory creation

## Planned Enhancements (Future Work)

### Phase 2: Optimization
- [ ] Mask R-CNN frame caching (compute every N frames, reuse mask)
- [ ] Batch processing for multiple videos
- [ ] Early exit for low-confidence detections
- [ ] Parallel hand detection (left/right processed independently)

### Phase 3: Features
- [ ] Multi-person support with tracking IDs
- [ ] Automatic segment detection (draw, fire, reload)
- [ ] Confidence-based metric quality scoring
- [ ] Export summary statistics (avg confidence, detection rates)

### Phase 4: Code Quality
- [ ] Type hints for all functions
- [ ] Unit tests for metric calculations
- [ ] Refactor into modular classes (PoseDetector, HandDetector, GazeEstimator)
- [ ] Extract to `smart_coach` library

## Performance Benchmarks

### Before Enhancements
- No error handling → crashes on bad frame
- No logging → debugging requires code changes
- Hard-coded config → need to edit code
- No performance visibility

### After Enhancements
- Graceful degradation → continues on errors
- Structured logging → easier debugging
- CLI arguments → flexible configuration
- Performance metrics → identify bottlenecks

## Usage Examples

### Basic Usage (Unchanged)
```bash
python scripts/processing/run_pipeline.py
```

### Advanced Usage (New Features)
```bash
# Process custom video with high confidence threshold
python scripts/processing/run_pipeline.py -i my_training.mp4 --conf-thres 0.4

# Enable GPU and performance logging
python scripts/processing/run_pipeline.py --enable-gpu --log-performance

# Adjust smoothing for faster response
python scripts/processing/run_pipeline.py --temp-alpha 0.8 --verbose

# Use different models
python scripts/processing/run_pipeline.py --pose-model custom/yolov8l-pose.pt
```

## Migration Guide

### For Existing Users
All changes are **backwards compatible**. The script works exactly as before when run without arguments:
```bash
python scripts/processing/run_pipeline.py
```

### For New Features
To leverage new features, add command-line arguments:
```bash
python scripts/processing/run_pipeline.py --help  # See all options
```

### For Developers
Configuration is now centralized in `PipelineConfig` dataclass. To add new parameters:
1. Add field to `PipelineConfig` class
2. Add argument to `parse_arguments()`
3. Update config in `main()` function

## Troubleshooting

### Issue: "Input video not found"
**Solution**: Check video path, use absolute path or ensure working directory is correct

### Issue: "Model not found"
**Solution**: Run model download script or check `data/models/` directory

### Issue: GPU not being used
**Solution**: 
1. Check `torch.cuda.is_available()` returns True
2. Ensure CUDA drivers installed
3. Use `--enable-gpu` flag

### Issue: Pipeline slow
**Solution**:
1. Use `--log-performance` to identify bottleneck
2. Reduce Mask R-CNN frequency with `--maskrcnn-cache 10`
3. Use lighter models (yolov8n instead of yolov8m)

## Technical Details

### Logging Format
```
2026-01-28 01:26:41 - __main__ - INFO - Starting Smart Coach Pose Detection Pipeline
2026-01-28 01:26:42 - __main__ - INFO - ✓ Input video found: data/input/test_video.mp4
2026-01-28 01:26:43 - __main__ - INFO - ✓ GPU available: NVIDIA GeForce RTX 3080
```

### Performance Summary Output
```
============================================================
PERFORMANCE SUMMARY
============================================================
Model Inference Times (avg/max ms):
  pose        :  45.23 / 120.50
  face        :  12.34 /  35.10
  hands       :  18.67 /  50.20
  maskrcnn    : 250.12 / 380.45
  facemesh    :  8.90 /  25.30

Detection Statistics:
  Pose Success Rate: 98.5%
  Face Success Rate: 92.3%
  Hands Detected:    1420 frames
  Gaze Computed:     1380 frames
============================================================
```

## Contributing

To add new enhancements:
1. Document the enhancement in this file
2. Implement with backwards compatibility
3. Add CLI arguments if user-facing
4. Update tests if applicable
5. Add usage examples

## References

- Main pipeline: `scripts/processing/run_pipeline.py`
- Configuration: `PipelineConfig` dataclass
- Logging: Python `logging` module
- CLI: Python `argparse` module
