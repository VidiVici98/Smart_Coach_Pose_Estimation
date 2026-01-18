import cv2
import csv
from ultralytics import YOLO

# ===============================
# Configuration (LOCK THESE IN)
# ===============================
VIDEO_PATH = "videos/test_video.mp4"
OUTPUT_CSV = "data/yolo_pose_landmarks.csv"

MODEL_NAME = "yolov8m-pose.pt"   # start here, not nano
IMG_SIZE = 960                   # critical for limb correctness
CONF_THRES = 0.25
IOU_THRES = 0.65
MAX_DET = 1                      # single shooter

# visibility tiers
CONF_PRESENT = 0.35
CONF_WEAK = 0.15

# ===============================
# Load model
# ===============================
model = YOLO(MODEL_NAME)

# ===============================
# Video
# ===============================
cap = cv2.VideoCapture(VIDEO_PATH)
frame_idx = 0

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "frame",
        "person_id",
        "kp_id",
        "x_px",
        "y_px",
        "confidence",
        "state"
    ])

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]

        # ===============================
        # YOLO inference (OFFLINE SAFE)
        # ===============================
        results = model(
            frame,
            imgsz=IMG_SIZE,
            conf=CONF_THRES,
            iou=IOU_THRES,
            max_det=MAX_DET,
            verbose=False
        )[0]

        if results.keypoints is None:
            frame_idx += 1
            continue

        kps = results.keypoints.data  # shape: (persons, 17, 3)

        for pid, person in enumerate(kps):
            for kp_id, (x, y, c) in enumerate(person):
                x_px = int(x.item())
                y_px = int(y.item())
                conf = float(c.item())

                if conf >= CONF_PRESENT:
                    state = "PRESENT"
                elif conf >= CONF_WEAK:
                    state = "WEAK"
                else:
                    state = "ABSENT"

                writer.writerow([
                    frame_idx,
                    pid,
                    kp_id,
                    x_px,
                    y_px,
                    round(conf, 4),
                    state
                ])

        frame_idx += 1

cap.release()
print("YOLO pose extraction complete.")
