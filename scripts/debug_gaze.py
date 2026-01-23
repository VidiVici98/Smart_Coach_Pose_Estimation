import os
import sys
os.environ["PYTORCH_NO_NNPACK"] = "1"
os.environ["TORCH_CPP_LOG_LEVEL"] = "ERROR"

class SuppressStdErr:
    def __enter__(self):
        self._old_stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._old_stderr

with SuppressStdErr():
    import cv2
    import numpy as np
    from ultralytics import YOLO
    import mediapipe as mp

# Load models
print("Loading models...")
with SuppressStdErr():
    pose_model = YOLO("models/yolov8m-pose.pt")
    face_model = YOLO("models/yolov8n-face.pt")
    mp_face = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True,
        refine_landmarks=True,
        max_num_faces=1
    )

# Open video
cap = cv2.VideoCapture("input/test_video.mp4")
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

CONF_THRES = 0.15
frame_count = 0
eye_left_found = 0
eye_right_found = 0
both_found = 0

print("Processing frames...")
while cap.isOpened() and frame_count < 10:  # Just process first 10 frames
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Get face
    face_results = face_model(frame, conf=CONF_THRES, max_det=1)[0]
    
    if len(face_results.boxes.xyxy) > 0:
        x1, y1, x2, y2 = map(int, face_results.boxes.xyxy[0])
        face_crop = rgb[y1:y2, x1:x2]
        mp_results = mp_face.process(face_crop)
        
        print(f"Frame {frame_count}: YOLO face box: ({x1},{y1},{x2},{y2}). MediaPipe landmarks: {mp_results.multi_face_landmarks is not None}")
        
        if mp_results.multi_face_landmarks:
            lm = mp_results.multi_face_landmarks[0].landmark
            
            def L(i):
                lm_i = lm[i]
                # MediaPipe face mesh landmarks don't have reliable visibility when cropped
                # Simply accept all landmarks
                return np.array([lm_i.x * (x2 - x1) + x1,
                                lm_i.y * (y2 - y1) + y1], dtype=np.float32)
            
            print(f"\nFrame {frame_count}:")
            eye_left = L(33)
            eye_right = L(263)
            
            if eye_left is not None:
                eye_left_found += 1
            if eye_right is not None:
                eye_right_found += 1
            if eye_left is not None and eye_right is not None:
                both_found += 1
                print(f"  -> Both eyes available!")

cap.release()

print(f"\n=== Summary ===")
print(f"Frames processed: {frame_count}")
print(f"Eye left found: {eye_left_found}")
print(f"Eye right found: {eye_right_found}")
print(f"Both eyes found: {both_found}")
