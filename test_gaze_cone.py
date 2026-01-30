#!/usr/bin/env python3
"""
Simple test script to verify gaze cone drawing works correctly.
"""

import cv2
import numpy as np

# Copy the unit function from the pipeline
def unit(v):
    """Normalize vector to unit length."""
    norm = np.linalg.norm(v)
    return v / norm if norm > 1e-6 else v

# Copy the improved draw_cone function
def draw_cone(frame, origin, direction, length, h_angle, v_angle, color, mask=None):
    """Draw 2D cone showing overall gaze direction with smooth confidence gradient.
    Draws multiple shells with increasing transparency from center to edge for gradient effect."""
    try:
        o = origin.astype(np.float32)
        d = unit(direction)
        
        # Validate inputs
        if np.any(np.isnan(o)) or np.any(np.isnan(d)):
            print("DEBUG: Invalid origin or direction (NaN detected)")
            return
        if np.linalg.norm(d) < 0.01:  # Direction vector too small
            print("DEBUG: Direction vector too small")
            return
        
        # Rotation matrix helper
        def rotate_vec(vec, angle):
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            return np.array([cos_a * vec[0] - sin_a * vec[1],
                            sin_a * vec[0] + cos_a * vec[1]])
        
        # Increased visibility: more shells and higher alpha values
        num_shells = 5  # More shells for smoother gradient
        edge_alpha = 0.25  # Increased from 0.15 for better visibility
        center_alpha = 0.6  # Increased from 0.4 for better visibility
        
        # Draw from outermost to innermost for proper layering
        for shell_idx in range(num_shells - 1, -1, -1):
            # Fraction from 0 (edge) to 1 (center)
            frac = (shell_idx + 1) / num_shells
            
            # Linear alpha gradient: edge_alpha at frac=0, center_alpha at frac=1
            shell_alpha = edge_alpha + frac * (center_alpha - edge_alpha)
            
            # Current shell angle
            shell_angle = frac * h_angle
            
            # Compute cone edges at this angle
            left_vec = rotate_vec(d, shell_angle)
            right_vec = rotate_vec(d, -shell_angle)
            
            p_left = o + left_vec * length
            p_right = o + right_vec * length
            
            # Draw triangle for this shell
            pts = np.array([o, p_left, p_right], np.int32)
            
            # Render ALL shells, not just the outermost one
            overlay = frame.copy()
            cv2.fillConvexPoly(overlay, pts, color)
            
            # Apply body mask clipping if provided
            if mask is not None:
                shell_mask = np.zeros_like(mask, dtype=np.uint8)
                cv2.fillConvexPoly(shell_mask, pts, 1)
                # Invert mask: show cone where body is NOT present
                shell_mask = shell_mask & (~mask)
                overlay = np.where(shell_mask[..., None], overlay, frame)
            
            # Blend this shell with the calculated alpha
            cv2.addWeighted(overlay, shell_alpha, frame, 1 - shell_alpha, 0, frame)
            
        print(f"DEBUG: Drew gaze cone at origin {o.astype(int)} with direction {d}")
    except Exception as e:
        # Print error for debugging but don't crash the pipeline
        print(f"DEBUG: Error in draw_cone: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

# Create a test image
width, height = 1920, 1080
frame = np.zeros((height, width, 3), dtype=np.uint8)
frame[:] = (40, 40, 40)  # Dark gray background

# Draw a simple person shape
center_x, center_y = width // 2, height // 2

# Head
cv2.circle(frame, (center_x, center_y - 100), 60, (180, 150, 120), -1)

# Body
cv2.rectangle(frame, (center_x - 80, center_y - 40), (center_x + 80, center_y + 200), (100, 100, 150), -1)

# Eyes
cv2.circle(frame, (center_x - 25, center_y - 110), 8, (255, 255, 255), -1)
cv2.circle(frame, (center_x + 25, center_y - 110), 8, (255, 255, 255), -1)

# Test 1: Draw cone WITHOUT mask (should be fully visible)
print("Test 1: Drawing gaze cone WITHOUT body mask")
test1_frame = frame.copy()
eye_mid = np.array([center_x, center_y - 110], dtype=np.float32)
gaze_direction = np.array([0.8, 0.2], dtype=np.float32)  # Looking forward and slightly up
cone_origin = eye_mid - gaze_direction * 40  # Move origin behind eyes
draw_cone(test1_frame, cone_origin, gaze_direction, 2040, np.radians(16.0), np.radians(9.0), (0, 255, 255), mask=None)
cv2.imwrite('test_gaze_cone_no_mask.png', test1_frame)
print("  Saved: test_gaze_cone_no_mask.png")

# Test 2: Draw cone WITH body mask (should clip through body)
print("\nTest 2: Drawing gaze cone WITH body mask")
test2_frame = frame.copy()

# Create body mask (1 where body is present)
body_mask = np.zeros((height, width), dtype=np.uint8)
cv2.circle(body_mask, (center_x, center_y - 100), 60, 1, -1)  # Head
cv2.rectangle(body_mask, (center_x - 80, center_y - 40), (center_x + 80, center_y + 200), 1, -1)  # Body

draw_cone(test2_frame, cone_origin, gaze_direction, 2040, np.radians(16.0), np.radians(9.0), (0, 255, 255), mask=body_mask)
cv2.imwrite('test_gaze_cone_with_mask.png', test2_frame)
print("  Saved: test_gaze_cone_with_mask.png")

# Test 3: Different directions
print("\nTest 3: Multiple gaze directions")
test3_frame = frame.copy()

# Multiple directions
directions = [
    (np.array([0.9, 0.0]), "Forward"),
    (np.array([0.7, 0.5]), "Up-Right"),
    (np.array([0.7, -0.5]), "Down-Right"),
]

colors = [(0, 255, 255), (255, 0, 255), (255, 255, 0)]

for (direction, label), color in zip(directions, colors):
    cone_orig = eye_mid - unit(direction) * 40
    draw_cone(test3_frame, cone_orig, direction, 1500, np.radians(12.0), np.radians(7.0), color, mask=None)
    print(f"  Drew {label} cone in color {color}")

cv2.imwrite('test_gaze_cone_multiple.png', test3_frame)
print("  Saved: test_gaze_cone_multiple.png")

print("\n✓ All tests completed!")
print("\nCheck the generated PNG files to verify gaze cone visualization:")
print("  - test_gaze_cone_no_mask.png: Full cone (no clipping)")
print("  - test_gaze_cone_with_mask.png: Cone with body clipping")
print("  - test_gaze_cone_multiple.png: Multiple overlapping cones")
