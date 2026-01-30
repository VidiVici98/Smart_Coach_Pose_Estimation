import os
import sys
import time

# Print immediately to show script is starting
print("=" * 60, flush=True)
print("Smart Coach Pose Estimation Pipeline", flush=True)
print("=" * 60, flush=True)
print("Initializing...", flush=True)

# -------------------------
# Fix for libGL.so.1 missing in codespace
# -------------------------
# Create a fake libGL stub to prevent import errors
import ctypes.util
_orig_find_library = ctypes.util.find_library

def _fake_find_library(name):
    if name in ['GL', 'GLU']:
        return None  # Return None to skip loading
    return _orig_find_library(name)

ctypes.util.find_library = _fake_find_library

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
print("Importing libraries...", flush=True)
with SuppressStdErr():
    import cv2
    import torch
    import numpy as np
    import csv
    from ultralytics import YOLO
    from torchvision.models.detection import maskrcnn_resnet50_fpn
    from torchvision.transforms import functional as F
    import mediapipe as mp
print("✓ Import complete", flush=True)

# -------------------------
# CONFIG
# -------------------------
VIDEO_PATH  = "data/input/test_video.mp4"
OUTPUT_PATH = "data/output/output_full.mp4"
CSV_PATH    = "data/output/analytics.csv"

# Limit processing to first N frames for testing (set to None to process entire video)
# Or set SAMPLE_FRAMES to process only specific frames from different points
MAX_FRAMES = None  # Process entire video
# Broader sampling across full video duration to capture hands and diverse poses
# Frame 10: early action, 30: establishing, 60: mid-action, 75: peak, 
# 100: follow-through, 120: recovery, 140: end sequence
SAMPLE_FRAMES = [10, 30, 60, 75, 100, 120, 140]  # Broader video coverage for validation

POSE_MODEL_PATH = "data/models/yolov8m-pose.pt"
FACE_MODEL_PATH = "data/models/yolov8n-face.pt"
HAND_MODEL_PATH = "data/models/hand_landmarker.task"
FACE_LANDMARKER_PATH = "data/models/face_landmarker.task"  # For MediaPipe Tasks API

# Validate model files before loading
print("Validating model files...")
model_validation_failed = False
for model_name, model_path, expected_min_mb, expected_max_mb, is_optional in [
    ("YOLOv8 Pose", POSE_MODEL_PATH, 40, 60, False),
    ("YOLOv8 Face", FACE_MODEL_PATH, 5, 10, False),
    ("Hand Landmarker", HAND_MODEL_PATH, 0.2, 30, True),  # Accept lightweight (0.3MB) or full (26MB) versions
    ("Face Landmarker", FACE_LANDMARKER_PATH, 3.0, 30, True)  # Accept lightweight (3.6MB) or full (26MB) versions
]:
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        
        # Check if file size is in expected range
        if size_mb < expected_min_mb or size_mb > expected_max_mb:
            print(f"  ✗ {model_name}: INVALID SIZE ({size_mb:.1f} MB, expected {expected_min_mb}-{expected_max_mb} MB)")
            
            if is_optional:
                print(f"    ⚠ Optional model - pipeline will continue without this feature")
            else:
                print(f"    ERROR: Critical model file corrupted!")
                model_validation_failed = True
        else:
            # Note if using lightweight version
            if size_mb < 10 and "Landmarker" in model_name:
                print(f"  ✓ {model_name}: {size_mb:.1f} MB (lightweight version)")
            else:
                print(f"  ✓ {model_name}: {size_mb:.1f} MB")
    else:
        print(f"  ✗ {model_name}: NOT FOUND")
        if not is_optional:
            print(f"    ERROR: Required model missing!")
            model_validation_failed = True
        else:
            print(f"    ⚠ Optional model - pipeline will continue without this feature")

if model_validation_failed:
    print("\n✗ Critical model files missing or corrupted!")
    sys.exit(1)

print()

# -------------------------
# PERFORMANCE MODE
# -------------------------
# Auto-detect codespace environment and enable LOW_MEMORY_MODE
# Set to False to enable all features (requires 4-core/16GB codespace)
# Set to True for 2-core/8GB codespace (disables Mask R-CNN body segmentation)

# Check if running in codespace or low-memory environment
IS_CODESPACE = os.environ.get('CODESPACES') or os.environ.get('SMART_COACH_CODESPACE')

# Auto-enable LOW_MEMORY_MODE for codespace unless explicitly disabled
if IS_CODESPACE:
    LOW_MEMORY_MODE = os.environ.get('LOW_MEMORY_MODE', 'true').lower() != 'false'
    if LOW_MEMORY_MODE:
        print("🌐 Codespace detected - LOW_MEMORY_MODE enabled", flush=True)
        print("   (Set env LOW_MEMORY_MODE=false to enable all features)", flush=True)
else:
    # For local environments, default to False (all features enabled)
    LOW_MEMORY_MODE = os.environ.get('LOW_MEMORY_MODE', 'false').lower() == 'true'

print()

# Temporal smoothing - lower = more responsive, higher = more stable
TEMP_ALPHA = 0.3  # Pose smoothing (30% new, 70% old)
HAND_TEMP_ALPHA = 0.7  # Hand smoothing - INCREASED for less lag (70% new, 30% old)
# Increased CONF_THRES to reduce false positives
CONF_THRES = 0.2

ALPHA_BODY = 0.35
ALPHA_CONE = 0.25  # NOTE: Not used in current draw_cone implementation (uses internal alpha values)
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

def calculate_angle(p1, p2, p3):
    """Calculate angle at p2 formed by p1-p2-p3 in degrees."""
    if p1 is None or p2 is None or p3 is None:
        return None
    v1 = p1 - p2
    v2 = p3 - p2
    cos_angle = np.dot(v1, v2) / (norm(v1) * norm(v2))
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle_rad = np.arccos(cos_angle)
    return np.degrees(angle_rad)

def calculate_center_of_mass(pts):
    """Calculate approximate center of mass from available keypoints."""
    # Use core body points: shoulders, hips, knees if available
    core_points = []
    # Shoulders
    if 5 in pts: core_points.append(pts[5])
    if 6 in pts: core_points.append(pts[6])
    # Hips
    if 11 in pts: core_points.append(pts[11])
    if 12 in pts: core_points.append(pts[12])
    # Knees
    if 13 in pts: core_points.append(pts[13])
    if 14 in pts: core_points.append(pts[14])
    
    if len(core_points) > 0:
        return np.mean(core_points, axis=0)
    return None

def calculate_body_lean(pts):
    """Calculate body lean angle from vertical in degrees."""
    # Use shoulder-to-hip vector for lean estimation
    if 5 in pts and 6 in pts and 11 in pts and 12 in pts:
        shoulder_mid = (pts[5] + pts[6]) / 2
        hip_mid = (pts[11] + pts[12]) / 2
        body_vec = shoulder_mid - hip_mid
        # Angle from vertical (0 degrees = straight up)
        vertical = np.array([0, -1])  # negative y is up in image coords
        cos_angle = np.dot(body_vec, vertical) / (norm(body_vec) * norm(vertical))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle_rad = np.arccos(cos_angle)
        return np.degrees(angle_rad)
    return None

def draw_mask_overlay(frame, mask):
    overlay = frame.copy()
    overlay[mask>0] = (50,150,255)
    cv2.addWeighted(overlay, ALPHA_BODY, frame, 1-ALPHA_BODY, 0, frame)

def draw_cone(frame, origin, direction, length, h_angle, v_angle, color, mask=None):
    """Draw 2D cone showing overall gaze direction with smooth confidence gradient.
    Draws multiple shells with increasing transparency from center to edge for gradient effect.
    
    FIXED: Previously only rendered outermost shell (causing invisible cones).
    Now renders all 5 shells with increased alpha values (0.25-0.6) for visibility.
    """
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
        
        # Enhanced visibility: more shells and higher alpha values for screenshots
        num_shells = 7  # More shells for smoother gradient and better visibility
        edge_alpha = 0.45  # Increased for better visibility in screenshots
        center_alpha = 0.8  # Increased for better visibility in screenshots
        
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
print("=" * 60)
print("STARTING MODEL LOADING")
print("=" * 60)
print("Loading models...")

with SuppressStdErr():
    print("  - Loading YOLOv8 Pose model...", flush=True)
    pose_model = YOLO(POSE_MODEL_PATH)
    print("    ✓ Pose model loaded", flush=True)
    
    print("  - Loading YOLOv8 Face model...", flush=True)
    face_model = YOLO(FACE_MODEL_PATH)
    print("    ✓ Face model loaded", flush=True)
    
    # Mask R-CNN is very memory-intensive (~2GB+ RAM)
    # Only load if LOW_MEMORY_MODE is disabled
    if not LOW_MEMORY_MODE:
        print("  - Loading Mask R-CNN model...", flush=True)
        maskrcnn = maskrcnn_resnet50_fpn(weights="DEFAULT")
        maskrcnn.eval()
        print("    ✓ Mask R-CNN loaded", flush=True)
    else:
        print("  - Mask R-CNN: DISABLED (LOW_MEMORY_MODE=True)", flush=True)
        print("    Body mask overlay will not be available", flush=True)
        maskrcnn = None

    print("  - Initializing MediaPipe Hand Landmarker...", flush=True)
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    BaseOptions = python.BaseOptions
    RunningMode = vision.RunningMode
    HandLandmarker = vision.HandLandmarker
    HandLandmarkerOptions = vision.HandLandmarkerOptions

    hands_detector = None
    if os.path.exists(HAND_MODEL_PATH):
        try:
            hands_detector = HandLandmarker.create_from_options(
                HandLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=HAND_MODEL_PATH),
                    running_mode=RunningMode.IMAGE,
                    num_hands=2
                )
            )
            print("    ✓ Hand landmarker loaded", flush=True)
        except Exception as e:
            print(f"    ⚠ Hand landmarker failed to load: {e}", flush=True)
            print("    → Continuing without hand detection...", flush=True)
            hands_detector = None
    else:
        print("    ⚠ Hand landmarker model not found", flush=True)
        print("    → Continuing without hand detection...", flush=True)
        hands_detector = None
        
print("✓ Core models loaded successfully")
print()
print("=" * 60)
print("FEATURE STATUS SUMMARY")
print("=" * 60)
print(f"✓ Pose Detection: ENABLED (17 keypoints)")
if hands_detector is not None:
    print(f"✓ Hand Detection: ENABLED (21 points per hand)")
else:
    print(f"⚠ Hand Detection: DISABLED (model not available)")
if maskrcnn is not None:
    print(f"✓ Body Segmentation: ENABLED (Mask R-CNN)")
else:
    print(f"⚠ Body Segmentation: DISABLED (LOW_MEMORY_MODE=True)")
print(f"  Face Detection: Checking...")
print()

# Initialize MediaPipe FaceMesh/FaceLandmarker for gaze detection
# Supports both old (Solutions API) and new (Tasks API) MediaPipe versions
print("=" * 60)
print("FACE DETECTION SETUP")
print("=" * 60)
print("Initializing face landmarker for gaze detection...")
mp_face = None
face_api_type = None  # 'solutions' or 'tasks' or None

# Try Solutions API first (MediaPipe < 0.10.8) - most stable
if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh'):
    try:
        print("  Attempting Solutions API (legacy)...", flush=True)
        mp_face_mesh = mp.solutions.face_mesh
        mp_face = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        face_api_type = 'solutions'
        print("✓ Face detection initialized (Solutions API)")
    except Exception as e:
        print(f"  ✗ Solutions API failed: {e}")
        mp_face = None
        face_api_type = None

# Try Tasks API if Solutions not available (MediaPipe >= 0.10.8)
if mp_face is None and os.path.exists(FACE_LANDMARKER_PATH):
    try:
        print("  Attempting Tasks API (modern)...", flush=True)
        print(f"    Model: {FACE_LANDMARKER_PATH}", flush=True)
        
        # Import Tasks vision module
        try:
            from mediapipe.tasks.python import vision as mp_vision
        except ImportError as e:
            print(f"  ✗ Cannot import Tasks vision module: {e}")
            raise
        
        # Create options
        FaceLandmarker = mp_vision.FaceLandmarker
        FaceLandmarkerOptions = mp_vision.FaceLandmarkerOptions
        VisionRunningMode = mp_vision.RunningMode
        
        options = FaceLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=FACE_LANDMARKER_PATH),
            running_mode=VisionRunningMode.IMAGE,  # IMAGE mode is more stable than VIDEO
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        print("    Creating FaceLandmarker...", flush=True)
        mp_face = FaceLandmarker.create_from_options(options)
        face_api_type = 'tasks'
        print("✓ Face detection initialized (Tasks API)")
        
    except Exception as e:
        print(f"  ✗ Tasks API initialization failed: {e}")
        print(f"     Error type: {type(e).__name__}")
        import traceback
        print("     Traceback:")
        traceback.print_exc()
        mp_face = None
        face_api_type = None
        print("  → Continuing without gaze detection...")

else:
    if mp_face is None:
        print("  ⚠ No face detection API available")
        print("    - Solutions API: not found")
        print(f"    - Tasks API model: {FACE_LANDMARKER_PATH} not found")
        print("  → To enable gaze: run 'python3 download_face_landmarker.py'")
        mp_face = None
        face_api_type = None

# Final status
if mp_face is not None:
    print(f"\n✓ Gaze cone visualization: ENABLED ({face_api_type} API)")
    print("  Gaze detection will appear as colored cone overlay on video")
else:
    print(f"\n⚠ Gaze cone visualization: DISABLED")
    print("  Reason: Face landmarker model not available (Google CDN issue)")
    print("  Fix: Run 'python3 download_face_alt.py' to try alternative download")
    print("  All other features (pose, hands, mask) will work normally")
print()

print("\n" + "=" * 60)
print("Model initialization complete - starting video setup...")
print("=" * 60)

# -------------------------
# VIDEO SETUP
# -------------------------
# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

print(f"\nOpening video: {VIDEO_PATH}")
cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print(f"✗ ERROR: Could not open video file: {VIDEO_PATH}")
    sys.exit(1)

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = float(cap.get(cv2.CAP_PROP_FPS))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"✓ Video opened successfully:")
print(f"  Resolution: {w}x{h}")
print(f"  FPS: {fps:.2f}")
print(f"  Total frames: {frame_count}")

print(f"\nCreating output video: {OUTPUT_PATH}")
writer = cv2.VideoWriter(OUTPUT_PATH, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w,h))

if not writer.isOpened():
    print(f"✗ ERROR: Could not create output video writer")
    cap.release()
    sys.exit(1)

print("✓ Output video writer ready")

# -------------------------
# CSV SETUP
# -------------------------
csv_fields = ["frame","timestamp","shoulder_width","hip_width","stance_width"]

# Pose keypoints with confidence scores
for i in range(17):
    csv_fields += [f"kps_{i}_x",f"kps_{i}_y",f"kps_{i}_vx",f"kps_{i}_vy",f"kps_{i}_conf"]

# Hand landmarks
for side in ["L","R"]:
    for i in range(21):
        csv_fields += [f"{side}_hand_{i}_x",f"{side}_hand_{i}_y",
                       f"{side}_hand_{i}_vx",f"{side}_hand_{i}_vy"]
    csv_fields += [f"{side}_trigger_pull"]

# Gaze metrics
csv_fields += ["gaze_dir_x","gaze_dir_y","gaze_on_body"]

# Joint angles (in degrees)
csv_fields += ["L_elbow_angle","R_elbow_angle","L_shoulder_angle","R_shoulder_angle",
               "L_hip_angle","R_hip_angle","L_knee_angle","R_knee_angle"]

# Arm extension metrics (normalized by shoulder_width)
csv_fields += ["L_arm_extension","R_arm_extension"]

# Grip metrics
csv_fields += ["hand_distance","grip_symmetry"]

# Body position metrics
csv_fields += ["center_of_mass_x","center_of_mass_y","body_lean_angle"]

# Head orientation (degrees)
csv_fields += ["head_pitch","head_yaw","head_roll"]

# Wrist metrics
csv_fields += ["L_wrist_elevation","R_wrist_elevation","L_elbow_elevation","R_elbow_elevation"]

csvfile = open(CSV_PATH,"w",newline="")
csvwriter = csv.DictWriter(csvfile,fieldnames=csv_fields)
csvwriter.writeheader()

# -------------------------
# STATE
# -------------------------
prev_pose = {}
prev_pose_conf = {}  # Track confidence scores
prev_hand = {}
prev_index_y = {"L":None,"R":None}
prev_forward_3d = None
prev_torso_forward_3d = None  # For smoothing torso vector to reduce arm artifacts
forward_buffer = []
prev_gaze_vec_2d = None  # For 2D outlier rejection
prev_arm_spread = {"L": None, "R": None}  # Track wrist-to-shoulder distance per side
frame_idx = 0
start_time = time.time()
video_start_time = 0.0  # Will be set from video

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
print(f"\nStarting processing: {frame_count} frames at {fps:.2f} FPS")
if SAMPLE_FRAMES is not None:
    print(f"SAMPLE MODE: Processing only frames {SAMPLE_FRAMES}")
print("=" * 60)

# Memory management
import gc
frames_processed = 0

# Torch memory optimization
# Torch memory optimization
torch.set_num_threads(4)  # Optimize for performance
if LOW_MEMORY_MODE:
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    torch.set_num_threads(2)  # Limit CPU threads if memory constrained

with SuppressStdErr():  # suppress any backend warnings during loop
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Skip frames not in SAMPLE_FRAMES if specified
        if SAMPLE_FRAMES is not None and frame_idx not in SAMPLE_FRAMES:
            frame_idx += 1
            continue
        
        # Check if we've reached the max frame limit
        if MAX_FRAMES is not None and frames_processed >= MAX_FRAMES:
            print(f"\n✓ Reached MAX_FRAMES limit ({MAX_FRAMES}), stopping processing...")
            break
        
        # Periodic garbage collection to prevent OOM
        frames_processed += 1
        if frames_processed % 30 == 0:
            gc.collect()
            if LOW_MEMORY_MODE and frames_processed % 10 == 0:
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
            if frames_processed % 60 == 0:
                print(f"  Processed {frames_processed}/{frame_count} frames...", flush=True)

        row = {"frame":frame_idx, "timestamp": frame_idx / fps}
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # -------- POSE --------
        pts = {}
        pts_conf = {}  # Store confidence scores
        result = pose_model(frame, conf=CONF_THRES, max_det=1)[0]
        if result.keypoints is not None and len(result.keypoints.data) > 0:
            kps = result.keypoints.data[0].cpu().numpy()
            for i,(x,y,c) in enumerate(kps):
                pts_conf[i] = c  # Store confidence
                if c < CONF_THRES and i in prev_pose:
                    pts[i] = prev_pose[i]
                    pts_conf[i] = prev_pose_conf.get(i, 0.0)  # Use previous confidence
                    continue
                p = np.array([x,y])
                if i in prev_pose:
                    p = lerp(prev_pose[i], p, TEMP_ALPHA)
                else:
                    p = np.array([x, y])  # Fallback for missing detection
                pts[i] = p
                prev_pose[i] = p
                prev_pose_conf[i] = c
            draw_skeleton(frame, pts, SKELETON_EDGES)

        # Use robust shoulder width calculation with fallback
        shoulder_width = 1.0  # Default fallback
        if 5 in pts and 6 in pts:
            shoulder_width = max(norm(pts[5]-pts[6]), 1.0)  # Ensure non-zero
        row["shoulder_width"] = shoulder_width
        
        # Calculate hip width (normalized by shoulder width for scale-invariance)
        if 11 in pts and 12 in pts:
            row["hip_width"] = norm(pts[11]-pts[12]) / shoulder_width
        else:
            row["hip_width"] = 0.0
        
        # Calculate stance width (foot-to-foot distance, normalized)
        if 15 in pts and 16 in pts:
            row["stance_width"] = norm(pts[15]-pts[16]) / shoulder_width
        else:
            row["stance_width"] = 0.0
        
        # Populate keypoint data in row (x, y, vx, vy, conf for each of 17 keypoints)
        for i in range(17):
            if i in pts:
                row[f"kps_{i}_x"] = pts[i][0]
                row[f"kps_{i}_y"] = pts[i][1]
                # Calculate velocity from previous frame
                if i in prev_pose:
                    row[f"kps_{i}_vx"] = pts[i][0] - prev_pose[i][0]
                    row[f"kps_{i}_vy"] = pts[i][1] - prev_pose[i][1]
                else:
                    row[f"kps_{i}_vx"] = 0.0
                    row[f"kps_{i}_vy"] = 0.0
                row[f"kps_{i}_conf"] = pts_conf.get(i, 0.0)
            else:
                # Keypoint not detected
                row[f"kps_{i}_x"] = 0.0
                row[f"kps_{i}_y"] = 0.0
                row[f"kps_{i}_vx"] = 0.0
                row[f"kps_{i}_vy"] = 0.0
                row[f"kps_{i}_conf"] = 0.0

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
        if maskrcnn is not None:
            with torch.no_grad():
                pred = maskrcnn([F.to_tensor(frame)])[0]
            for m,l,s in zip(pred["masks"],pred["labels"],pred["scores"]):
                if l==1 and s>0.7:
                    body_mask = (m[0]>0.5).numpy()
                    draw_mask_overlay(frame, body_mask)
                    break

        # -------- HANDS --------
        # Initialize all hand landmarks to 0
        for side in ["L","R"]:
            for i in range(21):
                row[f"{side}_hand_{i}_x"] = 0.0
                row[f"{side}_hand_{i}_y"] = 0.0
                row[f"{side}_hand_{i}_vx"] = 0.0
                row[f"{side}_hand_{i}_vy"] = 0.0
            row[f"{side}_trigger_pull"] = 0
        
        if hands_detector is not None:
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
                            p_prev = prev_hand[(side, i)]
                            p = lerp(p_prev, p, HAND_TEMP_ALPHA)  # Use separate hand smoothing
                            # Calculate velocity
                            row[f"{side}_hand_{i}_vx"] = p[0] - p_prev[0]
                            row[f"{side}_hand_{i}_vy"] = p[1] - p_prev[1]
                        else:
                            p = np.array([px, py], dtype=np.float32)  # Fallback for missing detection
                            row[f"{side}_hand_{i}_vx"] = 0.0
                            row[f"{side}_hand_{i}_vy"] = 0.0
                        
                        # Store position in row
                        row[f"{side}_hand_{i}_x"] = p[0]
                        row[f"{side}_hand_{i}_y"] = p[1]
                        
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
        # else: hands_detector is None, all hand metrics remain at 0 (initialized above)

        # -------- FACE + HEAD-TORSO BLENDED GAZE (3D, body-relative) --------
        row["gaze_dir_x"] = row["gaze_dir_y"] = row["gaze_on_body"] = 0
        
        # Only process face if mp_face is initialized
        if mp_face is not None:
            face_results = face_model(frame, conf=CONF_THRES, max_det=1)[0]

            if len(face_results.boxes.xyxy) > 0:
                x1, y1, x2, y2 = map(int, face_results.boxes.xyxy[0])
                # Validate bounding box is within frame and has minimum size
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                # Ensure face crop has minimum dimensions (20x20 pixels)
                if (x2 - x1) >= 20 and (y2 - y1) >= 20:
                    face_crop = rgb[y1:y2, x1:x2]
                    mp_results = None
                    
                    try:
                        if face_api_type == 'solutions':
                            # Solutions API (legacy)
                            mp_results = mp_face.process(face_crop)
                            has_landmarks = mp_results and mp_results.multi_face_landmarks
                            
                        elif face_api_type == 'tasks':
                            # Tasks API (modern) - using IMAGE mode (more stable)
                            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=face_crop)
                            mp_results = mp_face.detect(mp_image)  # IMAGE mode uses detect() not detect_for_video()
                            has_landmarks = mp_results and mp_results.face_landmarks
                            
                    except Exception as e:
                        # Skip face processing on error but continue pipeline
                        has_landmarks = False

                    if has_landmarks:
                        # Extract landmarks based on API type
                        if face_api_type == 'solutions':
                            lm = mp_results.multi_face_landmarks[0].landmark
                        else:  # tasks
                            lm = mp_results.face_landmarks[0]

                        def L(i):
                            lm_i = lm[i]
                            # Convert normalized coordinates to frame coordinates
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
                            # Use robust focal length estimation: average of width and height
                            # This adapts better to different aspect ratios and camera angles
                            focal_length = (w + h) / 2.0
                            camera_matrix = np.array([[focal_length, 0, w / 2.0],
                                                      [0, focal_length, h / 2.0],
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
                                    # Validate eye positions are reasonable
                                    eye_distance = np.linalg.norm(eye_right - eye_left)
                                    if eye_distance > 10:  # Minimum eye distance (pixels) for valid detection
                                        eye_mid = (eye_left + eye_right) / 2
                                        # Position cone origin inside head (behind eyes) so cone edges intersect eyes
                                        cone_origin = eye_mid - gaze_vec * CONE_ORIGIN_OFFSET
                                        
                                        # Validate cone origin is within reasonable bounds
                                        if 0 <= cone_origin[0] < w and 0 <= cone_origin[1] < h:
                                            # Debug: Print gaze detection status
                                            if frame_idx < 5 or frame_idx % 30 == 0:  # Print for first 5 frames and every 30th frame
                                                print(f"  Frame {frame_idx}: Gaze detected - origin: {cone_origin.astype(int)}, direction: {gaze_vec}")
                                            
                                            # Draw cone with radial confidence gradient (center=0.7 alpha, edges=0.35)
                                            # Changed to red for high visibility against all backgrounds
                                            # Body mask clipping shows only external portion
                                            draw_cone(frame, cone_origin, gaze_vec, GAZE_LENGTH + CONE_ORIGIN_OFFSET,
                                                      GAZE_CONE_H_ANGLE, GAZE_CONE_V_ANGLE, (0, 0, 255), mask=body_mask)
                                        else:
                                            if frame_idx < 5:
                                                print(f"  Frame {frame_idx}: Cone origin out of bounds: {cone_origin.astype(int)}")
                                    else:
                                        if frame_idx < 5:
                                            print(f"  Frame {frame_idx}: Eye distance too small: {eye_distance:.1f}px")
                                else:
                                    if frame_idx < 5:
                                        print(f"  Frame {frame_idx}: Eye landmarks not detected")

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
        
        # -------- CALCULATE ADDITIONAL METRICS --------
        # Joint angles
        row["L_elbow_angle"] = calculate_angle(pts.get(5), pts.get(7), pts.get(9)) or 0.0  # L shoulder-elbow-wrist
        row["R_elbow_angle"] = calculate_angle(pts.get(6), pts.get(8), pts.get(10)) or 0.0  # R shoulder-elbow-wrist
        row["L_shoulder_angle"] = calculate_angle(pts.get(11), pts.get(5), pts.get(7)) or 0.0  # L hip-shoulder-elbow
        row["R_shoulder_angle"] = calculate_angle(pts.get(12), pts.get(6), pts.get(8)) or 0.0  # R hip-shoulder-elbow
        row["L_hip_angle"] = calculate_angle(pts.get(5), pts.get(11), pts.get(13)) or 0.0  # L shoulder-hip-knee
        row["R_hip_angle"] = calculate_angle(pts.get(6), pts.get(12), pts.get(14)) or 0.0  # R shoulder-hip-knee
        row["L_knee_angle"] = calculate_angle(pts.get(11), pts.get(13), pts.get(15)) or 0.0  # L hip-knee-ankle
        row["R_knee_angle"] = calculate_angle(pts.get(12), pts.get(14), pts.get(16)) or 0.0  # R hip-knee-ankle
        
        # Arm extension (wrist to shoulder distance, normalized by shoulder_width)
        if 5 in pts and 9 in pts:
            row["L_arm_extension"] = norm(pts[9] - pts[5]) / shoulder_width
        else:
            row["L_arm_extension"] = 0.0
        
        if 6 in pts and 10 in pts:
            row["R_arm_extension"] = norm(pts[10] - pts[6]) / shoulder_width
        else:
            row["R_arm_extension"] = 0.0
        
        # Hand distance and grip symmetry
        # Check if both hands detected in hand landmarks
        hand_detected = {"L": False, "R": False}
        hand_centers = {}
        if hands_detector is not None and 'hand_res' in locals() and hand_res.hand_landmarks and len(hand_res.hand_landmarks) >= 1:
            for idx, (side, hand) in enumerate(zip(["L", "R"], hand_res.hand_landmarks)):
                if idx < len(hand_res.hand_landmarks):
                    hand_detected[side] = True
                    # Use wrist (landmark 0) as hand center
                    if (side, 0) in prev_hand:
                        hand_centers[side] = prev_hand[(side, 0)]
        
        if hand_detected["L"] and hand_detected["R"]:
            row["hand_distance"] = norm(hand_centers["L"] - hand_centers["R"]) / shoulder_width
            row["grip_symmetry"] = 1.0  # Both hands detected
        else:
            row["hand_distance"] = 0.0
            row["grip_symmetry"] = 0.0  # One or both hands missing
        
        # Center of mass
        com = calculate_center_of_mass(pts)
        if com is not None:
            row["center_of_mass_x"] = com[0] / shoulder_width
            row["center_of_mass_y"] = com[1] / shoulder_width
        else:
            row["center_of_mass_x"] = 0.0
            row["center_of_mass_y"] = 0.0
        
        # Body lean angle
        row["body_lean_angle"] = calculate_body_lean(pts) or 0.0
        
        # Head orientation (from rotation matrix if available)
        # These will be populated if we have face detection
        row["head_pitch"] = 0.0
        row["head_yaw"] = 0.0
        row["head_roll"] = 0.0
        
        # Extract Euler angles from rotation matrix if we calculated it
        if 'rot_mat' in locals() and rot_mat is not None:
            # Convert rotation matrix to Euler angles (in degrees)
            # Using standard aerospace convention: yaw-pitch-roll
            sy = np.sqrt(rot_mat[0, 0] * rot_mat[0, 0] + rot_mat[1, 0] * rot_mat[1, 0])
            singular = sy < 1e-6
            if not singular:
                row["head_pitch"] = np.degrees(np.arctan2(-rot_mat[2, 0], sy))
                row["head_yaw"] = np.degrees(np.arctan2(rot_mat[1, 0], rot_mat[0, 0]))
                row["head_roll"] = np.degrees(np.arctan2(rot_mat[2, 1], rot_mat[2, 2]))
            else:
                row["head_pitch"] = np.degrees(np.arctan2(-rot_mat[2, 0], sy))
                row["head_yaw"] = np.degrees(np.arctan2(-rot_mat[1, 2], rot_mat[1, 1]))
                row["head_roll"] = 0.0
        
        # Wrist and elbow elevation (y-coordinate, normalized)
        # Lower y value = higher in frame (image coordinates)
        if 9 in pts:  # L wrist
            row["L_wrist_elevation"] = -pts[9][1] / shoulder_width  # Negative for intuitive "higher = positive"
        else:
            row["L_wrist_elevation"] = 0.0
        
        if 10 in pts:  # R wrist
            row["R_wrist_elevation"] = -pts[10][1] / shoulder_width
        else:
            row["R_wrist_elevation"] = 0.0
        
        if 7 in pts:  # L elbow
            row["L_elbow_elevation"] = -pts[7][1] / shoulder_width
        else:
            row["L_elbow_elevation"] = 0.0
        
        if 8 in pts:  # R elbow
            row["R_elbow_elevation"] = -pts[8][1] / shoulder_width
        else:
            row["R_elbow_elevation"] = 0.0
        
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
if hands_detector is not None:
    hands_detector.close()
if mp_face is not None:
    if face_api_type == 'solutions':
        mp_face.close()
    elif face_api_type == 'tasks':
        mp_face.close()
csvfile.close()
total_time = time.time() - start_time
print(f"\nFinished processing {frame_count} frames in {total_time:.2f} seconds ({frame_count/total_time:.2f} FPS).")
