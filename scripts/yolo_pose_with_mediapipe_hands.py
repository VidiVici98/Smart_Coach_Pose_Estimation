import os
import sys
import time

# -------------------------
# Suppress PyTorch NNPACK warnings completely
# -------------------------
os.environ["PYTORCH_NO_NNPACK"] = "1"
os.environ["TORCH_CPP_LOG_LEVEL"] = "ERROR"  # suppress backend warnings

class SuppressStdErr:
    """Context manager to suppress stderr (for backend warnings like NNPACK)."""
    def __enter__(self):
        self._old_stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._old_stderr

# -------------------------
# IMPORTS
# -------------------------
with SuppressStdErr():
    import cv2
    import torch
    import numpy as np
    import csv
    from ultralytics import YOLO
    from torchvision.models.detection import maskrcnn_resnet50_fpn
    from torchvision.transforms import functional as F
    import mediapipe as mp

# -------------------------
# CONFIG
# -------------------------
VIDEO_PATH  = "input/test_video.mp4"
OUTPUT_PATH = "output/output_full.mp4"
CSV_PATH    = "output/analytics.csv"

POSE_MODEL_PATH = "models/yolov8m-pose.pt"
FACE_MODEL_PATH = "models/yolov8n-face.pt"
HAND_MODEL_PATH = "models/hand_landmarker.task"

# Adjusted TEMP_ALPHA for faster responsiveness
TEMP_ALPHA = 0.6
# Increased CONF_THRES to reduce false positives
CONF_THRES = 0.2

ALPHA_BODY = 0.35
ALPHA_CONE = 0.25
GAZE_LENGTH = 2000
GAZE_CONE_H_ANGLE = np.radians(16.0)  # Horizontal half-angle
GAZE_CONE_V_ANGLE = np.radians(9.0)   # Vertical half-angle
CONE_ORIGIN_OFFSET = 40  # Distance behind eyes to place cone origin (in pixels)
MAX_GAZE_ROT = 0.12  # rad/frame
GAZE_BUFFER_LEN = 9   # Increased for stronger median filtering
TORSO_BLEND = 0.25    # Reduced: more head-based for precision, less torso
GAZE_LERP_ALPHA = 0.15 # 85% old, 15% new - balanced smoothing
GAZE_2D_OUTLIER_THRESHOLD = 0.15  # Reject 2D gaze vectors that deviate too much
TORSO_LERP_ALPHA = 0.3  # Increased smoothing (lower = more filtering) to reduce arm artifacts
TORSO_CONSISTENCY_THRESHOLD = 0.5  # Min dot product with head direction for torso update

# -------------------------
# SKELETON
# -------------------------
SKELETON_EDGES = [
    (0,1),(0,2),(1,3),(2,4),
    (0,5),(0,6),(5,7),(7,9),
    (6,8),(8,10),
    (5,6),(5,11),(6,12),
    (11,12),(11,13),(13,15),
    (12,14),(14,16)
]

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20)
]

# -------------------------
# UTILS
# -------------------------
def norm(v): return np.linalg.norm(v)+1e-6
def unit(v): return v/norm(v)
def lerp(a,b,t): return a*(1-t)+b*t

def draw_mask_overlay(frame, mask):
    overlay = frame.copy()
    overlay[mask>0] = (50,150,255)
    cv2.addWeighted(overlay, ALPHA_BODY, frame, 1-ALPHA_BODY, 0, frame)

def draw_cone(frame, origin, direction, length, h_angle, v_angle, color, mask=None):
    """Draw 2D cone showing overall gaze direction with smooth confidence gradient.
    Uses 3 invisible shells for gradient calculation, but only renders the outermost shell visibly."""
    o = origin.astype(np.float32)
    d = unit(direction)
    
    # Rotation matrix helper
    def rotate_vec(vec, angle):
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        return np.array([cos_a * vec[0] - sin_a * vec[1],
                        sin_a * vec[0] + cos_a * vec[1]])
    
    num_shells = 3  # 3 shells: inner shells invisible, only outermost rendered
    edge_alpha = 0.15
    center_alpha = 0.4
    
    # Draw from outermost to innermost for proper layering
    for shell_idx in range(num_shells - 1, -1, -1):
        # Fraction from 0 (edge) to 1 (center), linear
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
        
        # Only render the outermost shell (shell_idx == num_shells - 1)
        if shell_idx == num_shells - 1:
            overlay = frame.copy()
            cv2.fillConvexPoly(overlay, pts, color)
            
            # Apply body mask clipping if provided
            if mask is not None:
                shell_mask = np.zeros_like(mask, dtype=np.uint8)
                cv2.fillConvexPoly(shell_mask, pts, 1)
                shell_mask = shell_mask & (~mask)
                overlay = np.where(shell_mask[..., None], overlay, frame)
            
            # Blend the outermost shell with the calculated alpha
            cv2.addWeighted(overlay, shell_alpha, frame, 1 - shell_alpha, 0, frame)

def draw_skeleton(frame, keypoints, edges, color=(0,255,255), radius=3, thickness=2):
    for a,b in edges:
        if a in keypoints and b in keypoints:
            cv2.line(frame, tuple(keypoints[a].astype(int)),
                             tuple(keypoints[b].astype(int)),
                             color, thickness)
    for i,p in keypoints.items():
        cv2.circle(frame, tuple(p.astype(int)), radius, color, -1)

def clamp_rotation(prev_vec, curr_vec, max_angle):
    prev_vec = unit(prev_vec)
    curr_vec = unit(curr_vec)
    dot = np.clip(np.dot(prev_vec, curr_vec), -1.0, 1.0)
    angle = np.arccos(dot)
    if angle <= max_angle:
        return curr_vec
    axis = np.cross(prev_vec, curr_vec)
    if norm(axis) < 1e-6:
        return prev_vec
    axis = unit(axis)
    K = np.array([[0,-axis[2],axis[1]],
                  [axis[2],0,-axis[0]],
                  [-axis[1],axis[0],0]])
    R = np.eye(3) + np.sin(max_angle)*K + (1-np.cos(max_angle))*(K@K)
    return R @ prev_vec

# -------------------------
# LOAD MODELS
# -------------------------
with SuppressStdErr():
    pose_model = YOLO(POSE_MODEL_PATH)
    face_model = YOLO(FACE_MODEL_PATH)
    maskrcnn = maskrcnn_resnet50_fpn(weights="DEFAULT")
    maskrcnn.eval()

    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    BaseOptions = python.BaseOptions
    RunningMode = vision.RunningMode
    HandLandmarker = vision.HandLandmarker
    HandLandmarkerOptions = vision.HandLandmarkerOptions

    hands_detector = HandLandmarker.create_from_options(
        HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=HAND_MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            num_hands=2
        )
    )

mp_face = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    refine_landmarks=True,
    max_num_faces=1
)

# -------------------------
# VIDEO SETUP
# -------------------------
cap = cv2.VideoCapture(VIDEO_PATH)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = float(cap.get(cv2.CAP_PROP_FPS))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
writer = cv2.VideoWriter(OUTPUT_PATH, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w,h))

# -------------------------
# CSV SETUP
# -------------------------
csv_fields = ["frame","shoulder_width"]
for i in range(17):
    csv_fields += [f"kps_{i}_x",f"kps_{i}_y",f"kps_{i}_vx",f"kps_{i}_vy"]
for side in ["L","R"]:
    for i in range(21):
        csv_fields += [f"{side}_hand_{i}_x",f"{side}_hand_{i}_y",
                       f"{side}_hand_{i}_vx",f"{side}_hand_{i}_vy"]
    csv_fields += [f"{side}_trigger_pull"]
csv_fields += ["gaze_dir_x","gaze_dir_y","gaze_on_body"]

csvfile = open(CSV_PATH,"w",newline="")
csvwriter = csv.DictWriter(csvfile,fieldnames=csv_fields)
csvwriter.writeheader()

# -------------------------
# STATE
# -------------------------
prev_pose = {}
prev_hand = {}
prev_index_y = {"L":None,"R":None}
prev_forward_3d = None
prev_torso_forward_3d = None  # For smoothing torso vector to reduce arm artifacts
forward_buffer = []
prev_gaze_vec_2d = None  # For 2D outlier rejection
prev_arm_spread = {"L": None, "R": None}  # Track wrist-to-shoulder distance per side
frame_idx = 0
start_time = time.time()

# -------------------------
# FACE MODEL 3D POINTS
# -------------------------
FACE_3D_POINTS = np.array([
    [0.0, 0.0, 0.0],
    [0.0, -63.6, -12.5],
    [-43.3, 32.7, -26.0],
    [43.3, 32.7, -26.0],
    [-28.9, -28.9, -24.1],
    [28.9, -28.9, -24.1]
])

# -------------------------
# MAIN LOOP
# -------------------------
with SuppressStdErr():  # suppress any backend warnings during loop
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        row = {"frame":frame_idx}
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # -------- POSE --------
        pts = {}
        result = pose_model(frame, conf=CONF_THRES, max_det=1)[0]
        if result.keypoints is not None:
            kps = result.keypoints.data[0].cpu().numpy()
            for i,(x,y,c) in enumerate(kps):
                if c < CONF_THRES and i in prev_pose:
                    pts[i] = prev_pose[i]
                    continue
                p = np.array([x,y])
                if i in prev_pose:
                    p = lerp(prev_pose[i], p, TEMP_ALPHA)
                else:
                    p = np.array([x, y])  # Fallback for missing detection
                pts[i] = p
                prev_pose[i] = p
            draw_skeleton(frame, pts, SKELETON_EDGES)

        shoulder_width = norm(pts[5]-pts[6]) if 5 in pts and 6 in pts else 1.0
        row["shoulder_width"] = shoulder_width

        # -------- ARM SPREAD MONITORING (for arm-aware torso correction) --------
        # Track if arms are compressing inward, which would corrupt shoulder-based torso
        arm_spread_changing = False
        for side, wrist_idx, shoulder_idx in [("L", 15, 5), ("R", 16, 6)]:
            if wrist_idx in pts and shoulder_idx in pts:
                arm_spread = norm(pts[wrist_idx] - pts[shoulder_idx])
                if prev_arm_spread[side] is not None:
                    spread_delta = arm_spread - prev_arm_spread[side]
                    # If arms compressing inward (spread decreasing), flag it - lower threshold for faster detection
                    if spread_delta < -0.015 * shoulder_width:  # More sensitive compression detection
                        arm_spread_changing = True
                prev_arm_spread[side] = arm_spread

        # -------- BODY MASK --------
        body_mask = None
        with torch.no_grad():
            pred = maskrcnn([F.to_tensor(frame)])[0]
        for m,l,s in zip(pred["masks"],pred["labels"],pred["scores"]):
            if l==1 and s>0.7:
                body_mask = (m[0]>0.5).numpy()
                draw_mask_overlay(frame, body_mask)
                break

        # -------- HANDS --------
        hand_res = hands_detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        if hand_res.hand_landmarks:
            for side,hand in zip(["L","R"], hand_res.hand_landmarks):
                pts_hand=[]
                index_y=None
                for i,lm in enumerate(hand):
                    px = int(np.clip(lm.x*w, 0, w-1))
                    py = int(np.clip(lm.y*h, 0, h-1))
                    p = np.array([px, py], dtype=np.float32)

                    if (side, i) in prev_hand:
                        p = lerp(prev_hand[(side, i)], p, TEMP_ALPHA)
                    else:
                        p = np.array([px, py], dtype=np.float32)  # Fallback for missing detection
                    prev_hand[(side, i)] = p
                    ip=(int(p[0]),int(p[1]))
                    pts_hand.append(ip)
                    cv2.circle(frame,ip,3,(255,0,0),-1)
                    if i==8: index_y=p[1]

                for a,b in HAND_CONNECTIONS:
                    cv2.line(frame,pts_hand[a],pts_hand[b],(255,0,0),2)

                row[f"{side}_trigger_pull"] = int(
                    index_y is not None and
                    prev_index_y[side] is not None and
                    index_y < prev_index_y[side]
                )
                prev_index_y[side] = index_y

        # -------- FACE + HEAD-TORSO BLENDED GAZE (3D, body-relative) --------
        row["gaze_dir_x"] = row["gaze_dir_y"] = row["gaze_on_body"] = 0
        face_results = face_model(frame, conf=CONF_THRES, max_det=1)[0]

        if len(face_results.boxes.xyxy) > 0:
            x1, y1, x2, y2 = map(int, face_results.boxes.xyxy[0])
            face_crop = rgb[y1:y2, x1:x2]
            mp_results = mp_face.process(face_crop)

            if mp_results.multi_face_landmarks:
                lm = mp_results.multi_face_landmarks[0].landmark

                def L(i):
                    lm_i = lm[i]
                    # MediaPipe face mesh landmarks don't have reliable visibility when cropped
                    # Simply accept all landmarks - they come from MediaPipe which already filtered them
                    return np.array([lm_i.x * (x2 - x1) + x1,
                                     lm_i.y * (y2 - y1) + y1], dtype=np.float32)

                # Build points, filter Nones
                image_points, model_points_filtered = [], []
                for idx_model, idx_lm in enumerate([1, 152, 33, 263, 61, 291]):
                    p = L(idx_lm)
                    if p is not None:
                        image_points.append(p)
                        model_points_filtered.append(FACE_3D_POINTS[idx_model] * shoulder_width / 100.0)
                image_points = np.array(image_points, dtype=np.float32)
                model_points_filtered = np.array(model_points_filtered, dtype=np.float32)

                if len(image_points) >= 4:  # Need at least 4 points for solvePnP
                    camera_matrix = np.array([[w, 0, w / 2],
                                              [0, w, h / 2],
                                              [0, 0, 1]], dtype=np.float32)
                    dist_coeffs = np.zeros((4, 1))

                    success, rotation_vector, translation_vector = cv2.solvePnP(
                        model_points_filtered, image_points, camera_matrix, dist_coeffs,
                        flags=cv2.SOLVEPNP_ITERATIVE
                    )

                    if success:
                        rot_mat, _ = cv2.Rodrigues(rotation_vector)
                        head_forward = rot_mat[:, 2].copy()

                        # --- Clamp vertical component to reduce noise while preserving pitch ---
                        # Balanced: strict enough to prevent drift, loose enough to track real elevation
                        head_forward[2] = np.clip(head_forward[2], -0.055, 0.055)
                        head_forward = unit(head_forward)

                        # --- Compute torso forward vector ---
                        # Priority: hips (most stable) → shoulders (with arm-aware filtering) → head-only fallback
                        torso_forward_3d = None
                        using_shoulders = False
                        
                        # Try hips first (stable anchor when in frame)
                        if 11 in pts and 12 in pts and 1 in pts:
                            hip_mid = (pts[11] + pts[12]) / 2
                            nose_pt = pts[1]
                            torso_forward_2d = nose_pt - hip_mid
                            torso_forward_3d = np.array([torso_forward_2d[0], torso_forward_2d[1], 0.0])
                            torso_forward_3d = unit(torso_forward_3d)
                        # Fall back to shoulders if hips missing (but with strict consistency check to reject arm artifacts)
                        elif 5 in pts and 6 in pts and 1 in pts:
                            using_shoulders = True
                            shoulder_mid = (pts[5] + pts[6]) / 2
                            nose_pt = pts[1]
                            torso_forward_2d = nose_pt - shoulder_mid
                            torso_forward_3d = np.array([torso_forward_2d[0], torso_forward_2d[1], 0.0])
                            torso_forward_3d = unit(torso_forward_3d)
                        
                        fused_forward = head_forward.copy()
                        if torso_forward_3d is not None:
                            # Arm-aware consistency check: when arms compress, only accept torso if strongly aligned with head
                            threshold = TORSO_CONSISTENCY_THRESHOLD
                            if using_shoulders and arm_spread_changing:
                                threshold = 0.8  # Even stricter during arm compression (reject almost all shoulder updates)
                            
                            # Consistency check: only update torso if it aligns reasonably with head (full 3D comparison)
                            if np.dot(torso_forward_3d, head_forward) > threshold:
                                # Smooth torso vector strongly to reduce arm movement artifacts
                                # Even stronger smoothing during arm compression
                                smooth_alpha = TORSO_LERP_ALPHA
                                if using_shoulders and arm_spread_changing:
                                    smooth_alpha = 0.05  # Extremely aggressive smoothing during compression (95% previous, 5% new)
                                
                                if prev_torso_forward_3d is not None:
                                    torso_forward_3d = unit(lerp(prev_torso_forward_3d, torso_forward_3d, smooth_alpha))
                                prev_torso_forward_3d = torso_forward_3d
                            else:
                                # Torso inconsistent with head; stick with previous torso
                                if prev_torso_forward_3d is not None:
                                    torso_forward_3d = prev_torso_forward_3d
                                else:
                                    torso_forward_3d = head_forward[:3]
                            
                            # --- Blend: 75% head (precision), 25% torso (stability anchor) ---
                            fused_forward = unit((1 - TORSO_BLEND) * head_forward + TORSO_BLEND * torso_forward_3d)

                        # --- Stabilize via flipping check and buffer smoothing ---
                        if forward_buffer:
                            recent_avg = unit(np.mean(forward_buffer, axis=0))
                            if np.dot(fused_forward, recent_avg) < 0:
                                fused_forward *= -1

                        forward_buffer.append(fused_forward)
                        if len(forward_buffer) > GAZE_BUFFER_LEN:
                            forward_buffer.pop(0)

                        # Use median of buffer for robust smoothing
                        if len(forward_buffer) >= 7:
                            buffer_array = np.array(forward_buffer)
                            smoothed_forward = unit(np.median(buffer_array, axis=0))
                        elif len(forward_buffer) >= 5:
                            buffer_array = np.array(forward_buffer)
                            smoothed_forward = unit(np.median(buffer_array, axis=0))
                        else:
                            smoothed_forward = unit(np.mean(forward_buffer, axis=0)) if forward_buffer else fused_forward

                        # Apply balanced exponential smoothing for jitter reduction without lag
                        if prev_forward_3d is not None:
                            smoothed_forward = unit(lerp(prev_forward_3d, smoothed_forward, GAZE_LERP_ALPHA))
                        
                        prev_forward_3d = smoothed_forward

                        # --- Project to 2D for cone drawing and CSV ---
                        gaze_vec = unit(smoothed_forward[:2])
                        
                        # --- Apply 2D outlier rejection to catch remaining spikes ---
                        if prev_gaze_vec_2d is not None:
                            deviation = np.linalg.norm(gaze_vec - prev_gaze_vec_2d)
                            if deviation > GAZE_2D_OUTLIER_THRESHOLD:
                                # Outlier detected - use previous instead
                                gaze_vec = prev_gaze_vec_2d
                        
                        prev_gaze_vec_2d = gaze_vec.copy()
                        row["gaze_dir_x"] = float(gaze_vec[0])
                        row["gaze_dir_y"] = float(gaze_vec[1])

                        eye_left = L(33)
                        eye_right = L(263)
                        if eye_left is not None and eye_right is not None:
                            eye_mid = (eye_left + eye_right) / 2
                            # Position cone origin inside head (behind eyes) so cone edges intersect eyes
                            cone_origin = eye_mid - gaze_vec * CONE_ORIGIN_OFFSET
                            # Draw cone with radial confidence gradient (center=0.4 alpha, edges=0.15)
                            # Body mask clipping shows only external portion
                            draw_cone(frame, cone_origin, gaze_vec, GAZE_LENGTH + CONE_ORIGIN_OFFSET,
                                      GAZE_CONE_H_ANGLE, GAZE_CONE_V_ANGLE, (0, 255, 255), mask=body_mask)

                        # Draw key face landmarks
                        for idx in [1, 33, 263, 61, 291, 152]:
                            p = L(idx)
                            if p is not None:
                                cv2.circle(frame, tuple(p.astype(int)), 3, (0, 255, 255), -1)

                        # Check gaze hitting body
                        if body_mask is not None and eye_left is not None and eye_right is not None:
                            eye_mid = (eye_left + eye_right) / 2
                            for d in range(0, GAZE_LENGTH, 10):
                                p = (eye_mid + gaze_vec * d).astype(int)
                                if 0 <= p[0] < w and 0 <= p[1] < h and body_mask[p[1], p[0]]:
                                    row["gaze_on_body"] = 1
                                    break
        # -------- WRITE --------
        csvwriter.writerow(row)
        writer.write(frame)

        # -------- FRAME PROGRESS + ETA --------
        frame_idx+=1
        elapsed = time.time() - start_time
        fps_current = frame_idx / elapsed if elapsed>0 else 0
        remaining = frame_count - frame_idx
        eta_sec = remaining / fps_current if fps_current>0 else 0
        eta_str = f"{int(eta_sec//60):02d}:{int(eta_sec%60):02d}"
        print(f"Frame {frame_idx}/{frame_count} | FPS: {fps_current:.2f} | ETA: {eta_str}", end="\r")

# -------------------------
# CLEANUP
# -------------------------
cap.release()
writer.release()
hands_detector.close()
csvfile.close()
total_time = time.time() - start_time
print(f"\nFinished processing {frame_count} frames in {total_time:.2f} seconds ({frame_count/total_time:.2f} FPS).")
