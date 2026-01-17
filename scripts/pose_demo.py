import cv2
import csv
import mediapipe as mp

# ===============================
# MediaPipe Tasks API imports
# ===============================
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# ===============================
# Pose model path
# ===============================
MODEL_PATH = "models/pose_landmarker_lite.task"

# ===============================
# Canonical pose skeleton
# (33-landmark MediaPipe pose)
# ===============================
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),

    (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16),

    (15, 17), (15, 19), (15, 21),
    (16, 18), (16, 20), (16, 22),

    (11, 23), (12, 24),
    (23, 24),

    (23, 25), (25, 27),
    (24, 26), (26, 28),

    (27, 29), (29, 31),
    (28, 30), (30, 32),
]

VISIBILITY_THRESHOLD = 0.5

# ===============================
# Landmarker setup
# ===============================
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO
)

landmarker = PoseLandmarker.create_from_options(options)

# ===============================
# Video input
# ===============================
cap = cv2.VideoCapture("videos/test_video.mp4")
frame_num = 0

# ===============================
# CSV output
# ===============================
with open("data/joint_coordinates.csv", "w", newline="") as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow([
        "frame",
        "person_id",
        "joint_index",
        "x",
        "y",
        "z",
        "visibility"
    ])

    # ===============================
    # Main loop
    # ===============================
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # IMPORTANT: timestamp must be monotonically increasing
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        if result.pose_landmarks:
            for person_id, person_landmarks in enumerate(result.pose_landmarks):

                # Convert landmarks to pixel coordinates once
                points = []
                for lm in person_landmarks:
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    points.append((px, py))

                # -------------------------------
                # Draw skeleton
                # -------------------------------
                for start_idx, end_idx in POSE_CONNECTIONS:
                    lm_start = person_landmarks[start_idx]
                    lm_end = person_landmarks[end_idx]

                    if lm_start.visibility < VISIBILITY_THRESHOLD:
                        continue
                    if lm_end.visibility < VISIBILITY_THRESHOLD:
                        continue

                    cv2.line(
                        frame,
                        points[start_idx],
                        points[end_idx],
                        (0, 255, 255),
                        2
                    )

                # -------------------------------
                # Save & draw joints
                # -------------------------------
                for idx, lm in enumerate(person_landmarks):
                    csvwriter.writerow([
                        frame_num,
                        person_id,
                        idx,
                        lm.x,
                        lm.y,
                        lm.z,
                        lm.visibility
                    ])

                    if lm.visibility < VISIBILITY_THRESHOLD:
                        continue

                    cv2.circle(
                        frame,
                        points[idx],
                        4,
                        (0, 255, 0),
                        -1
                    )

        cv2.imshow("Pose", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        frame_num += 1

# ===============================
# Cleanup
# ===============================
cap.release()
cv2.destroyAllWindows()
landmarker.close()
