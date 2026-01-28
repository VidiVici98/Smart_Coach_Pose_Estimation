# Model Files

This directory contains the pre-trained model weights required by the Smart Coach pipeline.

## Required Models

The pipeline needs three model files:

1. **yolov8m-pose.pt** (~52 MB)
   - YOLOv8 medium pose detection model
   - Detects 17 body keypoints (nose, eyes, shoulders, elbows, wrists, hips, knees, ankles)

2. **yolov8n-face.pt** (~6 MB)
   - YOLOv8 nano face detection model
   - Used for head pose estimation and gaze tracking

3. **hand_landmarker.task** (~27 MB)
   - MediaPipe Hand Landmarker model
   - Detects 21 hand landmarks per hand (wrist, fingers, joints)

## Automatic Download (Recommended)

The easiest way to get all models:

```bash
# Make sure you're in the repo root
cd /path/to/Smart_Coach_Pose_Estimation

# Activate virtual environment
source mediapipe_env/bin/activate

# Run download script
python scripts/tools/download_models.py
```

This will automatically download and place all models in the correct location.

## Manual Download

If the automatic download doesn't work, you can download manually:

### 1. YOLOv8 Pose Model

**Using Python:**
```bash
source mediapipe_env/bin/activate
python -c "from ultralytics import YOLO; model = YOLO('yolov8m-pose.pt')"
cp ~/.cache/ultralytics/yolov8m-pose.pt data/models/
```

**Or using wget:**
```bash
cd data/models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m-pose.pt
```

### 2. YOLOv8 Face Model

**Using Python:**
```bash
source mediapipe_env/bin/activate
python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt')"
cp ~/.cache/ultralytics/yolov8n.pt data/models/yolov8n-face.pt
```

**Note:** Standard YOLOv8 doesn't include a specific face model. The pipeline uses a general object detection model. For better face detection, you may need to train or find a custom face-specific YOLOv8 model.

### 3. MediaPipe Hand Landmarker

```bash
cd data/models
wget https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

## Verify Models

After downloading, verify all models are present:

```bash
python scripts/tools/verify_setup.py
```

Expected output:
```
Checking model files...
  ✓ yolov8m-pose.pt (52.0 MB) - YOLOv8 Pose Model
  ✓ yolov8n-face.pt (6.2 MB) - YOLOv8 Face Model
  ✓ hand_landmarker.task (26.8 MB) - MediaPipe Hand Landmarker
```

## Alternative Models

### Lighter Models (for faster processing)

If you have limited compute resources:
- Replace `yolov8m-pose.pt` with `yolov8n-pose.pt` (~6 MB, faster but less accurate)
- Update `POSE_MODEL_PATH` in `scripts/processing/run_pipeline.py`

### Heavier Models (for better accuracy)

For better detection quality:
- Replace `yolov8m-pose.pt` with `yolov8l-pose.pt` or `yolov8x-pose.pt`
- Requires more GPU memory and processing time

## Troubleshooting

### "Model file not found" error

Check that files exist:
```bash
ls -lh data/models/
```

Should show:
```
yolov8m-pose.pt
yolov8n-face.pt
hand_landmarker.task
```

### Download fails

1. Check internet connection
2. Try manual download with `wget` or `curl`
3. Download on another device and transfer files

### Wrong file size

If file sizes are very small (< 1 MB), the download likely failed:
```bash
# Remove and re-download
rm data/models/[filename]
python scripts/tools/download_models.py
```

## Model Sources

- **YOLOv8 Models**: [Ultralytics](https://github.com/ultralytics/ultralytics)
- **MediaPipe Models**: [Google MediaPipe](https://developers.google.com/mediapipe)

## License

Models have their own licenses:
- YOLOv8: AGPL-3.0 (or commercial license from Ultralytics)
- MediaPipe: Apache 2.0

See respective project pages for details.

## Custom Models

You can use your own custom-trained models by:
1. Placing them in this directory
2. Updating the model paths in `scripts/processing/run_pipeline.py`:
   ```python
   POSE_MODEL_PATH = "data/models/your_custom_pose.pt"
   FACE_MODEL_PATH = "data/models/your_custom_face.pt"
   HAND_MODEL_PATH = "data/models/your_custom_hand.task"
   ```

For training custom models, see the Ultralytics and MediaPipe documentation.
