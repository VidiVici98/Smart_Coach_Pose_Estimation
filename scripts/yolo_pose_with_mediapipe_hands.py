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

CONF_THRES = 0.15
TEMP_ALPHA = 0.7
GAZE_ALPHA_3D = 0.5

ALPHA_BODY = 0.35
ALPHA_CONE = 0.25
GAZE_LENGTH = 1000
GAZE_CONE_RAD = 0.12
GAZE_BINOCULAR_FACTOR = 0.25

# Max gaze rotation per frame (rad/frame)
MAX_GAZE_ROT = 0.12  # ~7°/frame

# -------------------------
# SKELETON (16-keypoint YOLOv8)
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
def norm(v): return np.linalg.norm(v) + 1e-6
def unit(v): return v / norm(v)
def lerp(a,b,t): return a*(1-t) + b*t

def draw_mask_overlay(frame, mask):
    overlay = frame.copy()
    overlay[mask>0] = (50,150,255)
    cv2.addWeighted(overlay, ALPHA_BODY, frame, 1-ALPHA_BODY, 0, frame)

def draw_cone(frame, origin, direction, length, angle, color):
    overlay = frame.copy()
    o = origin.astype(np.float32)
    d = unit(direction)
    rot = lambda a: np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    left  = o + (rot(angle) @ d) * length
    right = o + (rot(-angle) @ d) * length
    pts = np.array([o,left,right], np.int32)
    cv2.fillConvexPoly(overlay, pts, color)
    cv2.addWeighted(overlay, ALPHA_CONE, frame, 1-ALPHA_CONE, 0, frame)

def draw_skeleton(frame, keypoints, edges, color=(0,255,255), radius=3, thickness=2):
    for a,b in edges:
        if a in keypoints and b in keypoints:
            cv2.line(frame, tuple(keypoints[a].astype(int)), tuple(keypoints[b].astype(int)), color, thickness)
    for i,p in keypoints.items():
        cv2.circle(frame, tuple(p.astype(int)), radius, color, -1)

def clamp_rotation(prev_vec, curr_vec, max_angle):
    """Clamp rotation between prev_vec and curr_vec to max_angle (rad)"""
    prev_vec = unit(prev_vec)
    curr_vec = unit(curr_vec)
    dot = np.clip(np.dot(prev_vec, curr_vec), -1.0, 1.0)
    angle = np.arccos(dot)
    if angle <= max_angle:
        return curr_vec
    # rotation axis
    axis = np.cross(prev_vec, curr_vec)
    if norm(axis) < 1e-6:  # vectors aligned or opposite
        return prev_vec
    axis = unit(axis)
    # Rodrigues rotation formula
    K = np.array([[0,-axis[2],axis[1]],
                  [axis[2],0,-axis[0]],
                  [-axis[1],axis[0],0]])
    R = np.eye(3) + np.sin(max_angle)*K + (1-np.cos(max_angle))*(K@K)
    return R @ prev_vec

# -------------------------
# LOAD MODELS
# -------------------------
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

mp_face = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True, max_num_faces=1)

# -------------------------
# VIDEO SETUP
# -------------------------
cap = cv2.VideoCapture(VIDEO_PATH)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = float(cap.get(cv2.CAP_PROP_FPS))
writer = cv2.VideoWriter(OUTPUT_PATH, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w,h))

# -------------------------
# CSV SETUP
# -------------------------
csv_fields = ["frame","shoulder_width"]
for i in range(17):
    csv_fields += [f"kps_{i}_x",f"kps_{i}_y",f"kps_{i}_vx",f"kps_{i}_vy"]
for side in ["L","R"]:
    for i in range(21):
        csv_fields += [f"{side}_hand_{i}_x",f"{side}_hand_{i}_y",f"{side}_hand_{i}_vx",f"{side}_hand_{i}_vy"]
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
frame_idx = 0

# -------------------------
# FACE MODEL 3D POINTS
# -------------------------
FACE_3D_POINTS = np.array([
    [0.0, 0.0, 0.0],       # Nose
    [0.0, -63.6, -12.5],   # Chin
    [-43.3, 32.7, -26.0],  # Left eye outer
    [43.3, 32.7, -26.0],   # Right eye outer
    [-28.9, -28.9, -24.1], # Left mouth
    [28.9, -28.9, -24.1]   # Right mouth
])

# -------------------------
# MAIN LOOP
# -------------------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    row = {"frame":frame_idx}
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ---------------- POSE ----------------
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
            pts[i] = p
            prev_pose[i] = p

        draw_skeleton(frame, pts, SKELETON_EDGES)

    shoulder_width = norm(pts[5]-pts[6]) if 5 in pts and 6 in pts else 1.0
    row["shoulder_width"] = shoulder_width

    # ---------------- BODY MASK ----------------
    body_mask = None
    with torch.no_grad():
        pred = maskrcnn([F.to_tensor(frame)])[0]
    for m,l,s in zip(pred["masks"],pred["labels"],pred["scores"]):
        if l==1 and s>0.7:
            body_mask = (m[0]>0.5).numpy()
            draw_mask_overlay(frame, body_mask)
            break

    # ---------------- HANDS ----------------
    hand_res = hands_detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if hand_res.hand_landmarks:
        for side,hand in zip(["L","R"], hand_res.hand_landmarks):
            pts_hand=[]
            index_y=None
            for i,lm in enumerate(hand):
                p = np.array([lm.x*w,lm.y*h])
                if (side,i) in prev_hand:
                    p = lerp(prev_hand[(side,i)],p,TEMP_ALPHA)
                prev_hand[(side,i)] = p

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

    # ---------------- FACE + ANGLE-CLAMPED GAZE ----------------
    row["gaze_dir_x"]=row["gaze_dir_y"]=row["gaze_on_body"]=0
    face_results = face_model(frame, conf=CONF_THRES, max_det=1)[0]

    if len(face_results.boxes.xyxy)>0:
        x1,y1,x2,y2 = map(int, face_results.boxes.xyxy[0])
        face_crop = rgb[y1:y2, x1:x2]
        mp_results = mp_face.process(face_crop)

        if mp_results.multi_face_landmarks:
            lm = mp_results.multi_face_landmarks[0].landmark
            def L(i):
                return np.array([lm[i].x*(x2-x1)+x1, lm[i].y*(y2-y1)+y1], dtype=np.float32)

            image_points = np.array([L(1),L(152),L(33),L(263),L(61),L(291)], dtype=np.float32)
            model_points = FACE_3D_POINTS * shoulder_width / 100.0
            camera_matrix = np.array([[w,0,w/2],[0,w,h/2],[0,0,1]],dtype=np.float32)
            dist_coeffs = np.zeros((4,1))

            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )

            if success:
                rot_mat,_ = cv2.Rodrigues(rotation_vector)
                forward_3d = rot_mat[:,2]

                # Clamp rotation to max per frame
                if prev_forward_3d is not None:
                    forward_3d = clamp_rotation(prev_forward_3d, forward_3d, MAX_GAZE_ROT)

                # Smooth 3D vector
                if prev_forward_3d is not None:
                    forward_3d = lerp(prev_forward_3d, forward_3d, GAZE_ALPHA_3D)
                prev_forward_3d = forward_3d

                gaze_vec = unit(forward_3d[:2])
                row["gaze_dir_x"] = float(gaze_vec[0])
                row["gaze_dir_y"] = float(gaze_vec[1])

                eye_mid = (L(33)+L(263))/2
                draw_cone(frame, eye_mid, gaze_vec, GAZE_LENGTH,
                          GAZE_CONE_RAD*(1-GAZE_BINOCULAR_FACTOR),(0,255,255))

                for idx in [1,33,263,61,291,152]:
                    cv2.circle(frame, tuple(L(idx).astype(int)), 3, (0,255,255), -1)

                if body_mask is not None:
                    for d in range(0,GAZE_LENGTH,10):
                        p = (eye_mid + gaze_vec*d).astype(int)
                        if 0<=p[0]<w and 0<=p[1]<h and body_mask[p[1],p[0]]:
                            row["gaze_on_body"]=1
                            break

    # ---------------- WRITE ----------------
    csvwriter.writerow(row)
    writer.write(frame)
    frame_idx+=1

# -------------------------
# CLEANUP
# -------------------------
cap.release()
writer.release()
hands_detector.close()
csvfile.close()
print("Finished.")
