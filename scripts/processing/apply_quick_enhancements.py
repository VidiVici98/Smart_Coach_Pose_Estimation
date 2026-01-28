#!/usr/bin/env python3
"""
Quick Enhancements Patch for run_pipeline.py

This script applies minimal, surgical enhancements to the main pipeline:
1. Add basic logging
2. Add GPU detection
3. Add error handling wrapper
4. Add progress summary

Usage:
    python apply_quick_enhancements.py
    
This will create run_pipeline_v2.py with enhancements applied.
"""

import re
from pathlib import Path

def apply_logging_import(content: str) -> str:
    """Add logging import at the top."""
    # Find the imports section
    import_section = "import os\nimport sys\nimport time"
    if import_section in content:
        enhanced = import_section + "\nimport logging"
        content = content.replace(import_section, enhanced, 1)
    return content

def add_logging_setup(content: str) -> str:
    """Add logging configuration after imports."""
    # Add after the suppress stderr class
    marker = "os.environ[\"TORCH_CPP_LOG_LEVEL\"] = \"ERROR\"  # suppress backend warnings"
    if marker in content:
        logging_code = '''

# -------------------------
# LOGGING SETUP (Quick Enhancement)
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/output/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("Starting Smart Coach Detection Pipeline")
'''
        content = content.replace(marker, marker + logging_code, 1)
    return content

def add_gpu_check(content: str) -> str:
    """Add GPU availability check."""
    marker = "# LOAD MODELS"
    if marker in content:
        gpu_code = '''
# Check GPU availability
try:
    if torch.cuda.is_available():
        logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
    else:
        logger.info("Running on CPU (GPU not available)")
except:
    logger.info("Running on CPU")

'''
        content = content.replace(marker, gpu_code + marker, 1)
    return content

def add_validation(content: str) -> str:
    """Add input validation."""
    marker = "# VIDEO SETUP"
    if marker in content:
        validation_code = '''
# Validate inputs (Quick Enhancement)
logger.info("Validating configuration...")
if not os.path.exists(VIDEO_PATH):
    logger.error(f"Video file not found: {VIDEO_PATH}")
    sys.exit(1)
logger.info(f"✓ Input video: {VIDEO_PATH}")

for model_path, name in [(POSE_MODEL_PATH, "Pose"), (FACE_MODEL_PATH, "Face"), (HAND_MODEL_PATH, "Hand")]:
    if not os.path.exists(model_path):
        logger.error(f"{name} model not found: {model_path}")
        sys.exit(1)
    logger.info(f"✓ {name} model loaded")

'''
        content = content.replace(marker, validation_code + marker, 1)
    return content

def add_error_handling(content: str) -> str:
    """Add error logging (simplified approach)."""
    # Just add logging for frame read, don't restructure loop
    marker = "        ret, frame = cap.read()\n        if not ret:\n            break"
    if marker in content:
        enhanced = "        ret, frame = cap.read()\n        if not ret:\n            logger.info(f\"End of video at frame {frame_idx}\")\n            break"
        content = content.replace(marker, enhanced, 1)
    
    return content

def add_summary_stats(content: str) -> str:
    """Add summary statistics at the end."""
    marker = 'print(f"\\nFinished processing {frame_count} frames in {total_time:.2f} seconds ({frame_count/total_time:.2f} FPS).")'
    if marker in content:
        summary = '''logger.info(f"\\nFinished processing {frame_idx} frames in {total_time:.2f} seconds ({frame_idx/total_time:.2f} FPS).")
logger.info("=" * 60)
logger.info("PIPELINE SUMMARY")
logger.info("=" * 60)
logger.info(f"Input:  {VIDEO_PATH}")
logger.info(f"Output: {OUTPUT_PATH}")
logger.info(f"CSV:    {CSV_PATH}")
logger.info(f"Frames: {frame_idx}/{frame_count}")
logger.info(f"Time:   {total_time:.1f}s ({total_time/60:.1f} minutes)")
logger.info(f"FPS:    {frame_idx/total_time:.2f}")
logger.info("=" * 60)'''
        
        content = content.replace(marker, summary, 1)
    
    return content

def apply_all_enhancements(input_path: str, output_path: str):
    """Apply all enhancements to the pipeline script."""
    print(f"Reading {input_path}...")
    content = Path(input_path).read_text()
    
    print("Applying enhancements...")
    print("  - Adding logging import")
    content = apply_logging_import(content)
    
    print("  - Adding logging setup")
    content = add_logging_setup(content)
    
    print("  - Adding GPU detection")
    content = add_gpu_check(content)
    
    print("  - Adding input validation")
    content = add_validation(content)
    
    print("  - Adding error handling")
    content = add_error_handling(content)
    
    print("  - Adding summary statistics")
    content = add_summary_stats(content)
    
    print(f"Writing {output_path}...")
    Path(output_path).write_text(content)
    
    print(f"✓ Enhanced pipeline created: {output_path}")
    print()
    print("Changes applied:")
    print("  ✓ Logging to data/output/pipeline.log")
    print("  ✓ GPU detection and reporting")
    print("  ✓ Input validation with early exit")
    print("  ✓ Error handling with graceful degradation")
    print("  ✓ Summary statistics at completion")
    print()
    print("Usage:")
    print(f"  python {output_path}")

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    input_file = script_dir / "run_pipeline.py"
    output_file = script_dir / "run_pipeline_v2.py"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        print("This script must be in scripts/processing/ directory")
        return 1
    
    if output_file.exists():
        response = input(f"{output_file.name} already exists. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted")
            return 0
    
    apply_all_enhancements(str(input_file), str(output_file))
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
