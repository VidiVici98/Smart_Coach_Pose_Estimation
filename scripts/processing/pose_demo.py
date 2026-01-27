import cv2
import csv
import math
import mediapipe as mp

# ===============================
# MediaPipe Tasks API imports
# ===============================
BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode

PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions

HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

# ===============================
# Model paths
# ===============================
POSE_MODEL = "data/models/pose_landmarker_full.task"
HAND_MODEL = "data/models/hand_landmarker.task"

# ===============================
# Display
# ===============================
WINDOW_NAME = "mediapipe pose and hand landmarker"
DISPLAY_SCALE =  1.0
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

# ===============================
# Pose skeleton
# ===============================
POSE_CONNECTIONS = [
    # Face
    (0,1),(1,2),(2,3),(3,7),
    (0,4),(4,5),(5,6),(6,8),
    (9,10),

    # Head to torso
    (0,11),(0,12),

    # Torso
    (11,12),
    (11,23),(12,24),
    (23,24),

    # Arms
    (11,13),(13,15),
    (12,14),(14,16),

    # Hands anchors
    (15,17),(15,19),(15,21),
    (16,18),(16,20),(16,22),

    # Legs
    (23,25),(25,27),
    (24,26),(26,28),
    (27,29),(29,31),
    (28,30),(30,32),
]

# ===============================
# Hand skeleton
# ===============================
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20)
]

VIS_THRESH = 0.5

# ===============================
# Utility helpers
# ===============================
def lm_valid(lm):
    return (
        lm.visibility >= VIS_THRESH and
        0.0 <= lm.x <= 1.0 and
        0.0 <= lm.y <= 1.0
    )

# one-frame temporal memory
prev_pose_pts = {}

# ===============================
# Landmarkers
# ===============================
pose = PoseLandmarker.create_from_options(
    PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=POSE_MODEL),
        running_mode=VisionRunningMode.VIDEO
    )
)

hands = HandLandmarker.create_from_options(
    HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=HAND_MODEL),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=2
    )
)

# ===============================
# Video
# ===============================
cap = cv2.VideoCapture("videos/test_video.mp4")
frame_num = 0

with open("data/pose_hand_landmarks.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "frame","person_id","type","id","x","y","z"
    ])

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(mp.ImageFormat.SRGB, rgb)
        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        pose_result = pose.detect_for_video(mp_image, timestamp)
        hand_result = hands.detect_for_video(mp_image, timestamp)

        wrists = {}

        # ===============================
        # Pose
        # ===============================
        if pose_result.pose_landmarks:
            for pid, lms in enumerate(pose_result.pose_landmarks):
                pts = []

                for i, lm in enumerate(lms):
                    if not lm_valid(lm):
                        pts.append(None)
                        continue

                    x = int(lm.x * w)
                    y = int(lm.y * h)

                    # temporal smoothing
                    key = (pid, i)
                    if key in prev_pose_pts:
                        px, py = prev_pose_pts[key]
                        x = int(0.7 * px + 0.3 * x)
                        y = int(0.7 * py + 0.3 * y)

                    prev_pose_pts[key] = (x, y)
                    pts.append((x, y))

                    writer.writerow([frame_num, pid, "pose", i, lm.x, lm.y, lm.z])
                    cv2.circle(frame, (x, y), 3, (255, 255, 0), -1)

                # wrist anchors only if valid
                wrists[pid] = {
                    "L": pts[15] if pts[15] else None,
                    "R": pts[16] if pts[16] else None
                }

                for a, b in POSE_CONNECTIONS:
                    if pts[a] is None or pts[b] is None:
                        continue
                    cv2.line(frame, pts[a], pts[b], (0, 255, 255), 2)

        # ===============================
        # Hands
        # ===============================
        if hand_result.hand_landmarks:
            for hid, hand in enumerate(hand_result.hand_landmarks):
                pts = []
                for lm in hand:
                    if not (0.0 <= lm.x <= 1.0 and 0.0 <= lm.y <= 1.0):
                        pts.append(None)
                        continue
                    x, y = int(lm.x * w), int(lm.y * h)
                    pts.append((x, y))

                valid_pts = [p for p in pts if p]
                if not valid_pts:
                    continue

                cx = sum(p[0] for p in valid_pts) / len(valid_pts)
                cy = sum(p[1] for p in valid_pts) / len(valid_pts)

                assigned = None
                min_d = 1e9

                for pid, ws in wrists.items():
                    for side, wpt in ws.items():
                        if wpt is None:
                            continue
                        d = math.hypot(cx - wpt[0], cy - wpt[1])
                        if d < min_d:
                            min_d = d
                            assigned = (pid, side)

                pid, side = assigned if assigned else (-1, "U")

                for i, lm in enumerate(hand):
                    writer.writerow([frame_num, pid, f"hand_{side}", i, lm.x, lm.y, lm.z])

                for a, b in HAND_CONNECTIONS:
                    if pts[a] is None or pts[b] is None:
                        continue
                    cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)

                for p in valid_pts:
                    cv2.circle(frame, p, 2, (0, 200, 0), -1)

        display = cv2.resize(frame, None, fx=DISPLAY_SCALE, fy=DISPLAY_SCALE)
        cv2.imshow(WINDOW_NAME, display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        frame_num += 1

cap.release()
cv2.destroyAllWindows()
pose.close()
hands.close()
