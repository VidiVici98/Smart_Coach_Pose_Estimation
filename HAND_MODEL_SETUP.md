# Setup Instructions for Hand Detection Model

## Missing Model: hand_landmarker.task

The pipeline requires the MediaPipe Hand Landmarker model for hand tracking. Due to network restrictions (Google CDN blocked), this model could not be downloaded automatically.

### Manual Installation Required

**File:** `hand_landmarker.task`  
**Location:** `data/models/hand_landmarker.task`  
**Size:** ~3.6 MB (float16 version) or ~26 MB (full precision)

### Download Instructions

Download the model from MediaPipe:
```bash
cd data/models
wget https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

Or download from alternative sources if the above URL is blocked.

### Verification

After adding the model file, verify it's in place:
```bash
ls -lh data/models/hand_landmarker.task
```

Expected output:
```
-rw-r--r-- 1 user user 3.6M ... hand_landmarker.task
```

### Running the Pipeline

Once the hand model is added, all detection features will be enabled:
- ✅ Pose Detection (17 keypoints)
- ✅ Hand Detection (21 points per hand) - **requires hand_landmarker.task**
- ✅ Body Segmentation (Mask R-CNN)
- ✅ Face Detection & Gaze Tracking

Run the pipeline:
```bash
source mediapipe_env/bin/activate
python scripts/processing/run_pipeline.py
```

## Current Status

The pipeline currently runs with these features enabled:
- ✅ Pose Detection
- ⚠️  Hand Detection - **DISABLED** (model not available)
- ✅ Body Segmentation
- ✅ Face Detection & Gaze Tracking

Once you add `hand_landmarker.task`, hand detection will be automatically enabled.
