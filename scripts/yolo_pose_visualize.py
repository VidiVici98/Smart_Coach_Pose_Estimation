import cv2
from ultralytics import YOLO

# ===============================
# Config
# ===============================
VIDEO_PATH = "videos/test_video.mp4"
MODEL_NAME = "yolov8m-pose.pt"

IMG_SIZE = 960
CONF_THRES = 0.25
IOU_THRES = 0.65
MAX_DET = 1

WINDOW = "YOLOv8 Pose"

# COCO keypoint skeleton
SKELETON = [
    (5, 7), (7, 9),        # left arm
    (6, 8), (8, 10),       # right arm
    (5, 6),                # shoulders
    (5, 11), (6, 12),      # torso
    (11, 12),
    (11, 13), (13, 15),    # left leg
    (12, 14), (14, 16)     # right leg
]

CONF_PRESENT = 0.35

# ===============================
# Load model
# ===============================
model = YOLO(MODEL_NAME)

cap = cv2.VideoCapture(VIDEO_PATH)
cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(
        frame,
        imgsz=IMG_SIZE,
        conf=CONF_THRES,
        iou=IOU_THRES,
        max_det=MAX_DET,
        verbose=False
    )[0]

    if results.keypoints is not None:
        kps = results.keypoints.data[0]  # single person (17,3)

        pts = {}
        for i, (x, y, c) in enumerate(kps):
            if c >= CONF_PRESENT:
                px, py = int(x), int(y)
                pts[i] = (px, py)
                cv2.circle(frame, (px, py), 4, (0, 255, 255), -1)

        # draw skeleton only if BOTH endpoints exist
        for a, b in SKELETON:
            if a in pts and b in pts:
                cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)

    cv2.imshow(WINDOW, frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
