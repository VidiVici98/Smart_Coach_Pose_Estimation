"""
Integration tests for Smart Coach modules

Tests that all components work together correctly and handle edge cases robustly.

Run with: python tests/test_integration.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
from unittest.mock import Mock

# Import modules to test
from smart_coach.analysis.coaching_engine import (
    CoachingEngine, CoachingRule, Severity, MetricComparison
)
from smart_coach.models.firearm_detector import (
    FirearmDetector, FirearmDetection,
    fuse_firearm_and_arm_estimates,
    check_muzzle_body_intersection
)


def test_coaching_engine_end_to_end():
    """Test complete coaching engine workflow."""
    print("\n" + "="*80)
    print("TEST: Coaching Engine End-to-End")
    print("="*80)
    
    # Create realistic data
    np.random.seed(42)
    num_frames = 150
    
    df = pd.DataFrame({
        'frame': range(num_frames),
        'timestamp': np.arange(num_frames) / 30.0,
        
        # Mix of good and bad metrics
        'stance_width': np.concatenate([
            np.random.normal(0.6, 0.05, 75),  # Too narrow
            np.random.normal(1.2, 0.1, 75)    # Good
        ]),
        'L_arm_extension': np.random.normal(0.65, 0.05, num_frames),  # Incomplete
        'R_arm_extension': np.random.normal(0.63, 0.05, num_frames),
        'body_lean_angle': np.random.normal(8, 3, num_frames),
        'head_pitch': np.random.normal(0, 8, num_frames),
        'L_elbow_angle': np.random.normal(165, 10, num_frames),
        'center_of_mass_x': 500 + np.cumsum(np.random.normal(0, 1, num_frames)),
        'center_of_mass_y': 400 + np.cumsum(np.random.normal(0, 0.8, num_frames)),
    })
    
    # Add some NaN values to simulate real data
    df.loc[10:15, 'stance_width'] = np.nan
    df.loc[50:55, 'L_arm_extension'] = np.nan
    
    print(f"✓ Created test data: {len(df)} frames, {df.isnull().sum().sum()} NaN values")
    
    # Create engine and evaluate
    engine = CoachingEngine()
    violations = engine.evaluate_all_rules(df)
    
    print(f"✓ Evaluated rules: {len(violations)} violations found")
    
    # Generate reports in all formats
    for fmt in ['text', 'markdown', 'html']:
        try:
            report = engine.generate_report(df, output_format=fmt)
            print(f"✓ Generated {fmt} report: {len(report)} chars")
        except Exception as e:
            print(f"✗ Failed to generate {fmt} report: {e}")
            return False
    
    print("✅ Coaching engine end-to-end test PASSED")
    return True


def test_firearm_detector_integration():
    """Test firearm detector with mock YOLO model."""
    print("\n" + "="*80)
    print("TEST: Firearm Detector Integration")
    print("="*80)
    
    # Create mock model
    mock_model = Mock()
    
    # Mock detection result
    box = Mock()
    box.conf = [0.75]
    box.cls = [0]
    box.xyxy = [np.array([100, 100, 250, 200])]
    
    result = Mock()
    result.boxes = [box]
    result.names = {0: 'gun'}
    
    mock_model.return_value = [result]
    
    # Create detector
    detector = FirearmDetector(
        mock_model,
        confidence_threshold=0.4,
        smoothing_alpha=0.7
    )
    
    print(f"✓ Created detector with threshold={detector.confidence_threshold}")
    
    # Test detection on mock frames
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    detection = detector.detect(frame)
    assert detection is not None, "Detection should succeed"
    print(f"✓ Detection successful: confidence={detection.confidence:.2f}")
    
    # Test muzzle direction
    direction = detector.get_muzzle_direction_vector(detection)
    assert direction is not None, "Direction should be computed"
    print(f"✓ Muzzle direction computed: {direction}")
    
    # Test elevation
    elevation = detector.calculate_muzzle_elevation(detection)
    print(f"✓ Muzzle elevation: {elevation:.1f}°")
    
    # Test stability
    for _ in range(5):
        detector.detect(frame)
    
    is_stable = detector.is_detection_stable(min_consecutive=3)
    print(f"✓ Detection stability: {is_stable}")
    
    print("✅ Firearm detector integration test PASSED")
    return True


def test_fusion_pipeline():
    """Test fusion of firearm and arm estimates."""
    print("\n" + "="*80)
    print("TEST: Fusion Pipeline")
    print("="*80)
    
    # Test various fusion scenarios
    scenarios = [
        (np.array([1.0, 0.0]), np.array([0.8, 0.6]), 0.8, "firearm"),
        (np.array([1.0, 0.0]), np.array([0.8, 0.6]), 0.5, "blended"),
        (np.array([1.0, 0.0]), np.array([0.8, 0.6]), 0.2, "arms"),
        (None, np.array([0.8, 0.6]), 0.0, "arms"),
        (np.array([1.0, 0.0]), None, 0.8, "firearm"),
        (None, None, 0.0, "none"),
    ]
    
    for i, (firearm_dir, arm_dir, conf, expected_source) in enumerate(scenarios, 1):
        result, source = fuse_firearm_and_arm_estimates(
            firearm_dir, arm_dir, conf
        )
        
        assert source == expected_source, f"Scenario {i}: Expected {expected_source}, got {source}"
        print(f"✓ Scenario {i}: {source} (confidence={conf:.1f})")
    
    print("✅ Fusion pipeline test PASSED")
    return True


def test_safety_checking():
    """Test muzzle-body intersection detection."""
    print("\n" + "="*80)
    print("TEST: Safety Checking")
    print("="*80)
    
    # Create body mask (person in center)
    body_mask = np.zeros((480, 640), dtype=np.uint8)
    body_mask[200:300, 280:360] = 1
    
    # Test scenarios
    scenarios = [
        # (muzzle_point, direction, should_intersect, description)
        (np.array([200, 250]), np.array([1.0, 0.0]), True, "Pointing directly at body"),
        (np.array([200, 100]), np.array([0.0, -1.0]), False, "Pointing away from body"),
        (np.array([200, 250]), np.array([-1.0, 0.0]), False, "Pointing away from body"),
        (np.array([500, 250]), np.array([-1.0, 0.0]), True, "Pointing toward body from right"),
    ]
    
    for i, (point, direction, should_intersect, desc) in enumerate(scenarios, 1):
        intersects, distance = check_muzzle_body_intersection(
            point, direction, body_mask, ray_length=200
        )
        
        if should_intersect:
            assert intersects, f"Scenario {i} should intersect: {desc}"
        else:
            assert not intersects, f"Scenario {i} should not intersect: {desc}"
        
        print(f"✓ Scenario {i}: intersects={intersects}, distance={distance:.1f}px - {desc}")
    
    print("✅ Safety checking test PASSED")
    return True


def test_edge_cases():
    """Test handling of edge cases and invalid inputs."""
    print("\n" + "="*80)
    print("TEST: Edge Cases and Error Handling")
    print("="*80)
    
    # Test 1: Empty dataframe
    engine = CoachingEngine()
    df_empty = pd.DataFrame()
    violations = engine.evaluate_all_rules(df_empty)
    assert violations == [], "Empty dataframe should have no violations"
    print("✓ Empty dataframe handled")
    
    # Test 2: All-NaN dataframe
    df_nan = pd.DataFrame({
        'stance_width': [np.nan] * 10,
        'L_arm_extension': [np.nan] * 10,
    })
    violations = engine.evaluate_all_rules(df_nan)
    assert violations == [], "All-NaN dataframe should have no violations"
    print("✓ All-NaN dataframe handled")
    
    # Test 3: Invalid fusion inputs
    result, source = fuse_firearm_and_arm_estimates(None, None, 0.0)
    assert source == 'none', "No inputs should return 'none'"
    print("✓ Invalid fusion inputs handled")
    
    # Test 4: Invalid safety check inputs
    intersects, dist = check_muzzle_body_intersection(None, None, None)
    assert not intersects, "None inputs should not intersect"
    print("✓ Invalid safety check inputs handled")
    
    # Test 5: Extreme parameter values
    mock_model = Mock()
    detector = FirearmDetector(
        mock_model,
        confidence_threshold=5.0,  # > 1.0
        smoothing_alpha=-0.5,      # < 0.0
        buffer_size=1000            # Very large
    )
    assert 0.0 <= detector.confidence_threshold <= 1.0
    assert 0.0 <= detector.smoothing_alpha <= 1.0
    assert detector.buffer_size <= 100
    print("✓ Extreme parameters clamped")
    
    print("✅ Edge cases test PASSED")
    return True


def test_realistic_workflow():
    """Test a realistic workflow combining all components."""
    print("\n" + "="*80)
    print("TEST: Realistic Workflow")
    print("="*80)
    
    # Simulate processing a video
    num_frames = 100
    
    # Mock firearm detector
    mock_model = Mock()
    mock_model.return_value = [Mock(boxes=[])]
    detector = FirearmDetector(mock_model)
    
    # Simulate frame processing
    detections = []
    for i in range(num_frames):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detection = detector.detect(frame)
        detections.append(detection)
    
    print(f"✓ Processed {num_frames} frames")
    
    # Create analytics dataframe
    df = pd.DataFrame({
        'frame': range(num_frames),
        'stance_width': np.random.normal(1.0, 0.2, num_frames),
        'L_arm_extension': np.random.normal(0.85, 0.1, num_frames),
        'R_arm_extension': np.random.normal(0.83, 0.1, num_frames),
        'head_pitch': np.random.normal(0, 5, num_frames),
        'body_lean_angle': np.random.normal(7, 3, num_frames),
        'L_elbow_angle': np.random.normal(165, 8, num_frames),
        'center_of_mass_x': [100] * num_frames,
        'center_of_mass_y': [200] * num_frames,
    })
    
    # Generate coaching report
    engine = CoachingEngine()
    violations = engine.evaluate_all_rules(df)
    report = engine.generate_report(df, output_format='text')
    
    print(f"✓ Generated coaching report: {len(violations)} issues, {len(report)} chars")
    
    print("✅ Realistic workflow test PASSED")
    return True


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*80)
    print("SMART COACH - INTEGRATION TEST SUITE")
    print("="*80)
    
    tests = [
        ("Coaching Engine E2E", test_coaching_engine_end_to_end),
        ("Firearm Detector Integration", test_firearm_detector_integration),
        ("Fusion Pipeline", test_fusion_pipeline),
        ("Safety Checking", test_safety_checking),
        ("Edge Cases", test_edge_cases),
        ("Realistic Workflow", test_realistic_workflow),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
