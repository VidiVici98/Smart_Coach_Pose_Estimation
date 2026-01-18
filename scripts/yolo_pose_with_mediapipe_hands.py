import cv2
import csv
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
from scripts.pose_demo import HAND_CONNECTIONS, BaseOptions

# ===============================
# Config
# ===============================
VIDEO_PATH = "videos/test_video.mp4"
POSE_MODEL = "yolov8m-pose.pt"
HAND_MODEL = "models/hand_landmarker.task"

WINDOW = "YOLO Pose + Wrist-Gated Hands"
IMG_SIZE = 960
CONF_THRES = 0.25
IOU_THRES = 0.65
MAX_DET = 1

WRIST_CONF = 0.4
HAND_CROP_SIZE = 220

# YOLO Pose Skeleton (COCO-17)
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

# CSV Output
csv_file = open("data/yolo_pose_hands.csv", "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["frame", "type", "id", "x", "y", "confidence"])

frame_num = 0

# ===============================
# Temporal smoothing storage
# ===============================
prev_pose_pts = {}  # key = keypoint index, value = (x, y)

# ===============================
# Main Loop
# ===============================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # YOLO Pose Detection
    results = pose_model(
        frame,
        imgsz=IMG_SIZE,
        conf=CONF_THRES,
        iou=IOU_THRES,
        max_det=MAX_DET,
        verbose=False
    )[0]

    wrists = []

    if results.keypoints is not None:
        kps = results.keypoints.data[0]
        pts = {}

        for i, (x, y, c) in enumerate(kps):
            if c < CONF_THRES:
                continue

            px, py = int(x), int(y)

            # Temporal smoothing
            if i in prev_pose_pts:
                px = int(0.7 * prev_pose_pts[i][0] + 0.3 * px)
                py = int(0.7 * prev_pose_pts[i][1] + 0.3 * py)
            prev_pose_pts[i] = (px, py)

            pts[i] = (px, py)

            # Confidence-based radius
            radius = max(2, int(4 * c))
            alpha = min(1.0, max(0.3, c))
            cv2.circle(frame, (px, py), radius, (0, int(255*alpha), 255), -1)

            writer.writerow([frame_num, "pose", i, px, py, float(c)])

        # Draw skeleton lines
        for a, b in POSE_SKELETON:
            if a in pts and b in pts:
                cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)

        # Record wrists for hand gating
        if 9 in pts and kps[9][2] >= WRIST_CONF:
            wrists.append(("L", pts[9]))
        if 10 in pts and kps[10][2] >= WRIST_CONF:
            wrists.append(("R", pts[10]))

    # ===============================
    # Wrist-Gated Hand Detection
    # ===============================
    for side, (wx, wy) in wrists:
        half = HAND_CROP_SIZE // 2
        x1 = max(wx - half, 0)
        y1 = max(wy - half, 0)
        x2 = min(wx + half, w)
        y2 = min(wy + half, h)

        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_crop)
        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        hand_result = hand_landmarker.detect_for_video(mp_image, timestamp)
        if not hand_result.hand_landmarks:
            continue

        hand = hand_result.hand_landmarks[0]
        pts_hand = []

        for i, lm in enumerate(hand):
            px = int(x1 + lm.x * (x2 - x1))
            py = int(y1 + lm.y * (y2 - y1))
            pts_hand.append((px, py))
            cv2.circle(frame, (px, py), 3, (255, 0, 0), -1)
            writer.writerow([frame_num, f"hand_{side}", i, px, py, lm.z])

        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts_hand[a], pts_hand[b], (255, 0, 0), 2)

        # Optional: draw crop box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 1)

    # Display
    cv2.imshow(WINDOW, frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    frame_num += 1

# ===============================
# Cleanup
# ===============================
csv_file.close()
cap.release()
cv2.destroyAllWindows()
hand_landmarker.close()
