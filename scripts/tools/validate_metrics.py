#!/usr/bin/env python3
"""
Validation script to verify that all expected metrics are present in the CSV output.
This script checks the CSV header against the expected fields documented in metrics_reference.md
"""

import csv
import sys

# Expected CSV fields based on the updated pipeline
EXPECTED_FIELDS = ["frame", "timestamp", "shoulder_width", "hip_width", "stance_width"]

# Add pose keypoint fields (17 keypoints × 5 fields each)
for i in range(17):
    EXPECTED_FIELDS += [f"kps_{i}_x", f"kps_{i}_y", f"kps_{i}_vx", f"kps_{i}_vy", f"kps_{i}_conf"]

# Add hand landmark fields (2 hands × 21 landmarks × 4 fields each)
for side in ["L", "R"]:
    for i in range(21):
        EXPECTED_FIELDS += [f"{side}_hand_{i}_x", f"{side}_hand_{i}_y",
                           f"{side}_hand_{i}_vx", f"{side}_hand_{i}_vy"]
    EXPECTED_FIELDS += [f"{side}_trigger_pull"]

# Add gaze metrics
EXPECTED_FIELDS += ["gaze_dir_x", "gaze_dir_y", "gaze_on_body"]

# Add joint angles
EXPECTED_FIELDS += ["L_elbow_angle", "R_elbow_angle", "L_shoulder_angle", "R_shoulder_angle",
                   "L_hip_angle", "R_hip_angle", "L_knee_angle", "R_knee_angle"]

# Add arm extension metrics
EXPECTED_FIELDS += ["L_arm_extension", "R_arm_extension"]

# Add grip metrics
EXPECTED_FIELDS += ["hand_distance", "grip_symmetry"]

# Add body position metrics
EXPECTED_FIELDS += ["center_of_mass_x", "center_of_mass_y", "body_lean_angle"]

# Add head orientation
EXPECTED_FIELDS += ["head_pitch", "head_yaw", "head_roll"]

# Add wrist and elbow elevation
EXPECTED_FIELDS += ["L_wrist_elevation", "R_wrist_elevation", "L_elbow_elevation", "R_elbow_elevation"]


def validate_csv(csv_path):
    """Validate that CSV contains all expected fields."""
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            actual_fields = reader.fieldnames
            
            if not actual_fields:
                print(f"❌ ERROR: CSV file {csv_path} is empty or has no header")
                return False
            
            # Check for missing fields
            missing = set(EXPECTED_FIELDS) - set(actual_fields)
            if missing:
                print(f"❌ ERROR: Missing {len(missing)} expected fields:")
                for field in sorted(missing):
                    print(f"   - {field}")
                return False
            
            # Check for unexpected fields
            unexpected = set(actual_fields) - set(EXPECTED_FIELDS)
            if unexpected:
                print(f"⚠️  WARNING: Found {len(unexpected)} unexpected fields:")
                for field in sorted(unexpected):
                    print(f"   - {field}")
            
            # Count rows
            row_count = sum(1 for _ in reader)
            
            print(f"✅ CSV validation passed!")
            print(f"   Total fields: {len(actual_fields)}")
            print(f"   Total rows: {row_count}")
            
            # Print field categories
            print("\n📊 Field Categories:")
            print(f"   - Basic metrics: 5 fields")
            print(f"   - Pose keypoints: {17 * 5} fields (17 points × 5 metrics)")
            print(f"   - Hand landmarks: {2 * 21 * 4 + 2} fields (2 hands × 21 points × 4 metrics + 2 trigger)")
            print(f"   - Gaze metrics: 3 fields")
            print(f"   - Joint angles: 8 fields")
            print(f"   - Arm metrics: 2 fields")
            print(f"   - Grip metrics: 2 fields")
            print(f"   - Body position: 3 fields")
            print(f"   - Head orientation: 3 fields")
            print(f"   - Elevation metrics: 4 fields")
            print(f"   TOTAL: {len(EXPECTED_FIELDS)} fields")
            
            return True
            
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {csv_path}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_metrics.py <path_to_analytics.csv>")
        print("\nThis script validates that the CSV output contains all expected metrics")
        print("for comprehensive defensive handgun shooter coaching analysis.")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    success = validate_csv(csv_path)
    sys.exit(0 if success else 1)
