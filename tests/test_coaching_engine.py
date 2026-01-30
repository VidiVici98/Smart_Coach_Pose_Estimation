"""
Tests for Coaching Engine

Run with: pytest tests/test_coaching_engine.py -v
"""

import pytest
import pandas as pd
import numpy as np
from smart_coach.analysis.coaching_engine import (
    CoachingEngine, CoachingRule, Severity, MetricComparison
)


def test_coaching_rule_evaluation():
    """Test basic rule evaluation logic."""
    # Create sample data
    df = pd.DataFrame({
        'stance_width': [0.5, 0.6, 0.7, 1.0, 1.2, 0.5, 0.5],  # Three frames too narrow
        'frame': range(7)
    })
    
    # Create rule for narrow stance
    rule = CoachingRule(
        name="test_narrow_stance",
        title="Test Narrow Stance",
        description="Test description",
        metric="stance_width",
        threshold=0.8,
        comparison=MetricComparison.LESS,
        severity=Severity.MEDIUM,
        min_frames=3,
        frame_percentage=0.30  # 30% of frames
    )
    
    result = rule.evaluate(df)
    
    # Should trigger (3 frames below 0.8 = 42% > 30%)
    assert result is not None
    assert result['num_frames'] == 3
    assert result['percentage'] > 30


def test_coaching_rule_no_trigger():
    """Test that rule doesn't trigger with insufficient violations."""
    df = pd.DataFrame({
        'stance_width': [1.0, 1.0, 1.0, 0.5, 1.0, 1.0],  # Only 1 frame narrow
        'frame': range(6)
    })
    
    rule = CoachingRule(
        name="test_narrow_stance",
        title="Test",
        description="Test",
        metric="stance_width",
        threshold=0.8,
        comparison=MetricComparison.LESS,
        severity=Severity.MEDIUM,
        min_frames=2,
        frame_percentage=0.30
    )
    
    result = rule.evaluate(df)
    
    # Should not trigger (only 1 frame < 2 min_frames)
    assert result is None


def test_absolute_comparison():
    """Test absolute value comparison."""
    df = pd.DataFrame({
        'body_lean_angle': [-20, -18, 15, -5, 2, 18, -16],  # Three exceed ±15
    })
    
    rule = CoachingRule(
        name="test_lean",
        title="Test Lean",
        description="Test",
        metric="body_lean_angle",
        threshold=15.0,
        comparison=MetricComparison.ABS_GREATER,
        severity=Severity.HIGH,
        min_frames=2,
        frame_percentage=0.01
    )
    
    result = rule.evaluate(df)
    
    assert result is not None
    assert result['num_frames'] == 4  # -20, -18, 18, -16


def test_derived_metrics():
    """Test that engine calculates derived metrics."""
    df = pd.DataFrame({
        'L_arm_extension': [0.9, 0.8, 0.7],
        'R_arm_extension': [0.85, 0.9, 0.6],
        'center_of_mass_x': [100, 102, 105],
        'center_of_mass_y': [200, 201, 203]
    })
    
    engine = CoachingEngine()
    df_enhanced = engine.add_derived_metrics(df)
    
    # Check derived metrics exist
    assert 'arm_extension_diff' in df_enhanced.columns
    assert 'com_velocity' in df_enhanced.columns
    
    # Check calculations
    assert df_enhanced['arm_extension_diff'].iloc[0] == pytest.approx(0.05, abs=0.01)


def test_report_generation_text():
    """Test text report generation."""
    df = pd.DataFrame({
        'stance_width': [0.5] * 50,  # All frames too narrow
        'L_arm_extension': [1.0] * 50,
        'R_arm_extension': [1.0] * 50,
        'head_pitch': [5.0] * 50,
        'body_lean_angle': [8.0] * 50,
        'L_elbow_angle': [160.0] * 50,
    })
    
    engine = CoachingEngine()
    report = engine.generate_report(df, output_format="text")
    
    # Check report contains key sections
    assert "COACHING INSIGHTS REPORT" in report
    assert "frames analyzed" in report.lower()
    assert "issues" in report.lower() or "no significant issues" in report.lower()


def test_report_generation_html():
    """Test HTML report generation."""
    df = pd.DataFrame({
        'stance_width': [0.5] * 30,
        'L_arm_extension': [1.0] * 30,
        'R_arm_extension': [1.0] * 30,
    })
    
    engine = CoachingEngine()
    report = engine.generate_report(df, output_format="html")
    
    # Check HTML structure
    assert "<!DOCTYPE html>" in report
    assert "<html>" in report
    assert "Smart Coach" in report


def test_severity_ordering():
    """Test that violations are sorted by severity."""
    # Create data that triggers multiple rules
    df = pd.DataFrame({
        'stance_width': [0.5] * 50,  # MEDIUM severity
        'L_arm_extension': [0.5] * 50,  # HIGH severity (incomplete extension)
        'R_arm_extension': [0.5] * 50,
        'head_pitch': [5.0] * 50,
        'body_lean_angle': [8.0] * 50,
        'L_elbow_angle': [160.0] * 50,
    })
    
    engine = CoachingEngine()
    violations = engine.evaluate_all_rules(df)
    
    # Should have at least 2 violations
    assert len(violations) >= 2
    
    # First violation should be HIGH severity (incomplete arm extension)
    assert violations[0]['severity'] == Severity.HIGH


def test_missing_metric():
    """Test graceful handling of missing metrics."""
    df = pd.DataFrame({
        'some_other_metric': [1.0] * 10
    })
    
    rule = CoachingRule(
        name="test",
        title="Test",
        description="Test",
        metric="nonexistent_metric",
        threshold=0.5,
        comparison=MetricComparison.LESS,
        severity=Severity.LOW,
        min_frames=1,
        frame_percentage=0.01
    )
    
    result = rule.evaluate(df)
    
    # Should return None for missing metric
    assert result is None


def test_empty_dataframe():
    """Test handling of empty dataframe."""
    df = pd.DataFrame()
    
    engine = CoachingEngine()
    violations = engine.evaluate_all_rules(df)
    
    # Should return empty list, not crash
    assert violations == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
