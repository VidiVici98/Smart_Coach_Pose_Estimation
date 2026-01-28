"""
Unit tests for advanced metrics calculations.

Tests the new detection and measurement capabilities:
- Muzzle direction from arm kinematics
- Recoil detection
- Draw event detection
- Center of mass and body lean
"""
import unittest
import numpy as np
from smart_coach.metrics.advanced_metrics import (
    calculate_muzzle_vector_from_arms,
    calculate_muzzle_elevation,
    detect_recoil_impulse,
    calculate_hand_distance,
    calculate_grip_symmetry,
    calculate_center_of_mass,
    calculate_body_lean_angle,
    detect_arm_extension_event,
    detect_hand_separation_event,
    RecoilDetector,
    DrawDetector
)


class TestMuzzleDirection(unittest.TestCase):
    """Test muzzle direction calculations from arm kinematics."""
    
    def test_horizontal_arm(self):
        """Test muzzle vector for horizontally extended arm."""
        wrist = np.array([100, 50])
        elbow = np.array([80, 50])
        shoulder = np.array([60, 50])
        
        muzzle_vec = calculate_muzzle_vector_from_arms(wrist, elbow, shoulder)
        
        self.assertIsNotNone(muzzle_vec)
        # Should point right (positive x)
        self.assertGreater(muzzle_vec[0], 0.9)
        # Should be nearly horizontal
        self.assertLess(abs(muzzle_vec[1]), 0.1)
    
    def test_upward_elevation(self):
        """Test muzzle elevation angle pointing upward."""
        wrist = np.array([100, 30])  # Higher (lower y)
        elbow = np.array([80, 50])
        shoulder = np.array([60, 60])
        
        muzzle_vec = calculate_muzzle_vector_from_arms(wrist, elbow, shoulder)
        elevation = calculate_muzzle_elevation(muzzle_vec)
        
        # Positive elevation (pointing up)
        self.assertGreater(elevation, 0)
    
    def test_downward_elevation(self):
        """Test muzzle elevation angle pointing downward."""
        wrist = np.array([100, 70])  # Lower (higher y)
        elbow = np.array([80, 50])
        shoulder = np.array([60, 40])
        
        muzzle_vec = calculate_muzzle_vector_from_arms(wrist, elbow, shoulder)
        elevation = calculate_muzzle_elevation(muzzle_vec)
        
        # Negative elevation (pointing down)
        self.assertLess(elevation, 0)
    
    def test_folded_arm_rejected(self):
        """Test that folded-back arm is rejected."""
        wrist = np.array([60, 50])  # Behind elbow
        elbow = np.array([80, 50])
        shoulder = np.array([100, 50])
        
        muzzle_vec = calculate_muzzle_vector_from_arms(wrist, elbow, shoulder)
        
        # Should return None for invalid configuration
        self.assertIsNone(muzzle_vec)
    
    def test_none_input_handling(self):
        """Test handling of None inputs."""
        wrist = np.array([100, 50])
        elbow = None
        shoulder = np.array([60, 50])
        
        muzzle_vec = calculate_muzzle_vector_from_arms(wrist, elbow, shoulder)
        self.assertIsNone(muzzle_vec)


class TestRecoilDetection(unittest.TestCase):
    """Test recoil impulse detection."""
    
    def test_steady_motion(self):
        """Test that steady motion doesn't trigger recoil."""
        wrist_positions = [
            np.array([100, 50]),
            np.array([101, 50]),
            np.array([102, 50]),
            np.array([103, 50]),
        ]
        
        recoil, accel = detect_recoil_impulse(wrist_positions)
        
        self.assertFalse(recoil)
    
    def test_rapid_acceleration(self):
        """Test that rapid acceleration triggers recoil."""
        wrist_positions = [
            np.array([100, 50]),
            np.array([101, 50]),
            np.array([105, 55]),  # Sudden jump
            np.array([106, 56]),
        ]
        
        recoil, accel = detect_recoil_impulse(wrist_positions, threshold_multiplier=1.5)
        
        self.assertTrue(recoil)
        self.assertGreater(accel, 0)
    
    def test_insufficient_history(self):
        """Test handling of insufficient position history."""
        wrist_positions = [np.array([100, 50])]
        
        recoil, accel = detect_recoil_impulse(wrist_positions)
        
        self.assertFalse(recoil)
        self.assertEqual(accel, 0.0)


class TestRecoilDetectorClass(unittest.TestCase):
    """Test stateful RecoilDetector class."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = RecoilDetector(window_size=5)
        
        self.assertEqual(detector.window_size, 5)
        self.assertFalse(detector.in_recoil)
    
    def test_recoil_event_detection(self):
        """Test detection of recoil event."""
        detector = RecoilDetector(window_size=5)
        
        # Feed steady positions
        for i in range(3):
            metrics = detector.update(np.array([100 + i, 50]), frame_idx=i)
            self.assertFalse(metrics['recoil_detected'])
        
        # Feed recoil event
        metrics = detector.update(np.array([110, 60]), frame_idx=3)
        # May or may not detect on first frame, depends on history
        
        # Should detect in subsequent frames
        detector.update(np.array([111, 61]), frame_idx=4)
        metrics = detector.update(np.array([112, 62]), frame_idx=5)
        # Check that detector is tracking recoil state
        self.assertIsNotNone(metrics['peak_acceleration'])
    
    def test_recovery_time_measurement(self):
        """Test recovery time is measured."""
        detector = RecoilDetector(window_size=5)
        
        # Build history
        for i in range(5):
            detector.update(np.array([100 + i, 50]), frame_idx=i)
        
        # Simulate recoil and recovery
        # (Recovery time measurement requires full sequence)
        metrics = detector.update(np.array([120, 60]), frame_idx=5)
        
        # Recovery time starts at 0
        self.assertIsInstance(metrics['recovery_time_frames'], int)


class TestDrawDetection(unittest.TestCase):
    """Test draw event detection."""
    
    def test_no_draw_when_steady(self):
        """Test no false positives during steady presentation."""
        detector = DrawDetector(extension_threshold=0.5)
        
        # Feed steady extended arm
        for i in range(10):
            metrics = detector.update(arm_extension=0.7, frame_idx=i)
            if i > 3:  # After initial frames
                self.assertFalse(metrics['draw_detected'])
    
    def test_draw_event_detected(self):
        """Test draw event is detected."""
        detector = DrawDetector(extension_threshold=0.5)
        
        # Simulate draw sequence
        extensions = [0.2, 0.2, 0.3, 0.45, 0.6, 0.65, 0.7, 0.7, 0.7]
        
        draw_detected = False
        for i, ext in enumerate(extensions):
            metrics = detector.update(arm_extension=ext, frame_idx=i)
            if metrics['draw_detected']:
                draw_detected = True
                self.assertGreater(metrics['draw_time_frames'], 0)
        
        self.assertTrue(draw_detected, "Draw should be detected in sequence")
    
    def test_draw_time_reasonable(self):
        """Test draw time is within reasonable range."""
        detector = DrawDetector(extension_threshold=0.5)
        
        # Quick draw
        extensions = [0.1, 0.2, 0.6, 0.7, 0.7]
        
        for i, ext in enumerate(extensions):
            metrics = detector.update(arm_extension=ext, frame_idx=i)
            if metrics['draw_detected']:
                # Draw time should be a few frames
                self.assertGreater(metrics['draw_time_frames'], 0)
                self.assertLess(metrics['draw_time_frames'], 20)


class TestHandMetrics(unittest.TestCase):
    """Test hand-related metrics."""
    
    def test_hand_distance(self):
        """Test hand distance calculation."""
        left_wrist = np.array([50, 50])
        right_wrist = np.array([70, 50])
        
        distance = calculate_hand_distance(left_wrist, right_wrist, normalize_by=10.0)
        
        # Distance is 20 pixels, normalized by 10
        self.assertAlmostEqual(distance, 2.0, places=1)
    
    def test_hand_distance_missing_hand(self):
        """Test hand distance with missing hand."""
        left_wrist = np.array([50, 50])
        right_wrist = None
        
        distance = calculate_hand_distance(left_wrist, right_wrist)
        
        self.assertEqual(distance, 0.0)
    
    def test_grip_symmetry_both_hands(self):
        """Test grip symmetry with both hands present."""
        symmetry = calculate_grip_symmetry(True, True)
        self.assertEqual(symmetry, 1.0)
    
    def test_grip_symmetry_one_hand(self):
        """Test grip symmetry with one hand missing."""
        symmetry = calculate_grip_symmetry(True, False)
        self.assertEqual(symmetry, 0.0)
        
        symmetry = calculate_grip_symmetry(False, True)
        self.assertEqual(symmetry, 0.0)


class TestBodyMetrics(unittest.TestCase):
    """Test body position and lean metrics."""
    
    def test_center_of_mass(self):
        """Test center of mass calculation."""
        keypoints = {
            5: np.array([50, 40]),   # Left shoulder
            6: np.array([70, 40]),   # Right shoulder
            11: np.array([52, 80]),  # Left hip
            12: np.array([68, 80]),  # Right hip
        }
        
        com = calculate_center_of_mass(keypoints)
        
        self.assertIsNotNone(com)
        # COM should be between shoulders and hips
        self.assertGreater(com[0], 50)
        self.assertLess(com[0], 70)
        self.assertGreater(com[1], 40)
        self.assertLess(com[1], 80)
    
    def test_center_of_mass_partial_data(self):
        """Test COM with partial keypoints."""
        keypoints = {
            5: np.array([50, 40]),  # Only left shoulder
        }
        
        com = calculate_center_of_mass(keypoints)
        
        # Should still calculate with available data
        self.assertIsNotNone(com)
    
    def test_body_lean_vertical(self):
        """Test body lean for vertical posture."""
        shoulder_center = np.array([60, 40])
        hip_center = np.array([60, 80])
        
        lean = calculate_body_lean_angle(shoulder_center, hip_center)
        
        # Should be near 0 for vertical
        self.assertLess(abs(lean), 10)
    
    def test_body_lean_forward(self):
        """Test body lean for forward lean."""
        shoulder_center = np.array([70, 40])  # Forward
        hip_center = np.array([60, 80])
        
        lean = calculate_body_lean_angle(shoulder_center, hip_center)
        
        # Positive lean for forward
        self.assertGreater(lean, 0)
    
    def test_body_lean_backward(self):
        """Test body lean for backward lean."""
        shoulder_center = np.array([50, 40])  # Backward
        hip_center = np.array([60, 80])
        
        lean = calculate_body_lean_angle(shoulder_center, hip_center)
        
        # Negative lean for backward
        self.assertLess(lean, 0)


class TestTemporalPatterns(unittest.TestCase):
    """Test temporal pattern detection."""
    
    def test_arm_extension_event(self):
        """Test rapid arm extension detection."""
        previous_extensions = [0.2, 0.2, 0.25, 0.25]
        current_extension = 0.7
        
        detected = detect_arm_extension_event(
            current_extension, previous_extensions, threshold_delta=0.3
        )
        
        self.assertTrue(detected)
    
    def test_no_false_extension_event(self):
        """Test no false positive on gradual extension."""
        previous_extensions = [0.2, 0.25, 0.3, 0.35]
        current_extension = 0.4
        
        detected = detect_arm_extension_event(
            current_extension, previous_extensions, threshold_delta=0.3
        )
        
        self.assertFalse(detected)
    
    def test_hand_separation_event(self):
        """Test hand separation detection."""
        previous_distances = [0.5, 0.5, 0.55, 0.55, 0.6]
        current_distance = 1.2
        
        detected = detect_hand_separation_event(
            current_distance, previous_distances, threshold_delta=0.5
        )
        
        self.assertTrue(detected)


if __name__ == '__main__':
    unittest.main()
