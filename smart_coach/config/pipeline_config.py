"""
Pipeline configuration with validation and flexibility.
Supports environment variables and programmatic overrides.
"""
import os
from dataclasses import dataclass


@dataclass
class PipelineConfig:
    """Configuration for the Smart Coach detection pipeline.
    
    All parameters have sensible defaults and can be overridden via:
    1. Environment variables (SMARTCOACH_<PARAM_NAME>)
    2. Direct attribute assignment
    """
    
    # ===== Input/Output Paths =====
    video_path: str = "data/input/test_video.mp4"
    output_video_path: str = "data/output/output_full.mp4"
    output_csv_path: str = "data/output/analytics.csv"
    
    # ===== Model Paths =====
    pose_model_path: str = "data/models/yolov8m-pose.pt"
    face_model_path: str = "data/models/yolov8n-face.pt"
    hand_model_path: str = "data/models/hand_landmarker.task"
    
    # ===== Detection Parameters =====
    conf_threshold: float = 0.2
    temp_alpha: float = 0.6  # Temporal smoothing (0=all old, 1=all new)
    
    # ===== Performance Optimization =====
    enable_maskrcnn_cache: bool = True
    maskrcnn_cache_frames: int = 5  # Reuse mask for N frames
    enable_gpu: bool = True  # Auto-detected if not specified
    
    # ===== Visualization =====
    alpha_body: float = 0.35
    alpha_cone: float = 0.25
    gaze_length: int = 2000
    gaze_cone_h_angle_deg: float = 16.0  # Horizontal half-angle in degrees
    gaze_cone_v_angle_deg: float = 9.0   # Vertical half-angle in degrees
    
    # ===== Advanced Gaze Parameters =====
    cone_origin_offset: int = 40
    max_gaze_rot: float = 0.12  # rad/frame
    gaze_buffer_len: int = 9
    torso_blend: float = 0.25
    gaze_lerp_alpha: float = 0.15
    gaze_2d_outlier_threshold: float = 0.15
    torso_lerp_alpha: float = 0.3
    torso_consistency_threshold: float = 0.5
    
    # ===== Validation & Robustness =====
    validate_inputs: bool = True  # Check files exist before processing
    fail_on_missing_models: bool = True
    max_consecutive_failures: int = 10  # Stop if N frames fail in a row
    
    # ===== Performance Tracking =====
    log_performance: bool = False
    performance_log_interval: int = 30  # Log every N frames
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._apply_env_overrides()
        self._validate()
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        # Check for environment variables with SMARTCOACH_ prefix
        env_mapping = {
            'SMARTCOACH_VIDEO_PATH': 'video_path',
            'SMARTCOACH_OUTPUT_VIDEO': 'output_video_path',
            'SMARTCOACH_OUTPUT_CSV': 'output_csv_path',
            'SMARTCOACH_CONF_THRESHOLD': ('conf_threshold', float),
            'SMARTCOACH_TEMP_ALPHA': ('temp_alpha', float),
            'SMARTCOACH_ENABLE_CACHE': ('enable_maskrcnn_cache', lambda x: x.lower() == 'true'),
            'SMARTCOACH_CACHE_FRAMES': ('maskrcnn_cache_frames', int),
            'SMARTCOACH_ENABLE_GPU': ('enable_gpu', lambda x: x.lower() == 'true'),
        }
        
        for env_var, attr_info in env_mapping.items():
            if env_var in os.environ:
                if isinstance(attr_info, tuple):
                    attr_name, converter = attr_info
                    try:
                        setattr(self, attr_name, converter(os.environ[env_var]))
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Failed to parse {env_var}={os.environ[env_var]}: {e}")
                else:
                    setattr(self, attr_info, os.environ[env_var])
    
    def _validate(self):
        """Validate configuration values are in acceptable ranges."""
        # Validate thresholds
        if not 0.0 <= self.conf_threshold <= 1.0:
            raise ValueError(f"conf_threshold must be in [0, 1], got {self.conf_threshold}")
        
        if not 0.0 <= self.temp_alpha <= 1.0:
            raise ValueError(f"temp_alpha must be in [0, 1], got {self.temp_alpha}")
        
        # Validate cache frames
        if self.maskrcnn_cache_frames < 1:
            raise ValueError(f"maskrcnn_cache_frames must be >= 1, got {self.maskrcnn_cache_frames}")
        
        # Validate alpha values
        if not 0.0 <= self.alpha_body <= 1.0:
            raise ValueError(f"alpha_body must be in [0, 1], got {self.alpha_body}")
        
        if not 0.0 <= self.alpha_cone <= 1.0:
            raise ValueError(f"alpha_cone must be in [0, 1], got {self.alpha_cone}")
        
        # Validate max consecutive failures
        if self.max_consecutive_failures < 1:
            raise ValueError(f"max_consecutive_failures must be >= 1, got {self.max_consecutive_failures}")
    
    def validate_paths(self):
        """Validate that required files exist.
        
        Returns:
            tuple: (success: bool, missing_files: list)
        """
        if not self.validate_inputs:
            return True, []
        
        missing = []
        
        # Check input video
        if not os.path.exists(self.video_path):
            missing.append(f"Input video: {self.video_path}")
        
        # Check model files
        if self.fail_on_missing_models:
            for model_path, name in [
                (self.pose_model_path, "Pose model"),
                (self.face_model_path, "Face model"),
                (self.hand_model_path, "Hand model"),
            ]:
                if not os.path.exists(model_path):
                    missing.append(f"{name}: {model_path}")
        
        return len(missing) == 0, missing
    
    def __str__(self) -> str:
        """Return a formatted string representation of the config."""
        lines = ["Pipeline Configuration:"]
        lines.append("=" * 50)
        
        sections = {
            "Input/Output": ['video_path', 'output_video_path', 'output_csv_path'],
            "Models": ['pose_model_path', 'face_model_path', 'hand_model_path'],
            "Detection": ['conf_threshold', 'temp_alpha'],
            "Performance": ['enable_maskrcnn_cache', 'maskrcnn_cache_frames', 'enable_gpu'],
            "Visualization": ['alpha_body', 'alpha_cone', 'gaze_length'],
        }
        
        for section, attrs in sections.items():
            lines.append(f"\n{section}:")
            for attr in attrs:
                if hasattr(self, attr):
                    value = getattr(self, attr)
                    lines.append(f"  {attr}: {value}")
        
        return "\n".join(lines)


def get_default_config() -> PipelineConfig:
    """Get default configuration with current best practices.
    
    Returns:
        PipelineConfig with optimized defaults
    """
    return PipelineConfig(
        enable_maskrcnn_cache=True,
        maskrcnn_cache_frames=5,
        temp_alpha=0.6,
        conf_threshold=0.2,
    )


if __name__ == "__main__":
    # Demo: Create and save default config
    config = get_default_config()
    print(config)
    print("\nValidating paths...")
    success, missing = config.validate_paths()
    if success:
        print("✓ All paths valid")
    else:
        print("✗ Missing files:")
        for file in missing:
            print(f"  - {file}")
