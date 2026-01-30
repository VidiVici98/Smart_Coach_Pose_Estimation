"""
Tests for Firearm Detection Module

Run with: pytest tests/test_firearm_detector.py -v
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
from smart_coach.models.firearm_detector import (
    FirearmDetector,
    FirearmDetection,
    fuse_firearm_and_arm_estimates,
    check_muzzle_body_intersection,
    draw_firearm_detection
)


class TestFirearmDetection:
    """Test FirearmDetection dataclass."""
    
    def test_firearm_detection_creation(self):
        """Test creating a FirearmDetection object."""
        bbox = np.array([100, 100, 200, 150])
        muzzle = np.array([200, 125])
        grip = np.array([100, 125])
        
        detection = FirearmDetection(
            bbox=bbox,
            confidence=0.85,
            class_name='handgun',
            muzzle_point=muzzle,
            grip_point=grip,
            orientation_angle=0.0
        )
        
        assert detection.confidence == 0.85
        assert detection.class_name == 'handgun'
        assert np.array_equal(detection.muzzle_point, muzzle)
        assert detection.orientation_angle == 0.0


class TestFirearmDetector:
    """Test FirearmDetector class."""
    
    def create_mock_model(self, has_detection=True, confidence=0.8):
        """Create a mock YOLO model."""
        model = Mock()
        
        if has_detection:
            # Mock detection result
            box = Mock()
            box.conf = [confidence]
            box.cls = [0]
            box.xyxy = [np.array([100, 100, 200, 150])]
            
            result = Mock()
            result.boxes = [box]
            result.names = {0: 'gun'}
            
            model.return_value = [result]
        else:
            # No detection
            result = Mock()
            result.boxes = []
            model.return_value = [result]
        
        return model
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        model = self.create_mock_model()
        
        detector = FirearmDetector(
            model=model,
            confidence_threshold=0.5,
            target_classes=['gun', 'handgun']
        )
        
        assert detector.confidence_threshold == 0.5
        assert 'gun' in detector.target_classes
        assert detector.prev_bbox is None
    
    def test_detect_with_valid_detection(self):
        """Test detection with valid firearm present."""
        model = self.create_mock_model(has_detection=True, confidence=0.8)
        detector = FirearmDetector(model, confidence_threshold=0.5)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detection = detector.detect(frame)
        
        assert detection is not None
        assert detection.confidence == 0.8
        assert detection.class_name == 'gun'
        assert detection.bbox is not None
    
    def test_detect_with_no_detection(self):
        """Test detection when no firearm present."""
        model = self.create_mock_model(has_detection=False)
        detector = FirearmDetector(model, confidence_threshold=0.5)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detection = detector.detect(frame)
        
        assert detection is None
    
    def test_detect_below_threshold(self):
        """Test detection below confidence threshold."""
        model = self.create_mock_model(has_detection=True, confidence=0.3)
        detector = FirearmDetector(model, confidence_threshold=0.5)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detection = detector.detect(frame)
        
        assert detection is None  # Below threshold
    
    def test_temporal_smoothing(self):
        """Test that temporal smoothing is applied."""
        model = self.create_mock_model(has_detection=True)
        detector = FirearmDetector(model, smoothing_alpha=0.5)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # First detection
        detection1 = detector.detect(frame)
        bbox1 = detection1.bbox.copy()
        
        # Second detection (should be smoothed with first)
        detection2 = detector.detect(frame)
        
        # With smoothing_alpha=0.5, bbox2 should be average of two detections
        assert detector.prev_bbox is not None
    
    def test_get_muzzle_direction_vector(self):
        """Test getting muzzle direction vector."""
        model = Mock()
        detector = FirearmDetector(model)
        
        detection = FirearmDetection(
            bbox=np.array([100, 100, 200, 150]),
            confidence=0.8,
            class_name='gun',
            muzzle_point=np.array([200, 125]),
            grip_point=np.array([100, 125]),
            orientation_angle=0.0
        )
        
        direction = detector.get_muzzle_direction_vector(detection, normalize=True)
        
        assert direction is not None
        assert len(direction) == 2
        # Should be pointing right (normalized)
        assert abs(direction[0] - 1.0) < 0.01
        assert abs(direction[1]) < 0.01
    
    def test_calculate_muzzle_elevation(self):
        """Test muzzle elevation calculation."""
        model = Mock()
        detector = FirearmDetector(model)
        
        # Horizontal firearm (0 degrees)
        detection = FirearmDetection(
            bbox=np.array([100, 100, 200, 150]),
            confidence=0.8,
            class_name='gun',
            muzzle_point=np.array([200, 125]),
            grip_point=np.array([100, 125]),
            orientation_angle=0.0
        )
        
        elevation = detector.calculate_muzzle_elevation(detection)
        assert abs(elevation) < 1.0  # Should be close to 0
    
    def test_is_detection_stable(self):
        """Test detection stability check."""
        model = self.create_mock_model(has_detection=True)
        detector = FirearmDetector(model)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Not stable initially
        assert not detector.is_detection_stable(min_consecutive=3)
        
        # Add detections
        for _ in range(3):
            detector.detect(frame)
        
        # Should be stable now
        assert detector.is_detection_stable(min_consecutive=3)
    
    def test_reset(self):
        """Test detector reset."""
        model = self.create_mock_model(has_detection=True)
        detector = FirearmDetector(model)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detector.detect(frame)
        
        assert detector.prev_bbox is not None
        assert len(detector.detection_buffer) > 0
        
        detector.reset()
        
        assert detector.prev_bbox is None
        assert len(detector.detection_buffer) == 0


class TestFusionLogic:
    """Test fusion of firearm and arm estimates."""
    
    def test_fuse_high_confidence_firearm(self):
        """Test fusion with high confidence firearm detection."""
        firearm_dir = np.array([1.0, 0.0])
        arm_dir = np.array([0.8, 0.6])
        
        result, source = fuse_firearm_and_arm_estimates(
            firearm_dir,
            arm_dir,
            firearm_confidence=0.8,
            confidence_threshold=0.6
        )
        
        assert source == 'firearm'
        assert np.array_equal(result, firearm_dir)
    
    def test_fuse_moderate_confidence_blended(self):
        """Test fusion with moderate confidence (blend)."""
        firearm_dir = np.array([1.0, 0.0])
        arm_dir = np.array([0.8, 0.6])
        
        result, source = fuse_firearm_and_arm_estimates(
            firearm_dir,
            arm_dir,
            firearm_confidence=0.5,
            confidence_threshold=0.6,
            blend_weight=0.7
        )
        
        assert source == 'blended'
        assert result is not None
        # Result should be between firearm and arm
    
    def test_fuse_low_confidence_arms(self):
        """Test fusion with low confidence (use arms)."""
        firearm_dir = np.array([1.0, 0.0])
        arm_dir = np.array([0.8, 0.6])
        
        result, source = fuse_firearm_and_arm_estimates(
            firearm_dir,
            arm_dir,
            firearm_confidence=0.2,
            confidence_threshold=0.6
        )
        
        assert source == 'arms'
        assert np.array_equal(result, arm_dir)
    
    def test_fuse_no_firearm(self):
        """Test fusion with no firearm detection."""
        arm_dir = np.array([0.8, 0.6])
        
        result, source = fuse_firearm_and_arm_estimates(
            None,
            arm_dir,
            firearm_confidence=0.0
        )
        
        assert source == 'arms'
        assert np.array_equal(result, arm_dir)
    
    def test_fuse_no_arms(self):
        """Test fusion with no arm estimate."""
        firearm_dir = np.array([1.0, 0.0])
        
        result, source = fuse_firearm_and_arm_estimates(
            firearm_dir,
            None,
            firearm_confidence=0.8
        )
        
        assert source == 'firearm'
        assert np.array_equal(result, firearm_dir)
    
    def test_fuse_no_estimates(self):
        """Test fusion with no estimates available."""
        result, source = fuse_firearm_and_arm_estimates(
            None,
            None,
            firearm_confidence=0.0
        )
        
        assert source == 'none'
        assert result is None


class TestSafetyChecking:
    """Test muzzle-body intersection detection."""
    
    def test_muzzle_intersects_body(self):
        """Test detection of muzzle pointing at body."""
        # Create body mask (person in center)
        body_mask = np.zeros((480, 640), dtype=np.uint8)
        body_mask[200:280, 250:350] = 1
        
        # Muzzle pointing at body
        muzzle_point = np.array([200, 240])
        muzzle_direction = np.array([1.0, 0.0])  # Pointing right into body
        
        intersects, distance = check_muzzle_body_intersection(
            muzzle_point,
            muzzle_direction,
            body_mask,
            ray_length=200
        )
        
        assert intersects is True
        assert distance > 0
    
    def test_muzzle_misses_body(self):
        """Test muzzle not pointing at body."""
        # Create body mask (person in center)
        body_mask = np.zeros((480, 640), dtype=np.uint8)
        body_mask[200:280, 250:350] = 1
        
        # Muzzle pointing away from body
        muzzle_point = np.array([200, 100])
        muzzle_direction = np.array([0.0, -1.0])  # Pointing up, away from body
        
        intersects, distance = check_muzzle_body_intersection(
            muzzle_point,
            muzzle_direction,
            body_mask,
            ray_length=200
        )
        
        assert intersects is False
    
    def test_muzzle_body_intersection_no_mask(self):
        """Test with no body mask."""
        muzzle_point = np.array([200, 240])
        muzzle_direction = np.array([1.0, 0.0])
        
        intersects, distance = check_muzzle_body_intersection(
            muzzle_point,
            muzzle_direction,
            None,
            ray_length=200
        )
        
        assert intersects is False
        assert distance == 0.0


class TestVisualization:
    """Test visualization functions."""
    
    def test_draw_firearm_detection(self):
        """Test drawing firearm detection overlay."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        detection = FirearmDetection(
            bbox=np.array([100, 100, 200, 150]),
            confidence=0.85,
            class_name='handgun',
            muzzle_point=np.array([200, 125]),
            grip_point=np.array([100, 125]),
            orientation_angle=0.0
        )
        
        result = draw_firearm_detection(frame, detection)
        
        assert result.shape == frame.shape
        # Result should be modified (not all zeros)
        assert not np.array_equal(result, frame)
    
    def test_draw_no_detection(self):
        """Test drawing with no detection."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = draw_firearm_detection(frame, None)
        
        # Should return copy of original frame
        assert np.array_equal(result, frame)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
