import cv2
import torch
import numpy as np
import csv
from ultralytics import YOLO
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.transforms import functional as F
import mediapipe as mp

# ---- MediaPipe Tasks API imports ----
BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

# ======================================
# CONFIG
# ======================================
VIDEO_PATH = "videos/test_video.mp4"
OUTPUT_PATH = "videos/output_test-2.mp4"
CSV_PATH = "data/analytics.csv"

POSE_MODEL_PATH = "yolov8m-pose.pt"
HAND_MODEL_PATH = "models/hand_landmarker.task"

CONF_THRES = 0.2
TEMP_ALPHA = 0.7

ALPHA_BODY = 0.6
ALPHA_CONE = 0.6

MUZZLE_LENGTH = 350
MUZZLE_ANGLE_RAD = 0.003  # ~3 milliradians

# ======================================
# HAND CONNECTIONS
# ======================================
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20)
]

# ======================================
# UTILS
# ======================================
def norm(v): return np.linalg.norm(v) + 1e-6
def unit(v): return v / norm(v)
def lerp(a, b, t): return a*(1-t) + b*t
def angle_between(v1, v2): return np.arccos(np.clip(np.dot(unit(v1), unit(v2)), -1, 1)) * 180/np.pi

def draw_mask_overlay(frame, mask, color):
    overlay = frame.copy()
    overlay[mask > 0] = color
    cv2.addWeighted(overlay, ALPHA_BODY, frame, 1 - ALPHA_BODY, 0, frame)

def draw_muzzle_cone(frame, origin, direction, safe):
    overlay = frame.copy()
    o = origin.astype(np.float32)
    d = unit(direction)
    theta = MUZZLE_ANGLE_RAD
    rotL = np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta),  np.cos(theta)]])
    rotR = np.array([[np.cos(-theta), -np.sin(-theta)],
                     [np.sin(-theta),  np.cos(-theta)]])
    left = o + (rotL @ d) * MUZZLE_LENGTH
    right = o + (rotR @ d) * MUZZLE_LENGTH
    pts = np.array([o, left, right], np.int32)
    color = (0,255,0) if safe else (0,0,255)
    cv2.fillConvexPoly(overlay, pts, color)
    cv2.addWeighted(overlay, ALPHA_CONE, frame, 1 - ALPHA_CONE, 0, frame)

# ======================================
# LOAD MODELS
# ======================================
device = torch.device("cpu")

pose_model = YOLO(POSE_MODEL_PATH)

maskrcnn = maskrcnn_resnet50_fpn(weights="DEFAULT")
maskrcnn.to(device).eval()

hand_options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=HAND_MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2
)
hands_detector = HandLandmarker.create_from_options(hand_options)

# ======================================
# VIDEO SETUP
# ======================================
cap = cv2.VideoCapture(VIDEO_PATH)
w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
writer = cv2.VideoWriter(OUTPUT_PATH, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

prev_pose, prev_hand = {}, {}
prev_pose_norm, prev_hand_norm = {}, {}

# ---- CSV Setup ----
csv_fields = ["frame", "shoulder_width", "muzzle_safe"]
for i in range(33):
    csv_fields += [f"kps_{i}_x", f"kps_{i}_y", f"kps_{i}_vx", f"kps_{i}_vy"]
for hand in ["L","R"]:
    for i in range(21):
        csv_fields += [f"{hand}_hand_{i}_x", f"{hand}_hand_{i}_y", f"{hand}_hand_{i}_vx", f"{hand}_hand_{i}_vy"]
for side in ["L","R"]:
    csv_fields += [f"{side}_trigger_pull"]

csvfile = open(CSV_PATH,"w",newline="")
csvwriter = csv.DictWriter(csvfile, fieldnames=csv_fields)
csvwriter.writeheader()

frame_idx = 0
prev_index_y = {"L": None, "R": None}
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    row = {"frame": frame_idx}
    pts = {}
    # ---- YOLO POSE ----
    result = pose_model(frame, conf=CONF_THRES, max_det=1)[0]
    if result.keypoints is not None:
        kps = result.keypoints.data[0].cpu().numpy()
        for i,(x,y,c) in enumerate(kps):
            if c < CONF_THRES and i in prev_pose:
                pts[i] = prev_pose[i]
                continue
            p = np.array([x, y], np.float32)
            if i in prev_pose:
                p = lerp(prev_pose[i], p, TEMP_ALPHA)
            pts[i] = p
            prev_pose[i] = p

    # ---- Shoulder width ----
    shoulder_width = norm(pts[6]-pts[5]) if 5 in pts and 6 in pts else 1.0
    row["shoulder_width"] = shoulder_width

    # ---- YOLO keypoints normalized + velocity ----
    for i in range(33):
        if i in pts:
            p = pts[i]
            prev_n = prev_pose_norm.get(i, p / shoulder_width)
            norm_p = p / shoulder_width
            vel = norm_p - prev_n
            prev_pose_norm[i] = norm_p
            row[f"kps_{i}_x"] = norm_p[0]
            row[f"kps_{i}_y"] = norm_p[1]
            row[f"kps_{i}_vx"] = vel[0]
            row[f"kps_{i}_vy"] = vel[1]
        else:
            row[f"kps_{i}_x"] = row[f"kps_{i}_y"] = row[f"kps_{i}_vx"] = row[f"kps_{i}_vy"] = 0.0

    # ---- MASK R‑CNN BODY ----
    img_tensor = F.to_tensor(frame).to(device)
    with torch.no_grad():
        pred = maskrcnn([img_tensor])[0]

    body_mask = None
    for m, label, score in zip(pred["masks"], pred["labels"], pred["scores"]):
        if label == 1 and score > 0.6:
            body_mask = (m[0] > 0.5).cpu().numpy().astype(np.uint8)
            break
    if body_mask is not None:
        draw_mask_overlay(frame, body_mask*255, (50,150,255))

    # ---- MediaPipe Hands Tasks ----
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    hand_results = hands_detector.detect_for_video(mp_frame, int(cap.get(cv2.CAP_PROP_POS_MSEC)))

    for hand_side, hand in zip(["L","R"], hand_results.hand_landmarks or []):
        pts_hand = []
        index_y = None
        for i,lm in enumerate(hand):
            px, py = int(lm.x * w), int(lm.y * h)
            p = np.array([px, py], np.float32)
            prev_n = prev_hand_norm.get((hand_side,i), p / shoulder_width)
            norm_p = p / shoulder_width
            vel = norm_p - prev_n
            prev_hand_norm[(hand_side,i)] = norm_p
            row[f"{hand_side}_hand_{i}_x"] = norm_p[0]
            row[f"{hand_side}_hand_{i}_y"] = norm_p[1]
            row[f"{hand_side}_hand_{i}_vx"] = vel[0]
            row[f"{hand_side}_hand_{i}_vy"] = vel[1]

            if i in prev_hand:
                p = lerp(prev_hand[(hand_side,i)], p, TEMP_ALPHA)
            prev_hand[(hand_side,i)] = p
            pts_hand.append(p.astype(int))

            if i==8:  # index fingertip for trigger pull
                index_y = p[1]

            cv2.circle(frame, tuple(p.astype(int)), 3, (255,0,0), -1)

        # Draw hand connections
        for a,b in HAND_CONNECTIONS:
            cv2.line(frame, pts_hand[a], pts_hand[b], (255,0,0), 2)

        # ---- Trigger pull detection
        if index_y is not None and prev_index_y[hand_side] is not None:
            row[f"{hand_side}_trigger_pull"] = int(index_y < prev_index_y[hand_side])  # simple upward movement
        else:
            row[f"{hand_side}_trigger_pull"] = 0
        prev_index_y[hand_side] = index_y

    # ---- Muzzle Safety ----
    muzzle_safe = True
    for wrist, elbow in [(9,7),(10,8)]:
        if wrist in pts and elbow in pts:
            origin = pts[wrist]
            direction = pts[wrist] - pts[elbow]
            unsafe = False
            if body_mask is not None:
                for d in np.linspace(0, MUZZLE_LENGTH, 30):
                    sample_pt = (origin + unit(direction)*d).astype(int)
                    x_s,y_s = sample_pt
                    if 0 <= x_s < w and 0 <= y_s < h and body_mask[y_s,x_s]:
                        unsafe = True
                        muzzle_safe = False
                        break
            draw_muzzle_cone(frame, origin, direction, not unsafe)
    row["muzzle_safe"] = muzzle_safe

    writer.write(frame)
    csvwriter.writerow(row)

    frame_idx += 1
    print(f"Frame {frame_idx}/{int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}", end="\r")

cap.release()
writer.release()
hands_detector.close()
csvfile.close()
print("\nFinished. Output saved to:", OUTPUT_PATH, "CSV saved to:", CSV_PATH)
