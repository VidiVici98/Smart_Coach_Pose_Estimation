import cv2
import torch
import numpy as np
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
OUTPUT_PATH = "videos/output_review.mp4"

POSE_MODEL_PATH = "yolov8m-pose.pt"
HAND_MODEL_PATH = "models/hand_landmarker.task"

CONF_THRES = 0.2
TEMP_ALPHA = 0.7

ALPHA_BODY = 0.6
ALPHA_CONE = 0.6

MUZZLE_LENGTH = 220
MUZZLE_ANGLE_RAD = 0.003  # ~3 milliradians

# ======================================
# STANDARD HAND CONNECTIONS (21 pts)
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
                     [np.sin(-theta),   np.cos(-theta)]])

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
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

writer = cv2.VideoWriter(
    OUTPUT_PATH,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (w, h)
)

prev_pose = {}
prev_hand = {}

frame_idx = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # ---- YOLO POSE ----
    pts = {}
    result = pose_model(frame, conf=CONF_THRES, max_det=1)[0]
    if result.keypoints is not None:
        kps = result.keypoints.data[0].cpu().numpy()
        for i,(x,y,c) in enumerate(kps):
            if c < CONF_THRES:
                if i in prev_pose:
                    pts[i] = prev_pose[i]
                continue
            p = np.array([x, y], np.float32)
            if i in prev_pose:
                p = lerp(prev_pose[i], p, TEMP_ALPHA)
            pts[i] = p
            prev_pose[i] = p
            cv2.circle(frame, tuple(p.astype(int)), 4, (0,255,255), -1)

    SKELETON = [
        (5,7),(7,9),(6,8),(8,10),
        (5,6),(5,11),(6,12),
        (11,12),(11,13),(13,15),
        (12,14),(14,16)
    ]
    for a,b in SKELETON:
        if a in pts and b in pts:
            cv2.line(frame, tuple(pts[a].astype(int)),
                     tuple(pts[b].astype(int)), (0,255,0), 2)

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
    hand_results = hands_detector.detect_for_video(mp_frame,
                        int(cap.get(cv2.CAP_PROP_POS_MSEC)))

    if hand_results.hand_landmarks:
        for hand in hand_results.hand_landmarks:
            pts_hand = []
            for i,lm in enumerate(hand):
                px = int(lm.x * w)
                py = int(lm.y * h)
                p = np.array([px, py], np.float32)
                if i in prev_hand:
                    p = lerp(prev_hand[i], p, TEMP_ALPHA)
                prev_hand[i] = p
                pts_hand.append(p.astype(int))
                cv2.circle(frame, tuple(p.astype(int)), 3, (255,0,0), -1)
            for (a,b) in HAND_CONNECTIONS:
                cv2.line(frame, pts_hand[a], pts_hand[b], (255,0,0), 2)

    # ---- Muzzle Safety ----
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
                        break
            draw_muzzle_cone(frame, origin, direction, not unsafe)

    writer.write(frame)
    frame_idx += 1
    print(f"Frame {frame_idx}/{int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}", end="\r")

cap.release()
writer.release()
hands_detector.close()
print("\nFinished. Output saved to:", OUTPUT_PATH)
