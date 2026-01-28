"""
Configuration Helper for Detection Pipeline

Provides easy-to-use configuration management for the detection pipeline.
Supports loading from YAML files, environment variables, and command-line args.

Usage:
    from pipeline_config import PipelineConfig
    
    # Load default configuration
    config = PipelineConfig.load_default()
    
    # Load from YAML
    config = PipelineConfig.load_from_yaml('config/my_config.yaml')
    
    # Override specific values
    config.temp_alpha = 0.7
    config.conf_thres = 0.3
    
    # Save configuration
    config.save_to_yaml('config/saved_config.yaml')
"""

import yaml
from dataclasses import dataclass, asdict, fields
from pathlib import Path
from typing import Optional

@dataclass
class PipelineConfig:
    """Configuration for the detection pipeline."""
    
    # I/O Paths
    video_path: str = "data/input/test_video.mp4"
    output_path: str = "data/output/output_full.mp4"
    csv_path: str = "data/output/analytics.csv"
    
    # Model Paths
    pose_model_path: str = "data/models/yolov8m-pose.pt"
    face_model_path: str = "data/models/yolov8n-face.pt"
    hand_model_path: str = "data/models/hand_landmarker.task"
    
    # Detection Parameters
    temp_alpha: float = 0.6  # Temporal smoothing (0.6 = faster response)
    conf_thres: float = 0.2  # Confidence threshold
    
    # Visualization Parameters
    alpha_body: float = 0.35  # Body mask overlay opacity
    alpha_cone: float = 0.25  # Gaze cone opacity
    gaze_length: int = 2000  # Gaze ray length in pixels
    
    # Gaze Parameters
    gaze_cone_h_angle: float = 16.0  # Horizontal half-angle (degrees)
    gaze_cone_v_angle: float = 9.0   # Vertical half-angle (degrees)
    cone_origin_offset: int = 40     # Distance behind eyes (pixels)
    max_gaze_rot: float = 0.12       # Max rotation per frame (rad)
    gaze_buffer_len: int = 9         # Median filter buffer size
    torso_blend: float = 0.25        # Torso weight in gaze blend (0-1)
    gaze_lerp_alpha: float = 0.15    # Gaze smoothing factor
    gaze_2d_outlier_threshold: float = 0.15  # Outlier rejection threshold
    torso_lerp_alpha: float = 0.3    # Torso smoothing factor
    torso_consistency_threshold: float = 0.5  # Min dot product for torso update
    
    # Performance Parameters
    enable_gpu: bool = True          # Use GPU if available
    maskrcnn_cache_frames: int = 5   # Cache Mask R-CNN results every N frames
    skip_hand_on_low_conf: bool = False  # Skip hand detection if pose conf < threshold
    
    # Logging
    verbose: bool = False            # Enable verbose logging
    log_performance: bool = False    # Log model inference times
    
    @classmethod
    def load_default(cls) -> 'PipelineConfig':
        """Load default configuration."""
        return cls()
    
    @classmethod
    def load_from_yaml(cls, yaml_path: str) -> 'PipelineConfig':
        """Load configuration from YAML file.
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            PipelineConfig instance with values from YAML
            
        Example YAML:
            detection:
              temp_alpha: 0.7
              conf_thres: 0.3
            
            models:
              pose_model_path: "data/models/yolov8l-pose.pt"
            
            performance:
              enable_gpu: true
              maskrcnn_cache_frames: 10
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Flatten nested structure if present
        flat_data = {}
        for section, values in data.items():
            if isinstance(values, dict):
                flat_data.update(values)
            else:
                flat_data[section] = values
        
        # Create config with only recognized fields
        valid_fields = {f.name for f in fields(cls)}
        kwargs = {k: v for k, v in flat_data.items() if k in valid_fields}
        
        return cls(**kwargs)
    
    def save_to_yaml(self, yaml_path: str):
        """Save configuration to YAML file.
        
        Args:
            yaml_path: Path where YAML will be saved
        """
        Path(yaml_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Organize into logical sections
        config_dict = asdict(self)
        
        organized = {
            'io_paths': {
                'video_path': config_dict['video_path'],
                'output_path': config_dict['output_path'],
                'csv_path': config_dict['csv_path'],
            },
            'models': {
                'pose_model_path': config_dict['pose_model_path'],
                'face_model_path': config_dict['face_model_path'],
                'hand_model_path': config_dict['hand_model_path'],
            },
            'detection': {
                'temp_alpha': config_dict['temp_alpha'],
                'conf_thres': config_dict['conf_thres'],
            },
            'visualization': {
                'alpha_body': config_dict['alpha_body'],
                'alpha_cone': config_dict['alpha_cone'],
                'gaze_length': config_dict['gaze_length'],
            },
            'gaze': {
                'gaze_cone_h_angle': config_dict['gaze_cone_h_angle'],
                'gaze_cone_v_angle': config_dict['gaze_cone_v_angle'],
                'cone_origin_offset': config_dict['cone_origin_offset'],
                'max_gaze_rot': config_dict['max_gaze_rot'],
                'gaze_buffer_len': config_dict['gaze_buffer_len'],
                'torso_blend': config_dict['torso_blend'],
                'gaze_lerp_alpha': config_dict['gaze_lerp_alpha'],
                'gaze_2d_outlier_threshold': config_dict['gaze_2d_outlier_threshold'],
                'torso_lerp_alpha': config_dict['torso_lerp_alpha'],
                'torso_consistency_threshold': config_dict['torso_consistency_threshold'],
            },
            'performance': {
                'enable_gpu': config_dict['enable_gpu'],
                'maskrcnn_cache_frames': config_dict['maskrcnn_cache_frames'],
                'skip_hand_on_low_conf': config_dict['skip_hand_on_low_conf'],
            },
            'logging': {
                'verbose': config_dict['verbose'],
                'log_performance': config_dict['log_performance'],
            }
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(organized, f, default_flow_style=False, sort_keys=False)
    
    def validate(self) -> bool:
        """Validate configuration values.
        
        Returns:
            True if all validations pass
            
        Raises:
            ValueError: If any parameter is out of valid range
            FileNotFoundError: If required files don't exist
        """
        # Validate ranges
        if not 0.0 <= self.temp_alpha <= 1.0:
            raise ValueError(f"temp_alpha must be in [0, 1], got {self.temp_alpha}")
        if not 0.0 <= self.conf_thres <= 1.0:
            raise ValueError(f"conf_thres must be in [0, 1], got {self.conf_thres}")
        if self.gaze_buffer_len < 1:
            raise ValueError(f"gaze_buffer_len must be >= 1, got {self.gaze_buffer_len}")
        if not 0.0 <= self.torso_blend <= 1.0:
            raise ValueError(f"torso_blend must be in [0, 1], got {self.torso_blend}")
        
        # Check file existence
        if not Path(self.video_path).exists():
            raise FileNotFoundError(f"Video not found: {self.video_path}")
        if not Path(self.pose_model_path).exists():
            raise FileNotFoundError(f"Pose model not found: {self.pose_model_path}")
        if not Path(self.face_model_path).exists():
            raise FileNotFoundError(f"Face model not found: {self.face_model_path}")
        if not Path(self.hand_model_path).exists():
            raise FileNotFoundError(f"Hand model not found: {self.hand_model_path}")
        
        return True
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        lines = ["PipelineConfig:"]
        lines.append(f"  Input:  {self.video_path}")
        lines.append(f"  Output: {self.output_path}")
        lines.append(f"  Params: temp_alpha={self.temp_alpha}, conf_thres={self.conf_thres}")
        lines.append(f"  GPU:    {self.enable_gpu}")
        return "\n".join(lines)

# Example usage
if __name__ == "__main__":
    # Create default config
    config = PipelineConfig.load_default()
    print("Default Configuration:")
    print(config)
    print()
    
    # Save to YAML
    config.save_to_yaml("config/pipeline_config.yaml")
    print("Saved to config/pipeline_config.yaml")
    print()
    
    # Load from YAML
    loaded = PipelineConfig.load_from_yaml("config/pipeline_config.yaml")
    print("Loaded Configuration:")
    print(loaded)
    print()
    
    # Validate
    try:
        if loaded.validate():
            print("✓ Configuration valid")
    except (ValueError, FileNotFoundError) as e:
        print(f"✗ Validation failed: {e}")
