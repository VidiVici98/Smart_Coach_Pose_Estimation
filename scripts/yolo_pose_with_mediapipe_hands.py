import cv2
import csv
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
from scripts.pose_demo import HAND_CONNECTIONS, BaseOptions

# ===============================
# Vector / Angle Utilities
# ===============================
def vec(a, b):
    """Vector from point b to point a"""
    return np.array(a, dtype=np.float32) - np.array(b, dtype=np.float32)

def norm(v):
    return np.linalg.norm(v) + 1e-6

def unit(v):
    return v / norm(v)

def angle_3pts(a, b, c):
    """Angle at point b formed by points a-b-c in degrees [0,180]"""
    ba = vec(a, b)
    bc = vec(c, b)
    cosang = np.dot(ba, bc) / (norm(ba) * norm(bc))
    return np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0)))

def signed_angle(v1, v2):
    """Signed angle between 2D vectors"""
    v1u = unit(v1)
    v2u = unit(v2)
    det = v1u[0]*v2u[1] - v1u[1]*v2u[0]
    dot = np.dot(v1u, v2u)
    return np.degrees(np.arctan2(det, dot))

def shoulder_midpoint(pts):
    L_sh, R_sh = np.array(pts[5], np.float32), np.array(pts[6], np.float32)
    return (L_sh + R_sh) / 2

def shoulder_width(pts):
    L_sh, R_sh = np.array(pts[5], np.float32), np.array(pts[6], np.float32)
    return norm(R_sh - L_sh)

def normalize_point(pt, origin, scale):
    return (np.array(pt, np.float32) - origin) / scale

def interpolate_missing(prev_pts, idx):
    return prev_pts.get(idx, None)

# ===============================
# Config
# ===============================
VIDEO_PATH = "videos/test_video.mp4"
POSE_MODEL = "yolov8m-pose.pt"
HAND_MODEL = "models/hand_landmarker.task"

WINDOW = "YOLO Pose + Hands + Muzzle"
IMG_SIZE = 640
CONF_THRES = 0.1
IOU_THRES = 0.3
MAX_DET = 1
WRIST_CONF = 0.4
HAND_CROP_SIZE = 220

POSE_SKELETON = [
    (5, 7), (7, 9),
    (6, 8), (8, 10),
    (5, 6),
    (5, 11), (6, 12),
    (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16)
]

# ===============================
# MediaPipe Hands
# ===============================
VisionRunningMode = mp.tasks.vision.RunningMode
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
hand_landmarker = HandLandmarker.create_from_options(
    HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=HAND_MODEL),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=1
    )
)

# ===============================
# Load YOLO
# ===============================
pose_model = YOLO(POSE_MODEL)
cap = cv2.VideoCapture(VIDEO_PATH)
cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)

# ===============================
# CSV Output
# ===============================
csv_file = open("data/yolo_pose_hands.csv", "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["frame", "type", "id", "x", "y", "confidence"])

analytics_file = open("data/pose_analytics.csv", "w", newline="")
analytics_writer = csv.writer(analytics_file)
analytics_writer.writerow([
    "frame",
    "elbow_angle_L", "elbow_angle_R",
    "wrist_height_delta",
    "shoulder_line_angle", "head_vs_shoulder_angle",
    "left_trigger_vec_x", "left_trigger_vec_y",
    "right_trigger_vec_x", "right_trigger_vec_y",
    "left_muzzle_vec_x", "left_muzzle_vec_y",
    "right_muzzle_vec_x", "right_muzzle_vec_y",
    "muzzle_rise_L", "muzzle_rise_R",
    "left_muzzle_safe", "right_muzzle_safe"
])

frame_num = 0
prev_pose_pts = {}
prev_hand_pts = {}
prev_muzzle_vec = {"L": None, "R": None}

# ===============================
# Main Loop
# ===============================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    h, w, _ = frame.shape
    wrists = []

    # --------- YOLO Pose Detection ---------
    results = pose_model(frame, imgsz=IMG_SIZE, conf=CONF_THRES, iou=IOU_THRES, max_det=MAX_DET, verbose=False)[0]
    pts = {}
    if results.keypoints is not None:
        kps = results.keypoints.data[0]
        for i, (x, y, c) in enumerate(kps):
            if c < CONF_THRES:
                val = interpolate_missing(prev_pose_pts, i)
                if val is None: continue
                px, py = val
            else:
                px, py = int(x), int(y)
            if i in prev_pose_pts:
                px = int(0.7*prev_pose_pts[i][0] + 0.3*px)
                py = int(0.7*prev_pose_pts[i][1] + 0.3*py)
            prev_pose_pts[i] = (px, py)
            pts[i] = (px, py)
            radius = max(2,int(4*c))
            alpha = min(1.0,max(0.3,c))
            cv2.circle(frame,(px,py),radius,(0,int(255*alpha),255),-1)
            writer.writerow([frame_num,"pose",i,px,py,float(c)])
        for a,b in POSE_SKELETON:
            if a in pts and b in pts:
                cv2.line(frame, pts[a], pts[b], (0,255,0),2)
        if 9 in pts and kps[9][2]>=WRIST_CONF:
            wrists.append(("L",pts[9]))
        if 10 in pts and kps[10][2]>=WRIST_CONF:
            wrists.append(("R",pts[10]))

    # --------- Normalization ---------
    normalized_pts = {}
    if 5 in pts and 6 in pts:
        origin = shoulder_midpoint(pts)
        scale = shoulder_width(pts)
        for i,p in pts.items():
            normalized_pts[i] = normalize_point(p, origin, scale)

    # --------- Analytics: Angles, Trigger, Muzzle ---------
    required_pts = [0,5,6,7,8,9,10]
    if all(k in normalized_pts or k in prev_pose_pts for k in required_pts):
        for k in required_pts:
            if k not in normalized_pts and k in prev_pose_pts:
                normalized_pts[k] = normalize_point(prev_pose_pts[k], origin, scale)

        L_sh,R_sh = normalized_pts[5],normalized_pts[6]
        L_el,R_el = normalized_pts[7],normalized_pts[8]
        L_wr,R_wr = normalized_pts[9],normalized_pts[10]
        head = normalized_pts[0]

        # Angles
        elbow_angle_L = angle_3pts(L_sh,L_el,L_wr)
        elbow_angle_R = angle_3pts(R_sh,R_el,R_wr)
        wrist_height_delta = L_wr[1]-R_wr[1]
        shoulder_vec = vec(R_sh,L_sh)
        shoulder_line_angle = signed_angle(shoulder_vec,np.array([1.0,0.0]))
        head_vec = vec(head,(L_sh+R_sh)/2)
        head_vs_shoulder_angle = signed_angle(shoulder_vec,head_vec)

        # Trigger finger vector (proxy)
        left_trigger_vec = vec(L_wr, normalized_pts.get(9,L_wr))
        right_trigger_vec = vec(R_wr, normalized_pts.get(10,R_wr))

        # --------- Muzzle vector (proxy) ---------
        left_muzzle_vec = vec(L_wr, normalized_pts.get(9,L_wr))
        right_muzzle_vec = vec(R_wr, normalized_pts.get(10,R_wr))

        # Muzzle rise
        muzzle_rise_L = 0
        muzzle_rise_R = 0
        if prev_muzzle_vec["L"] is not None:
            muzzle_rise_L = left_muzzle_vec[1] - prev_muzzle_vec["L"][1]
        if prev_muzzle_vec["R"] is not None:
            muzzle_rise_R = right_muzzle_vec[1] - prev_muzzle_vec["R"][1]
        prev_muzzle_vec["L"] = left_muzzle_vec
        prev_muzzle_vec["R"] = right_muzzle_vec

        # Safety check: forward cone (simple)
        left_muzzle_safe = right_muzzle_safe = True
        for vec_ in [left_muzzle_vec, right_muzzle_vec]:
            if vec_[1] < -0.3:  # roughly up toward face
                if vec_ is left_muzzle_vec: left_muzzle_safe = False
                else: right_muzzle_safe = False

        analytics_writer.writerow([
            frame_num,
            round(elbow_angle_L,2), round(elbow_angle_R,2),
            round(wrist_height_delta,3),
            round(shoulder_line_angle,2), round(head_vs_shoulder_angle,2),
            round(left_trigger_vec[0],3), round(left_trigger_vec[1],3),
            round(right_trigger_vec[0],3), round(right_trigger_vec[1],3),
            round(left_muzzle_vec[0],3), round(left_muzzle_vec[1],3),
            round(right_muzzle_vec[0],3), round(right_muzzle_vec[1],3),
            round(muzzle_rise_L,3), round(muzzle_rise_R,3),
            left_muzzle_safe, right_muzzle_safe
        ])

    # --------- Wrist-Gated Hand Detection ---------
    for side,(wx,wy) in wrists:
        half = HAND_CROP_SIZE//2
        x1 = max(wx-half,0)
        y1 = max(wy-half,0)
        x2 = min(wx+half,w)
        y2 = min(wy+half,h)
        crop = frame[y1:y2,x1:x2]
        if crop.size==0: continue
        rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb_crop)
        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        hand_result = hand_landmarker.detect_for_video(mp_image,timestamp)
        if not hand_result.hand_landmarks:
            if (frame_num-1,side) in prev_hand_pts:
                pts_hand = prev_hand_pts[(frame_num-1,side)]
            else:
                continue
        else:
            hand = hand_result.hand_landmarks[0]
            pts_hand = []
            for i,lm in enumerate(hand):
                px = int(x1 + lm.x*(x2-x1))
                py = int(y1 + lm.y*(y2-y1))
                pts_hand.append((px,py))
                prev_hand_pts[(frame_num,side,i)] = (px,py)
                cv2.circle(frame,(px,py),3,(255,0,0),-1)
                writer.writerow([frame_num,f"hand_{side}",i,px,py,lm.z])
            for a,b in HAND_CONNECTIONS:
                cv2.line(frame, pts_hand[a], pts_hand[b], (255,0,0),2)
        cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,255),1)

    # --------- Display ---------
    cv2.imshow(WINDOW,frame)
    if cv2.waitKey(1)&0xFF==ord("q"): break
    frame_num += 1

# ===============================
# Cleanup
# ===============================
csv_file.close()
analytics_file.close()
cap.release()
cv2.destroyAllWindows()
hand_landmarker.close()
