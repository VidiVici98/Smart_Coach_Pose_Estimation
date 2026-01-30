"""
YOLOv8 Firearm Detection Training Script

This script fine-tunes YOLOv8 for improved firearm detection accuracy.
Requires a properly formatted dataset (see docs/PHASE4_MODEL_FINETUNING.md)

Usage:
    python scripts/training/train_firearm_detector.py --data data/dataset/data.yaml --epochs 100
"""

import argparse
import os
from pathlib import Path
from ultralytics import YOLO


def train_firearm_detector(
    data_yaml: str,
    model_size: str = "yolov8n",
    epochs: int = 100,
    batch_size: int = 16,
    img_size: int = 640,
    device: str = "0",
    project: str = "runs/firearm_detection",
    name: str = "exp",
):
    """
    Train YOLOv8 model for firearm detection.
    
    Args:
        data_yaml: Path to dataset YAML configuration
        model_size: Model size (n, s, m, l, x)
        epochs: Number of training epochs
        batch_size: Batch size (adjust based on GPU memory)
        img_size: Input image size
        device: Device to use (0=GPU 0, cpu=CPU)
        project: Project directory for results
        name: Experiment name
    """
    print("=" * 80)
    print("YOLOv8 Firearm Detection Training")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Dataset: {data_yaml}")
    print(f"  Model: {model_size}")
    print(f"  Epochs: {epochs}")
    print(f"  Batch size: {batch_size}")
    print(f"  Image size: {img_size}")
    print(f"  Device: {device}")
    print(f"  Output: {project}/{name}")
    print()
    
    # Verify dataset exists
    if not os.path.exists(data_yaml):
        raise FileNotFoundError(f"Dataset YAML not found: {data_yaml}")
    
    # Initialize model from COCO pretrained weights
    model_path = f"{model_size}.pt"
    print(f"Loading pretrained model: {model_path}")
    model = YOLO(model_path)
    
    print(f"\nStarting training...")
    print("-" * 80)
    
    # Train
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        patience=20,  # Early stopping patience
        device=device,
        
        # Data augmentation (YOLOv8 defaults are good)
        hsv_h=0.015,      # Hue augmentation
        hsv_s=0.7,        # Saturation augmentation
        hsv_v=0.4,        # Value augmentation
        degrees=10.0,     # Image rotation (+/- deg)
        translate=0.1,    # Image translation (+/- fraction)
        scale=0.5,        # Image scale (+/- gain)
        shear=0.0,        # Image shear (+/- deg)
        perspective=0.0,  # Image perspective (+/- fraction)
        flipud=0.0,       # Vertical flip (probability)
        fliplr=0.5,       # Horizontal flip (probability)
        mosaic=1.0,       # Mosaic augmentation (probability)
        mixup=0.1,        # Mixup augmentation (probability)
        copy_paste=0.0,   # Copy-paste augmentation (probability)
        
        # Optimizer settings
        optimizer='AdamW',
        lr0=0.01,         # Initial learning rate
        lrf=0.01,         # Final learning rate (lr0 * lrf)
        momentum=0.937,   # SGD momentum/Adam beta1
        weight_decay=0.0005,  # Optimizer weight decay
        
        # Training settings
        warmup_epochs=3.0,    # Warmup epochs
        warmup_momentum=0.8,  # Warmup initial momentum
        warmup_bias_lr=0.1,   # Warmup initial bias lr
        box=7.5,              # Box loss gain
        cls=0.5,              # Class loss gain
        dfl=1.5,              # DFL loss gain
        
        # Validation
        val=True,
        
        # Logging and saving
        project=project,
        name=name,
        exist_ok=False,
        pretrained=True,
        verbose=True,
        seed=0,
        deterministic=True,
        single_cls=False,
        rect=False,
        cos_lr=False,
        close_mosaic=10,  # Disable mosaic last N epochs
        resume=False,
        amp=True,  # Automatic Mixed Precision
        fraction=1.0,  # Dataset fraction to train on
        profile=False,
        freeze=None,
        save=True,
        save_period=10,  # Save checkpoint every N epochs
        cache=False,
        workers=8,
        plots=True,
    )
    
    print("\n" + "=" * 80)
    print("Training Complete!")
    print("=" * 80)
    
    # Print results
    best_model = Path(project) / name / "weights" / "best.pt"
    last_model = Path(project) / name / "weights" / "last.pt"
    
    print(f"\nModel saved to:")
    print(f"  Best: {best_model}")
    print(f"  Last: {last_model}")
    
    print(f"\nTraining metrics:")
    print(f"  mAP@0.5: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
    print(f"  mAP@0.5:0.95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
    
    print(f"\nTo use this model in the pipeline:")
    print(f"  1. Copy to models directory:")
    print(f"     cp {best_model} data/models/yolov8_firearm_finetuned.pt")
    print(f"  2. Update run_pipeline_enhanced.py:")
    print(f"     FIREARM_MODEL_PATH = 'data/models/yolov8_firearm_finetuned.pt'")
    
    return results


def evaluate_model(model_path: str, data_yaml: str):
    """
    Evaluate trained model on test set.
    
    Args:
        model_path: Path to trained model weights
        data_yaml: Path to dataset YAML configuration
    """
    print("=" * 80)
    print("Model Evaluation")
    print("=" * 80)
    
    model = YOLO(model_path)
    
    # Run validation on test split
    metrics = model.val(data=data_yaml, split='test')
    
    print(f"\nTest Set Results:")
    print(f"  mAP@0.5: {metrics.box.map50:.3f}")
    print(f"  mAP@0.5:0.95: {metrics.box.map:.3f}")
    print(f"  Precision: {metrics.box.mp:.3f}")
    print(f"  Recall: {metrics.box.mr:.3f}")
    
    # Performance assessment
    if metrics.box.map50 >= 0.92:
        print(f"\n✓ Excellent performance! (mAP@0.5 >= 0.92)")
    elif metrics.box.map50 >= 0.85:
        print(f"\n✓ Good performance (mAP@0.5 >= 0.85)")
    elif metrics.box.map50 >= 0.70:
        print(f"\n~ Acceptable performance (mAP@0.5 >= 0.70)")
    else:
        print(f"\n✗ Below target (mAP@0.5 < 0.70) - consider retraining")
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Train YOLOv8 firearm detector")
    
    # Required arguments
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to dataset YAML file"
    )
    
    # Optional arguments
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n",
        choices=["yolov8n", "yolov8s", "yolov8m", "yolov8l", "yolov8x"],
        help="Model size (default: yolov8n)"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs (default: 100)"
    )
    
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Batch size (default: 16, adjust based on GPU memory)"
    )
    
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Input image size (default: 640)"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        default="0",
        help="Device to use: 0 for GPU 0, cpu for CPU (default: 0)"
    )
    
    parser.add_argument(
        "--project",
        type=str,
        default="runs/firearm_detection",
        help="Project directory for results (default: runs/firearm_detection)"
    )
    
    parser.add_argument(
        "--name",
        type=str,
        default="exp",
        help="Experiment name (default: exp)"
    )
    
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Evaluate model after training"
    )
    
    args = parser.parse_args()
    
    # Train model
    results = train_firearm_detector(
        data_yaml=args.data,
        model_size=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.imgsz,
        device=args.device,
        project=args.project,
        name=args.name,
    )
    
    # Evaluate if requested
    if args.eval:
        best_model = Path(args.project) / args.name / "weights" / "best.pt"
        evaluate_model(str(best_model), args.data)


if __name__ == "__main__":
    main()
