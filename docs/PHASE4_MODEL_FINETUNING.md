# Phase 4: Firearm Detection Model Fine-Tuning Guide

## Overview

This guide covers fine-tuning YOLOv8 for improved firearm detection accuracy. While the generic YOLOv8 model provides reasonable baseline performance, fine-tuning on firearm-specific data can significantly improve:

- Detection accuracy (especially for handguns, partially occluded firearms)
- Confidence scores (more reliable fusion decisions)
- Muzzle/grip point estimation accuracy
- Performance across lighting conditions and backgrounds

**Note:** This is an optional enhancement. The current hybrid fusion system works well even with moderate detection accuracy.

---

## Prerequisites

### Hardware Requirements

**Minimum (Training Possible):**
- GPU: NVIDIA GPU with 6GB+ VRAM (GTX 1060 or better)
- RAM: 16GB system RAM
- Storage: 50GB free space (dataset + model checkpoints)

**Recommended (Efficient Training):**
- GPU: NVIDIA RTX 3070 or better (8GB+ VRAM)
- RAM: 32GB system RAM
- Storage: 100GB free space

**CPU-Only:** Not recommended (training would take days/weeks)

### Software Requirements

```bash
# Already in requirements.txt
ultralytics>=8.0.0
torch>=2.0.0
torchvision>=0.15.0
opencv-python>=4.7.0
```

**Additional for training:**
```bash
pip install tensorboard albumentations
```

---

## Step 1: Dataset Preparation

### Option A: Use Existing Firearm Datasets

**Roboflow Universe:**
- Search "firearm detection" or "gun detection"
- Export in YOLOv8 format
- Typical datasets: 1000-10000 images

**Example datasets:**
- [Firearm Detection](https://universe.roboflow.com/) - Various public datasets
- Look for datasets with:
  - Multiple firearm types (handgun, rifle, shotgun)
  - Various lighting conditions
  - Diverse backgrounds
  - Partial occlusion examples

### Option B: Create Custom Dataset

**1. Collect Training Videos:**
```bash
# Record training sessions
- Multiple shooters
- Different firearms
- Various ranges/backgrounds
- Different lighting (indoor/outdoor)
- Multiple angles
```

**2. Extract Frames:**
```bash
python scripts/tools/extract_frames.py \
  --video data/training_videos/*.mp4 \
  --output data/dataset/images \
  --fps 2  # Extract 2 frames per second
```

**3. Annotate Images:**

Use annotation tools:
- **CVAT** (Computer Vision Annotation Tool) - Recommended
- **LabelImg** - Simple, desktop-based
- **Roboflow** - Cloud-based with auto-labeling

**Annotation format (YOLOv8):**
```
# data/dataset/labels/image001.txt
# Format: class_id center_x center_y width height (normalized 0-1)
0 0.5 0.4 0.3 0.2
```

**Classes:**
```yaml
# data/dataset/data.yaml
names:
  0: handgun
  1: rifle
  2: shotgun
  # Or simplified:
  0: firearm
```

### Dataset Structure

```
data/
  dataset/
    train/
      images/
        img001.jpg
        img002.jpg
        ...
      labels/
        img001.txt
        img002.txt
        ...
    val/
      images/
      labels/
    test/
      images/
      labels/
    data.yaml
```

### Dataset Requirements

**Minimum viable dataset:**
- Training: 500+ images
- Validation: 100+ images
- Test: 100+ images

**Good dataset:**
- Training: 2000+ images
- Validation: 400+ images
- Test: 400+ images

**Excellent dataset:**
- Training: 5000+ images
- Validation: 1000+ images
- Test: 1000+ images

**Distribution guidelines:**
- 70% train, 15% validation, 15% test
- Balanced across firearm types
- Balanced across lighting conditions
- Include challenging examples (occlusion, motion blur)

---

## Step 2: Configuration

### Create Training Configuration

**File:** `data/dataset/data.yaml`

```yaml
# Dataset paths
path: /absolute/path/to/data/dataset
train: train/images
val: val/images
test: test/images

# Classes
nc: 1  # number of classes (simplified: just "firearm")
names:
  0: firearm

# Or multiple classes
nc: 3
names:
  0: handgun
  1: rifle
  2: shotgun
```

### Training Configuration

**File:** `scripts/training/train_firearm_detector.py`

```python
from ultralytics import YOLO

# Configuration
DATA_YAML = "data/dataset/data.yaml"
MODEL_SIZE = "yolov8n"  # n, s, m, l, x (nano to extra-large)
EPOCHS = 100
BATCH_SIZE = 16  # Adjust based on GPU memory
IMG_SIZE = 640
PATIENCE = 20  # Early stopping

# Initialize model
model = YOLO(f"{MODEL_SIZE}.pt")  # Start from COCO pretrained weights

# Train
results = model.train(
    data=DATA_YAML,
    epochs=EPOCHS,
    batch=BATCH_SIZE,
    imgsz=IMG_SIZE,
    patience=PATIENCE,
    device=0,  # GPU 0, use 'cpu' for CPU training
    
    # Augmentation (already optimized in YOLOv8)
    hsv_h=0.015,      # Hue augmentation
    hsv_s=0.7,        # Saturation augmentation
    hsv_v=0.4,        # Value augmentation
    degrees=10.0,     # Rotation
    translate=0.1,    # Translation
    scale=0.5,        # Scaling
    shear=0.0,        # Shear
    perspective=0.0,  # Perspective
    flipud=0.0,       # Flip up-down
    fliplr=0.5,       # Flip left-right
    mosaic=1.0,       # Mosaic augmentation
    mixup=0.1,        # Mixup augmentation
    
    # Optimization
    optimizer='AdamW',
    lr0=0.01,         # Initial learning rate
    lrf=0.01,         # Final learning rate (lr0 * lrf)
    momentum=0.937,
    weight_decay=0.0005,
    
    # Training settings
    warmup_epochs=3,
    warmup_momentum=0.8,
    warmup_bias_lr=0.1,
    box=7.5,          # Box loss gain
    cls=0.5,          # Class loss gain
    dfl=1.5,          # DFL loss gain
    
    # Logging
    project='runs/firearm_detection',
    name='exp',
    exist_ok=False,
    verbose=True,
    save=True,
    save_period=10,   # Save checkpoint every N epochs
)

print(f"\nTraining complete!")
print(f"Best model saved to: {results.save_dir}/weights/best.pt")
```

---

## Step 3: Training

### Start Training

```bash
cd /path/to/Smart_Coach_Pose_Estimation

# Create training script if not exists
python scripts/training/train_firearm_detector.py

# Monitor with TensorBoard (optional)
tensorboard --logdir runs/firearm_detection
```

### Expected Training Time

**YOLOv8n (nano) on RTX 3070:**
- 100 epochs: ~2-4 hours (2000 images)
- 100 epochs: ~6-10 hours (5000 images)

**YOLOv8m (medium) on RTX 3070:**
- 100 epochs: ~6-12 hours (2000 images)
- 100 epochs: ~15-25 hours (5000 images)

### Monitor Training

**Console Output:**
```
Epoch   GPU_mem   box_loss   cls_loss   dfl_loss   Instances   Size
  1/100     1.2G      1.234      0.567      1.234        156    640
  2/100     1.2G      1.123      0.498      1.187        142    640
  ...
 100/100    1.2G      0.345      0.123      0.456        138    640

Training complete! Best mAP@0.5: 0.892
```

**TensorBoard Metrics:**
- Loss curves (box, class, DFL)
- mAP@0.5, mAP@0.5:0.95
- Precision, Recall
- Learning rate schedule

### Training Tips

**If loss not decreasing:**
- Lower learning rate (lr0=0.005)
- Increase warmup epochs (warmup_epochs=5)
- Check dataset quality (labels correct?)

**If overfitting:**
- Increase augmentation
- Add more training data
- Use dropout (if available)
- Reduce model size

**If underfitting:**
- Increase model size (n→s→m)
- Train longer (more epochs)
- Check dataset difficulty

**GPU Out of Memory:**
- Reduce batch size (batch=8 or batch=4)
- Reduce image size (imgsz=416)
- Use smaller model (yolov8n)

---

## Step 4: Evaluation

### Evaluate on Test Set

```python
from ultralytics import YOLO

# Load best model
model = YOLO('runs/firearm_detection/exp/weights/best.pt')

# Evaluate
metrics = model.val(data='data/dataset/data.yaml', split='test')

print(f"mAP@0.5: {metrics.box.map50:.3f}")
print(f"mAP@0.5:0.95: {metrics.box.map:.3f}")
print(f"Precision: {metrics.box.mp:.3f}")
print(f"Recall: {metrics.box.mr:.3f}")
```

### Performance Targets

**Minimum acceptable:**
- mAP@0.5: > 0.70
- Precision: > 0.75
- Recall: > 0.60

**Good performance:**
- mAP@0.5: > 0.85
- Precision: > 0.85
- Recall: > 0.75

**Excellent performance:**
- mAP@0.5: > 0.92
- Precision: > 0.90
- Recall: > 0.85

### Visual Inspection

```python
# Test on sample images
results = model.predict(
    source='data/dataset/test/images',
    save=True,
    conf=0.3,
    project='runs/firearm_detection',
    name='test_predictions'
)
```

**Check for:**
- ✓ Correct detections on clear examples
- ✓ Robust to partial occlusion
- ✓ Works across lighting conditions
- ✓ Minimal false positives
- ✓ Consistent across firearm types

---

## Step 5: Integration

### Deploy Fine-Tuned Model

```bash
# Copy best model to models directory
cp runs/firearm_detection/exp/weights/best.pt data/models/yolov8_firearm_finetuned.pt
```

### Update Pipeline Configuration

**In `scripts/processing/run_pipeline_enhanced.py`:**

```python
# Change line ~58
FIREARM_MODEL_PATH = "data/models/yolov8_firearm_finetuned.pt"  # Use fine-tuned model
```

### Test Integration

```bash
# Run pipeline with fine-tuned model
python scripts/processing/run_pipeline_enhanced.py

# Generate coaching report
python scripts/tools/generate_coaching_report.py data/output/analytics.csv

# Check metrics
# Should see:
# - Higher firearm_confidence values
# - More consistent firearm_detected flags
# - More accurate muzzle_point estimates
```

### Performance Comparison

**Before (generic YOLOv8n):**
- Detection rate: 20-60%
- Average confidence: 0.4-0.6
- False positives: Occasional
- Muzzle fusion: 50% firearm, 50% arms

**After (fine-tuned):**
- Detection rate: 60-90%
- Average confidence: 0.7-0.9
- False positives: Rare
- Muzzle fusion: 80% firearm, 20% arms

---

## Step 6: Advanced Improvements

### Firearm Type Classification

Instead of single class "firearm", train with multiple classes:

```yaml
# data/dataset/data.yaml
nc: 3
names:
  0: handgun
  1: rifle
  2: shotgun
```

**Benefits:**
- Type-specific coaching (different recoil patterns)
- Different safety rules per type
- Better analytics segmentation

### Keypoint Detection

For even better muzzle/grip estimation, use YOLOv8-pose:

```python
from ultralytics import YOLO

# Train with keypoints
model = YOLO('yolov8n-pose.pt')

# Define keypoints: [muzzle, grip, trigger, sight_front, sight_rear]
# Requires keypoint annotations in dataset
```

**Annotation format with keypoints:**
```
# label.txt
# class cx cy w h kp1_x kp1_y kp1_v kp2_x kp2_y kp2_v ...
0 0.5 0.4 0.3 0.2 0.6 0.35 2 0.4 0.45 2 ...
# kp_v: 0=not labeled, 1=labeled but occluded, 2=labeled and visible
```

### Export Optimized Model

**For deployment:**

```python
# Export to ONNX (faster inference)
model.export(format='onnx', dynamic=True, simplify=True)

# Export to TensorRT (GPU optimization)
model.export(format='engine', device=0)

# Export to CoreML (Apple devices)
model.export(format='coreml')
```

---

## Troubleshooting

### Problem: Low mAP after training

**Solutions:**
1. Check dataset quality (correct labels?)
2. Increase training data (need more examples)
3. Train longer (more epochs)
4. Adjust augmentation parameters
5. Try larger model (yolov8s or yolov8m)

### Problem: High training loss, low validation loss

**Diagnosis:** Overfitting

**Solutions:**
1. Add more training data
2. Increase augmentation
3. Reduce model complexity
4. Add regularization

### Problem: High validation loss

**Diagnosis:** Underfitting or poor data

**Solutions:**
1. Increase model capacity
2. Train longer
3. Reduce augmentation
4. Check data quality

### Problem: Slow inference

**Solutions:**
1. Use smaller model (yolov8n)
2. Export to ONNX or TensorRT
3. Reduce input size (imgsz=416)
4. Batch processing

---

## Best Practices

### Data Collection

1. **Diverse conditions:** Indoor, outdoor, day, night
2. **Multiple firearms:** Different makes, models, colors
3. **Various shooters:** Different body types, stances
4. **Camera angles:** Front, side, 3/4 view
5. **Motion:** Static and dynamic (drawing, presenting)

### Annotation Quality

1. **Tight bounding boxes:** Just around firearm
2. **Consistent labeling:** Same criteria across images
3. **Include difficult cases:** Occlusion, blur, small objects
4. **Multiple annotators:** Consensus labeling for quality

### Training Strategy

1. **Start small:** Test with subset (500 images)
2. **Iterate quickly:** Quick experiments to find best config
3. **Monitor metrics:** Track mAP, loss curves
4. **Save checkpoints:** Resume training if needed
5. **Evaluate regularly:** Test on validation set

### Deployment

1. **A/B test:** Compare generic vs fine-tuned
2. **Monitor confidence:** Track average confidence scores
3. **User feedback:** Are detections accurate?
4. **Update regularly:** Retrain with new data

---

## Cost Estimate

### Cloud GPU Training (if no local GPU)

**Google Colab Pro:**
- $10/month
- Includes P100/V100 GPU
- Sufficient for fine-tuning

**AWS EC2 (g4dn.xlarge):**
- ~$0.50/hour
- Training time: 2-10 hours
- Total: $1-5 per training run

**Paperspace Gradient:**
- $0.45/hour (P4000)
- Training time: 2-10 hours
- Total: $1-5 per training run

### Dataset Annotation

**DIY:**
- Time: 1-2 hours per 100 images
- Cost: Free (your time)

**Annotation Service:**
- Cost: $0.10-1.00 per image
- 1000 images: $100-1000

---

## Summary

**Phase 4 is optional** but provides significant benefits:

**Before fine-tuning:**
- ✓ Working system with hybrid fusion
- ✓ Graceful fallback to arm kinematics
- ~ Detection: 20-60% depending on conditions

**After fine-tuning:**
- ✓ Higher detection accuracy (60-90%)
- ✓ More confident predictions
- ✓ Better muzzle point estimation
- ✓ Firearm type classification (optional)
- ✓ Reduced reliance on fallback

**Recommendation:** 
Start with the current system. If firearm detection is consistently low (<30%) in your specific use case, consider fine-tuning.

**Next Steps:**
1. Collect or source firearm dataset
2. Annotate 500-1000 images
3. Run training script
4. Evaluate on test set
5. Deploy if mAP > 0.70
6. Monitor performance in production

---

## Resources

**YOLOv8 Documentation:**
- https://docs.ultralytics.com/

**Dataset Sources:**
- Roboflow Universe: https://universe.roboflow.com/
- Open Images: https://storage.googleapis.com/openimages/web/index.html

**Annotation Tools:**
- CVAT: https://www.cvat.ai/
- LabelImg: https://github.com/heartexlabs/labelImg
- Roboflow: https://roboflow.com/

**Training Platforms:**
- Google Colab: https://colab.research.google.com/
- Paperspace: https://www.paperspace.com/
- AWS SageMaker: https://aws.amazon.com/sagemaker/

---

**Status:** Documentation complete for optional Phase 4
