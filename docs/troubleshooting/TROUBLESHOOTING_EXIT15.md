# Troubleshooting Exit Code -15

Exit code -15 (SIGTERM) typically indicates the process was terminated by a signal. This usually happens due to:

## Common Causes

### 1. Segmentation Fault
- **Symptom**: Process crashes immediately or during MediaPipe initialization
- **Test**: Run `python3 test_mediapipe_init.py` to isolate the issue
- **Fix**: MediaPipe FaceMesh has been configured with minimal settings to prevent crashes

### 2. Out of Memory
- **Symptom**: Process crashes during video processing
- **Check**: Run `free -h` to see available memory
- **Fix**: Process smaller videos or reduce model batch sizes

### 3. Library Incompatibility
- **Symptom**: Crashes on import or initialization
- **Check**: Verify MediaPipe and OpenCV versions are compatible
- **Fix**: Reinstall packages: `pip install --force-reinstall mediapipe opencv-python`

## Diagnostic Steps

### Step 1: Test MediaPipe Initialization
```bash
python3 test_mediapipe_init.py
```
If this fails, MediaPipe FaceMesh has a compatibility issue.

### Step 2: Run Pipeline with Diagnostics
```bash
python3 run_pipeline_safe.py
```
This will show exactly where the pipeline fails.

### Step 3: Check System Resources
```bash
free -h          # Check available memory
df -h            # Check disk space
ulimit -a        # Check process limits
```

## Current Configuration

The pipeline has been configured with:
- **MediaPipe FaceMesh**: Minimal configuration (`refine_landmarks=False`)
- **Error Handling**: All face processing wrapped in try-except
- **Graceful Degradation**: Pipeline continues even if gaze visualization fails
- **Debug Output**: Progress messages throughout initialization

## Fallback Mode

If MediaPipe FaceMesh cannot be initialized, the pipeline will:
1. Print a warning message
2. Disable gaze cone visualization
3. Continue processing all other metrics (pose, hands, body mask)

You will still get:
- ✓ Full-body skeleton tracking
- ✓ Hand landmark detection
- ✓ Body mask segmentation
- ✓ All joint angles and metrics
- ✗ Gaze cone visualization (disabled)
- ✗ Head pose 3D estimation (disabled)

## If Issue Persists

Run with verbose output to see exact failure point:
```bash
python3 scripts/processing/run_pipeline.py 2>&1 | tee pipeline_output.log
```

Check the log for:
- Last successful operation before crash
- Any segmentation fault messages
- Memory errors

## Quick Fixes

### Try 1: Disable Refinement (Already Done)
FaceMesh refinement has been disabled to reduce memory usage.

### Try 2: Static Mode
Edit line 276 in `run_pipeline.py`:
```python
static_image_mode=True,  # Change from False to True
```

### Try 3: Disable Face Mesh Entirely
Edit line 275 in `run_pipeline.py`:
```python
mp_face = None  # Skip initialization, comment out the try block
```

This will disable gaze visualization but allow the rest of the pipeline to work.
