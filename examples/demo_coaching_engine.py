#!/usr/bin/env python3
"""
Coaching Engine Demo - Demonstrates the coaching insights system
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from smart_coach.analysis.coaching_engine import CoachingEngine, Severity

def create_sample_data(scenario="beginner"):
    np.random.seed(42)
    num_frames = 120
    
    if scenario == "beginner":
        df = pd.DataFrame({
            'frame': range(num_frames),
            'timestamp': np.arange(num_frames) / 30.0,
            'stance_width': np.random.normal(0.6, 0.08, num_frames),
            'L_arm_extension': np.random.normal(0.65, 0.05, num_frames),
            'R_arm_extension': np.random.normal(0.63, 0.05, num_frames),
            'body_lean_angle': np.random.normal(18, 3, num_frames),
            'head_pitch': np.random.normal(0, 15, num_frames),
            'L_elbow_angle': np.random.normal(130, 8, num_frames),
            'R_elbow_angle': np.random.normal(135, 10, num_frames),
            'center_of_mass_x': 500 + np.cumsum(np.random.normal(0, 3, num_frames)),
            'center_of_mass_y': 400 + np.cumsum(np.random.normal(0, 2.5, num_frames)),
        })
    elif scenario == "expert":
        df = pd.DataFrame({
            'frame': range(num_frames),
            'timestamp': np.arange(num_frames) / 30.0,
            'stance_width': np.random.normal(1.15, 0.03, num_frames),
            'L_arm_extension': np.random.normal(0.97, 0.02, num_frames),
            'R_arm_extension': np.random.normal(0.96, 0.02, num_frames),
            'body_lean_angle': np.random.normal(6, 1.5, num_frames),
            'head_pitch': np.random.normal(0, 4, num_frames),
            'L_elbow_angle': np.random.normal(170, 3, num_frames),
            'R_elbow_angle': np.random.normal(168, 3, num_frames),
            'center_of_mass_x': 500 + np.cumsum(np.random.normal(0, 0.5, num_frames)),
            'center_of_mass_y': 400 + np.cumsum(np.random.normal(0, 0.4, num_frames)),
        })
    return df

print("="*80)
print("SMART COACH - COACHING ENGINE DEMO")
print("="*80)

for scenario_name in ["Beginner", "Expert"]:
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario_name.upper()}")
    print('='*80)
    
    df = create_sample_data(scenario_name.lower())
    engine = CoachingEngine()
    violations = engine.evaluate_all_rules(df)
    
    print(f"\n📊 Issues Detected: {len(violations)}")
    
    if len(violations) == 0:
        print("✅ Excellent form!")
    else:
        for i, v in enumerate(violations[:3], 1):
            icon = "🔴" if v['severity'] == Severity.HIGH else "🟡"
            print(f"\n{i}. {icon} {v['title']}")
            print(f"   Frequency: {v['percentage']:.1f}%")

print("\n" + "="*80)
print("Try: python scripts/tools/generate_coaching_report.py data/output/analytics.csv")
print("="*80)
