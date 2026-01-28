"""
Advanced metric calculations for Smart Coach pose detection.

This module provides enhanced metrics that extract more value from existing detections:
- Firearm orientation and muzzle direction
- Recoil detection and recovery
- Grip and hand positioning
- Stance and balance
- Temporal patterns (draw, reload, cadence)

All metrics are camera-invariant through normalization and physically explainable.
"""
import numpy as np
from typing import Dict, Optional, Tuple, List
from collections import deque


def calculate_muzzle_vector_from_arms(
    wrist: np.ndarray,
    elbow: np.ndarray,
    shoulder: np.ndarray,
    normalize: bool = True
) -> Optional[np.ndarray]:
    """Calculate muzzle direction vector from arm kinematics.
    
    Uses wrist-to-elbow vector as primary direction, with shoulder for validation.
    
    Args:
        wrist: Wrist position [x, y]
        elbow: Elbow position [x, y]
        shoulder: Shoulder position [x, y]
        normalize: Whether to normalize to unit vector
        
    Returns:
        Muzzle direction vector [dx, dy] or None if invalid
    """
    if wrist is None or elbow is None:
        return None
    
    # Primary direction: wrist -> forward from elbow
    direction = wrist - elbow
    
    # Validate arm is extended (not folded back)
    if shoulder is not None:
        upper_arm = elbow - shoulder
        # Check angle isn't too acute (arm folded)
        dot = np.dot(direction, upper_arm)
        if dot < 0:  # Pointing backward
            return None
    
    if normalize:
        norm = np.linalg.norm(direction)
        if norm < 1e-6:
            return None
        direction = direction / norm
    
    return direction


def calculate_muzzle_elevation(muzzle_vector: np.ndarray) -> float:
    """Calculate elevation angle of muzzle from horizontal.
    
    Args:
        muzzle_vector: Direction vector [dx, dy]
        
    Returns:
        Elevation angle in degrees (positive = up, negative = down)
    """
    if muzzle_vector is None or len(muzzle_vector) != 2:
        return 0.0
    
    # Note: In image coordinates, y increases downward
    # So negative dy = upward elevation
    angle_rad = np.arctan2(-muzzle_vector[1], muzzle_vector[0])
    return np.degrees(angle_rad)


def detect_recoil_impulse(
    wrist_positions: List[np.ndarray],
    time_window: int = 3,
    threshold_multiplier: float = 2.0
) -> Tuple[bool, float]:
    """Detect recoil impulse from rapid wrist acceleration.
    
    Args:
        wrist_positions: Recent wrist positions (at least 3 frames)
        time_window: Number of frames to analyze
        threshold_multiplier: Sensitivity multiplier (higher = less sensitive)
        
    Returns:
        Tuple of (recoil_detected, peak_acceleration)
    """
    if len(wrist_positions) < 3:
        return False, 0.0
    
    # Calculate velocities (frame-to-frame)
    velocities = []
    for i in range(1, min(len(wrist_positions), time_window + 1)):
        vel = wrist_positions[-i] - wrist_positions[-i-1]
        velocities.append(np.linalg.norm(vel))
    
    if len(velocities) < 2:
        return False, 0.0
    
    # Calculate accelerations (velocity change)
    accelerations = []
    for i in range(1, len(velocities)):
        accel = abs(velocities[i] - velocities[i-1])
        accelerations.append(accel)
    
    if not accelerations:
        return False, 0.0
    
    peak_accel = max(accelerations)
    mean_accel = np.mean(accelerations)
    
    # Detect if peak significantly exceeds baseline
    recoil_detected = peak_accel > (mean_accel * threshold_multiplier)
    
    return recoil_detected, peak_accel


def calculate_hand_distance(
    left_wrist: Optional[np.ndarray],
    right_wrist: Optional[np.ndarray],
    normalize_by: float = 1.0
) -> float:
    """Calculate distance between hands.
    
    Args:
        left_wrist: Left wrist position [x, y]
        right_wrist: Right wrist position [x, y]
        normalize_by: Normalization factor (e.g., shoulder_width)
        
    Returns:
        Normalized distance between hands
    """
    if left_wrist is None or right_wrist is None:
        return 0.0
    
    distance = np.linalg.norm(left_wrist - right_wrist)
    return distance / normalize_by if normalize_by > 0 else 0.0


def calculate_grip_symmetry(
    left_hand_detected: bool,
    right_hand_detected: bool
) -> float:
    """Calculate grip symmetry (both hands present).
    
    Args:
        left_hand_detected: Whether left hand is detected
        right_hand_detected: Whether right hand is detected
        
    Returns:
        1.0 if both hands detected, 0.0 otherwise
    """
    return 1.0 if (left_hand_detected and right_hand_detected) else 0.0


def calculate_center_of_mass(keypoints: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
    """Estimate center of mass from body keypoints.
    
    Uses weighted average of torso and hip keypoints.
    
    Args:
        keypoints: Dictionary mapping keypoint index to position
        
    Returns:
        Estimated center of mass [x, y] or None
    """
    # Key points for COM: shoulders (5,6), hips (11,12)
    com_points = []
    weights = []
    
    # Shoulders (lower weight)
    for idx in [5, 6]:
        if idx in keypoints:
            com_points.append(keypoints[idx])
            weights.append(0.3)
    
    # Hips (higher weight)
    for idx in [11, 12]:
        if idx in keypoints:
            com_points.append(keypoints[idx])
            weights.append(0.7)
    
    if not com_points:
        return None
    
    com_points = np.array(com_points)
    weights = np.array(weights)
    weights = weights / np.sum(weights)  # Normalize
    
    com = np.average(com_points, axis=0, weights=weights)
    return com


def calculate_body_lean_angle(
    shoulder_center: np.ndarray,
    hip_center: np.ndarray
) -> float:
    """Calculate body lean angle from vertical.
    
    Args:
        shoulder_center: Center point between shoulders [x, y]
        hip_center: Center point between hips [x, y]
        
    Returns:
        Lean angle in degrees (positive = forward, negative = backward)
    """
    if shoulder_center is None or hip_center is None:
        return 0.0
    
    # Vector from hips to shoulders
    torso_vector = shoulder_center - hip_center
    
    # Vertical reference (note: y increases downward in image coords)
    vertical = np.array([0, -1])  # Pointing up
    
    # Calculate angle
    dot = np.dot(torso_vector, vertical)
    norm = np.linalg.norm(torso_vector)
    
    if norm < 1e-6:
        return 0.0
    
    cos_angle = dot / norm
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle_rad = np.arccos(cos_angle)
    
    # Determine sign (forward vs backward)
    # Forward lean has positive x component
    sign = 1.0 if torso_vector[0] > 0 else -1.0
    
    return sign * np.degrees(angle_rad)


def detect_arm_extension_event(
    arm_extension: float,
    previous_extensions: List[float],
    threshold_delta: float = 0.3
) -> bool:
    """Detect rapid arm extension (e.g., draw or presentation).
    
    Args:
        arm_extension: Current arm extension (normalized)
        previous_extensions: Recent extension values
        threshold_delta: Minimum extension increase to trigger
        
    Returns:
        True if rapid extension detected
    """
    if len(previous_extensions) < 2:
        return False
    
    # Calculate recent change
    recent_avg = np.mean(previous_extensions[-3:])
    delta = arm_extension - recent_avg
    
    return delta > threshold_delta


def detect_hand_separation_event(
    hand_distance: float,
    previous_distances: List[float],
    threshold_delta: float = 0.5
) -> bool:
    """Detect hand separation (e.g., reload or equipment manipulation).
    
    Args:
        hand_distance: Current hand distance (normalized)
        previous_distances: Recent distance values
        threshold_delta: Minimum distance increase to trigger
        
    Returns:
        True if significant separation detected
    """
    if len(previous_distances) < 2:
        return False
    
    # Calculate recent baseline
    recent_avg = np.mean(previous_distances[-5:])
    delta = hand_distance - recent_avg
    
    return delta > threshold_delta


class RecoilDetector:
    """Stateful recoil detection with recovery time measurement."""
    
    def __init__(self, window_size: int = 5):
        """Initialize recoil detector.
        
        Args:
            window_size: Number of frames to track
        """
        self.window_size = window_size
        self.wrist_history = deque(maxlen=window_size)
        self.in_recoil = False
        self.recoil_start_frame = None
        self.recovery_time = 0
    
    def update(self, wrist_pos: np.ndarray, frame_idx: int) -> Dict:
        """Update with new wrist position.
        
        Args:
            wrist_pos: Current wrist position [x, y]
            frame_idx: Current frame index
            
        Returns:
            Dictionary with recoil metrics
        """
        self.wrist_history.append(wrist_pos)
        
        if len(self.wrist_history) < 3:
            return {
                'recoil_detected': False,
                'peak_acceleration': 0.0,
                'recovery_time_frames': 0
            }
        
        # Detect recoil
        recoil_detected, peak_accel = detect_recoil_impulse(
            list(self.wrist_history)
        )
        
        # State machine for recovery time
        if recoil_detected and not self.in_recoil:
            # New recoil event
            self.in_recoil = True
            self.recoil_start_frame = frame_idx
            self.recovery_time = 0
        elif self.in_recoil:
            # In recovery phase
            if not recoil_detected:
                # Check if stabilized
                recent_accels = []
                for i in range(1, min(len(self.wrist_history), 4)):
                    vel = np.linalg.norm(
                        self.wrist_history[-i] - self.wrist_history[-i-1]
                    )
                    recent_accels.append(vel)
                
                if recent_accels and max(recent_accels) < 2.0:  # Stabilized
                    self.recovery_time = frame_idx - self.recoil_start_frame
                    self.in_recoil = False
        
        return {
            'recoil_detected': recoil_detected,
            'peak_acceleration': peak_accel,
            'recovery_time_frames': self.recovery_time if not self.in_recoil else 0
        }


class DrawDetector:
    """Detect draw events from holster to presentation."""
    
    def __init__(self, extension_threshold: float = 0.5):
        """Initialize draw detector.
        
        Args:
            extension_threshold: Minimum extension to consider "presented"
        """
        self.extension_threshold = extension_threshold
        self.extension_history = deque(maxlen=10)
        self.in_draw = False
        self.draw_start_frame = None
    
    def update(self, arm_extension: float, frame_idx: int) -> Dict:
        """Update with current arm extension.
        
        Args:
            arm_extension: Normalized arm extension (shoulder to wrist distance)
            frame_idx: Current frame index
            
        Returns:
            Dictionary with draw event metrics
        """
        self.extension_history.append(arm_extension)
        
        if len(self.extension_history) < 3:
            return {'draw_detected': False, 'draw_time_frames': 0}
        
        # State machine
        if not self.in_draw:
            # Check if starting draw (was low, now increasing)
            if (np.mean(list(self.extension_history)[-5:]) < 0.3 and
                arm_extension > 0.4):
                self.in_draw = True
                self.draw_start_frame = frame_idx
        else:
            # Check if draw complete (extension stabilized above threshold)
            if arm_extension > self.extension_threshold:
                recent_stable = all(
                    e > self.extension_threshold * 0.9
                    for e in list(self.extension_history)[-3:]
                )
                if recent_stable:
                    draw_time = frame_idx - self.draw_start_frame
                    self.in_draw = False
                    return {'draw_detected': True, 'draw_time_frames': draw_time}
        
        return {'draw_detected': False, 'draw_time_frames': 0}


if __name__ == "__main__":
    # Demo usage
    print("Advanced Metrics Demo")
    print("=" * 50)
    
    # Test muzzle vector
    wrist = np.array([100, 50])
    elbow = np.array([80, 60])
    shoulder = np.array([60, 70])
    
    muzzle_vec = calculate_muzzle_vector_from_arms(wrist, elbow, shoulder)
    print(f"\nMuzzle vector: {muzzle_vec}")
    print(f"Muzzle elevation: {calculate_muzzle_elevation(muzzle_vec):.1f}°")
    
    # Test recoil detection
    wrist_history = [
        np.array([100, 50]),
        np.array([100, 51]),
        np.array([100, 55]),  # Sudden movement
        np.array([100, 52]),
    ]
    recoil, accel = detect_recoil_impulse(wrist_history)
    print(f"\nRecoil detected: {recoil}, Peak accel: {accel:.2f}")
    
    # Test COM
    keypoints = {
        5: np.array([50, 40]),  # Left shoulder
        6: np.array([70, 40]),  # Right shoulder
        11: np.array([52, 80]), # Left hip
        12: np.array([68, 80]), # Right hip
    }
    com = calculate_center_of_mass(keypoints)
    print(f"\nCenter of mass: {com}")
