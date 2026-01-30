"""
Firearm Detection Module for Smart Coach

Provides firearm detection and muzzle direction estimation using YOLOv8 object detection.

Design Approach:
- Use YOLOv8 for object detection (firearms, handguns)
- Calculate muzzle direction from bounding box orientation
- Hybrid approach: Use detection when confident, fall back to arm kinematics
- Temporal smoothing for stability
"""

import numpy as np
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
import cv2


@dataclass
class FirearmDetection:
    """Result from firearm detection."""
    bbox: np.ndarray  # [x1, y1, x2, y2]
    confidence: float
    class_name: str
    muzzle_point: Optional[np.ndarray] = None  # Estimated [x, y] of muzzle
    grip_point: Optional[np.ndarray] = None    # Estimated [x, y] of grip
    orientation_angle: float = 0.0  # Degrees from horizontal


class FirearmDetector:
    """
    Detects firearms in video frames and estimates muzzle direction.
    
    Uses YOLOv8 object detection with temporal smoothing for stability.
    Falls back to arm kinematics when detection confidence is low.
    """
    
    def __init__(
        self,
        model,  # YOLO model instance
        confidence_threshold: float = 0.4,
        target_classes: List[str] = None,
        smoothing_alpha: float = 0.7,
        buffer_size: int = 5
    ):
        """
        Initialize firearm detector.
        
        Args:
            model: YOLOv8 model instance
            confidence_threshold: Minimum confidence for detection
            target_classes: List of class names to detect (e.g., ['gun', 'handgun', 'pistol'])
            smoothing_alpha: Temporal smoothing factor (0-1, higher = more smoothing)
            buffer_size: Number of recent detections to buffer
        """
        self.model = model
        self.confidence_threshold = confidence_threshold
        self.target_classes = target_classes or ['gun', 'handgun', 'pistol', 'firearm', 'weapon']
        self.smoothing_alpha = smoothing_alpha
        self.buffer_size = buffer_size
        
        # State for temporal smoothing
        self.prev_bbox = None
        self.prev_orientation = None
        self.detection_buffer = []
        
    def detect(self, frame: np.ndarray) -> Optional[FirearmDetection]:
        """
        Detect firearm in frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            FirearmDetection object if detected, None otherwise
        """
        # Run YOLO detection
        results = self.model(frame, conf=self.confidence_threshold, verbose=False)
        
        if len(results) == 0 or len(results[0].boxes) == 0:
            return None
        
        # Find highest confidence detection matching target classes
        best_detection = None
        best_conf = 0.0
        
        for box in results[0].boxes:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            
            # Get class name
            if hasattr(results[0], 'names'):
                cls_name = results[0].names[cls_id].lower()
            else:
                cls_name = f"class_{cls_id}"
            
            # Check if this is a target class
            is_target = any(target in cls_name for target in self.target_classes)
            
            if is_target and conf > best_conf:
                best_conf = conf
                bbox = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                best_detection = (bbox, conf, cls_name)
        
        if best_detection is None:
            return None
        
        bbox, conf, cls_name = best_detection
        
        # Apply temporal smoothing to bbox
        if self.prev_bbox is not None:
            bbox = self.smoothing_alpha * self.prev_bbox + (1 - self.smoothing_alpha) * bbox
        
        self.prev_bbox = bbox
        
        # Calculate firearm properties
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = x2 - x1
        height = y2 - y1
        
        # Estimate muzzle and grip points
        # Assumption: Longer dimension is barrel direction
        # Muzzle is at the end of longer dimension
        if width > height:
            # Horizontal orientation
            muzzle_point = np.array([x2, center_y])  # Right end
            grip_point = np.array([x1, center_y])    # Left end
            orientation_angle = 0.0
        else:
            # Vertical orientation
            muzzle_point = np.array([center_x, y1])  # Top end
            grip_point = np.array([center_x, y2])    # Bottom end
            orientation_angle = 90.0
        
        # Calculate orientation from bounding box aspect ratio
        # This is a simplified heuristic - more sophisticated methods could use
        # rotated bounding boxes or keypoint detection on the firearm
        dx = muzzle_point[0] - grip_point[0]
        dy = muzzle_point[1] - grip_point[1]
        orientation_angle = np.degrees(np.arctan2(dy, dx))
        
        # Apply smoothing to orientation
        if self.prev_orientation is not None:
            # Handle angle wrapping
            angle_diff = orientation_angle - self.prev_orientation
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360
            
            orientation_angle = self.prev_orientation + (1 - self.smoothing_alpha) * angle_diff
        
        self.prev_orientation = orientation_angle
        
        detection = FirearmDetection(
            bbox=bbox,
            confidence=conf,
            class_name=cls_name,
            muzzle_point=muzzle_point,
            grip_point=grip_point,
            orientation_angle=orientation_angle
        )
        
        # Add to buffer
        self.detection_buffer.append(detection)
        if len(self.detection_buffer) > self.buffer_size:
            self.detection_buffer.pop(0)
        
        return detection
    
    def get_muzzle_direction_vector(
        self,
        detection: Optional[FirearmDetection],
        normalize: bool = True
    ) -> Optional[np.ndarray]:
        """
        Get muzzle direction as a unit vector.
        
        Args:
            detection: FirearmDetection object
            normalize: Whether to normalize to unit vector
            
        Returns:
            Direction vector [dx, dy] or None if no detection
        """
        if detection is None or detection.muzzle_point is None or detection.grip_point is None:
            return None
        
        direction = detection.muzzle_point - detection.grip_point
        
        if normalize:
            norm = np.linalg.norm(direction)
            if norm < 1e-6:
                return None
            direction = direction / norm
        
        return direction
    
    def calculate_muzzle_elevation(self, detection: Optional[FirearmDetection]) -> float:
        """
        Calculate muzzle elevation angle from horizontal.
        
        Args:
            detection: FirearmDetection object
            
        Returns:
            Elevation angle in degrees (positive = up, negative = down)
        """
        if detection is None:
            return 0.0
        
        direction = self.get_muzzle_direction_vector(detection, normalize=False)
        if direction is None:
            return 0.0
        
        # In image coordinates, y increases downward
        # Negative dy means upward elevation
        angle_rad = np.arctan2(-direction[1], direction[0])
        return np.degrees(angle_rad)
    
    def is_detection_stable(self, min_consecutive: int = 3) -> bool:
        """
        Check if firearm detection is stable over recent frames.
        
        Args:
            min_consecutive: Minimum number of consecutive detections required
            
        Returns:
            True if detection is stable
        """
        return len(self.detection_buffer) >= min_consecutive
    
    def reset(self):
        """Reset detector state (for new video or scene change)."""
        self.prev_bbox = None
        self.prev_orientation = None
        self.detection_buffer = []


def fuse_firearm_and_arm_estimates(
    firearm_direction: Optional[np.ndarray],
    arm_direction: Optional[np.ndarray],
    firearm_confidence: float,
    confidence_threshold: float = 0.6,
    blend_weight: float = 0.7
) -> Tuple[Optional[np.ndarray], str]:
    """
    Fuse firearm detection and arm kinematics estimates.
    
    Uses firearm detection when confidence is high, blends when moderate,
    falls back to arms when low or no detection.
    
    Args:
        firearm_direction: Direction vector from firearm detection
        arm_direction: Direction vector from arm kinematics
        firearm_confidence: Detection confidence (0-1)
        confidence_threshold: Threshold for using firearm vs arms
        blend_weight: Weight for firearm vs arms when blending (0-1)
        
    Returns:
        Tuple of (fused_direction, source_string)
        source_string is one of: 'firearm', 'blended', 'arms', 'none'
    """
    # No estimates available
    if firearm_direction is None and arm_direction is None:
        return None, 'none'
    
    # Only arm estimate available
    if firearm_direction is None:
        return arm_direction, 'arms'
    
    # Only firearm estimate available
    if arm_direction is None:
        return firearm_direction, 'firearm'
    
    # Both available - decide how to fuse
    if firearm_confidence >= confidence_threshold:
        # High confidence - use firearm
        return firearm_direction, 'firearm'
    elif firearm_confidence >= confidence_threshold * 0.5:
        # Moderate confidence - blend
        fused = blend_weight * firearm_direction + (1 - blend_weight) * arm_direction
        # Normalize
        norm = np.linalg.norm(fused)
        if norm > 1e-6:
            fused = fused / norm
        return fused, 'blended'
    else:
        # Low confidence - use arms
        return arm_direction, 'arms'


def check_muzzle_body_intersection(
    muzzle_point: np.ndarray,
    muzzle_direction: np.ndarray,
    body_mask: np.ndarray,
    ray_length: int = 200
) -> Tuple[bool, float]:
    """
    Check if muzzle direction ray intersects with body mask.
    
    Args:
        muzzle_point: Starting point [x, y]
        muzzle_direction: Direction vector [dx, dy] (normalized)
        body_mask: Binary mask of body (1 = body, 0 = background)
        ray_length: Length of ray to check (pixels)
        
    Returns:
        Tuple of (intersects, distance_to_intersection)
    """
    if body_mask is None or muzzle_point is None or muzzle_direction is None:
        return False, 0.0
    
    h, w = body_mask.shape[:2]
    x, y = muzzle_point
    dx, dy = muzzle_direction
    
    # Cast ray from muzzle point
    for dist in range(0, ray_length, 2):  # Check every 2 pixels for efficiency
        px = int(x + dx * dist)
        py = int(y + dy * dist)
        
        # Check bounds
        if px < 0 or px >= w or py < 0 or py >= h:
            break
        
        # Check if ray intersects body
        if body_mask[py, px] > 0:
            return True, dist
    
    return False, 0.0


def draw_firearm_detection(
    frame: np.ndarray,
    detection: Optional[FirearmDetection],
    color: Tuple[int, int, int] = (0, 255, 255),  # Yellow
    thickness: int = 2
) -> np.ndarray:
    """
    Draw firearm detection overlay on frame.
    
    Args:
        frame: Input frame
        detection: FirearmDetection object
        color: Color for bounding box (BGR)
        thickness: Line thickness
        
    Returns:
        Frame with detection overlay
    """
    if detection is None:
        return frame
    
    frame = frame.copy()
    
    # Draw bounding box
    x1, y1, x2, y2 = detection.bbox.astype(int)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    
    # Draw muzzle and grip points
    if detection.muzzle_point is not None:
        muzzle_pt = detection.muzzle_point.astype(int)
        cv2.circle(frame, tuple(muzzle_pt), 5, (0, 0, 255), -1)  # Red dot at muzzle
        cv2.putText(frame, "M", (muzzle_pt[0] + 10, muzzle_pt[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    if detection.grip_point is not None:
        grip_pt = detection.grip_point.astype(int)
        cv2.circle(frame, tuple(grip_pt), 5, (0, 255, 0), -1)  # Green dot at grip
        cv2.putText(frame, "G", (grip_pt[0] + 10, grip_pt[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw direction arrow
    if detection.muzzle_point is not None and detection.grip_point is not None:
        muzzle_pt = detection.muzzle_point.astype(int)
        direction = detection.muzzle_point - detection.grip_point
        direction = direction / np.linalg.norm(direction) * 100  # 100 pixel arrow
        end_pt = (muzzle_pt + direction).astype(int)
        cv2.arrowedLine(frame, tuple(muzzle_pt), tuple(end_pt), (255, 0, 255), thickness)
    
    # Draw label
    label = f"{detection.class_name}: {detection.confidence:.2f}"
    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
               0.6, color, 2)
    
    return frame
