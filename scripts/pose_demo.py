import cv2
import csv
import mediapipe as mp

# Task API imports
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = "models/pose_landmarker_lite.task"

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO
)

landmarker = PoseLandmarker.create_from_options(options)

cap = cv2.VideoCapture("videos/test_video.mp4")
frame_num = 0

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

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # IMPORTANT: timestamp must be monotonically increasing
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        # Save landmarks
        if result.pose_landmarks:
            for person_id, person_landmarks in enumerate(result.pose_landmarks):
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

                    # Draw landmark
                    px = int(lm.x * frame.shape[1])
                    py = int(lm.y * frame.shape[0])
                    cv2.circle(frame, (px, py), 4, (0, 255, 0), -1)

        cv2.imshow("Pose", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        frame_num += 1

cap.release()
cv2.destroyAllWindows()
landmarker.close()

