# models/theft_detector.pyimport cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import mediapipe as mp
import time
import logging
import warnings
import absl.logging
import os

# Suppress TensorFlow Lite warnings
warnings.filterwarnings("ignore", category=UserWarning)
absl.logging.set_verbosity(absl.logging.ERROR)

# Configuration settings
CONFIG = {
    "yolo_model": "yolov8n.pt",  # YOLOv8 nano for speed
    "confidence_threshold": 0.5,  # Detection confidence threshold
    "tracked_classes": [0, 24, 26, 28],  # person, backpack, bottle, cup
    "proximity_threshold": 100,  # Pixel distance for person-object proximity
    "alert_cooldown": 5,  # Seconds between alerts
    "output_video": "output_theft_detection.mp4",  # Output video file
    "log_file": "theft_alerts.log"  # Log file for alerts
}

# Setup logging
logging.basicConfig(filename=CONFIG["log_file"], level=logging.INFO, 
                    format="%(asctime)s - %(message)s")

# Prompt for video source
def get_video_source():
    print("Enter video source (path to video file, or '0' for webcam):")
    source = input().strip()
    if source.lower() == '0':
        return 0
    if os.path.isfile(source):
        return source
    print(f"Error: File '{source}' does not exist.")
    return get_video_source()  # Retry if invalid

CONFIG["video_source"] = get_video_source()

# Initialize models
try:
    model = YOLO(CONFIG["yolo_model"])
    tracker = DeepSort(max_age=30, nn_budget=100)
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
except Exception as e:
    print(f"Error initializing models: {e}")
    exit()

# Video capture
cap = cv2.VideoCapture(CONFIG["video_source"])
if not cap.isOpened():
    print(f"Error: Could not open video source '{CONFIG['video_source']}'. "
          "Ensure the file exists or webcam is connected.")
    exit()

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30

# Setup video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(CONFIG["output_video"], fourcc, fps, (frame_width, frame_height))

# Store object states
object_locations = {}  # Track objects: {track_id: last_position}
theft_alerts = []  # Log potential thefts
frame_count = 0
last_alert_time = 0
start_time = time.time()

def is_running(pose_landmarks, frame_height):
    """Check if person is running based on pose (simplified heuristic)."""
    if not pose_landmarks:
        return False
    knee_left = pose_landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y
    knee_right = pose_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y
    return abs(knee_left - knee_right) > frame_height * 0.1

def check_theft(detections, tracks, pose_results, frame, frame_height):
    """Check for theft-like behavior."""
    global last_alert_time, frame_count
    current_time = time.time()

    # Update object locations
    for track in tracks:
        if not track.is_confirmed():
            continue
        track_id = track.track_id
        cls_id = track.det_class if hasattr(track, 'det_class') else 0
        if cls_id != 0:  # Non-person objects
            ltrb = track.to_ltrb()
            object_locations[track_id] = {"position": ltrb, "last_seen": frame_count, "class": cls_id}

    # Check for disappeared objects
    disappeared = [oid for oid in list(object_locations) 
                   if oid not in [t.track_id for t in tracks] 
                   and frame_count - object_locations[oid]["last_seen"] > fps]
    for oid in disappeared:
        for track in tracks:
            if not track.is_confirmed() or track.det_class != 0:
                continue
            person_ltrb = track.to_ltrb()
            obj_ltrb = object_locations[oid]["position"]
            distance = np.sqrt((person_ltrb[0] - obj_ltrb[0])**2 + (person_ltrb[1] - obj_ltrb[1])**2)
            if distance < CONFIG["proximity_threshold"]:
                pose_landmarks = pose_results.pose_landmarks.landmark if pose_results.pose_landmarks else None
                if is_running(pose_landmarks, frame_height):
                    if current_time - last_alert_time > CONFIG["alert_cooldown"]:
                        alert = (f"Theft Alert: Object ID {oid} ({model.names[object_locations[oid].get('class', 0)]}) "
                                 f"taken by Person ID {track.track_id} at frame {frame_count}")
                        theft_alerts.append(alert)
                        logging.info(alert)
                        print(alert)
                        last_alert_time = current_time
        del object_locations[oid]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1

    # YOLOv8 detection
    try:
        results = model(frame, conf=CONFIG["confidence_threshold"])
        detections = []
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            for box, score, cls in zip(boxes, scores, classes):
                if cls in CONFIG["tracked_classes"]:
                    x1, y1, x2, y2 = box
                    w, h = x2 - x1, y2 - y1
                    detections.append(([x1, y1, w, h], score, int(cls)))
    except Exception as e:
        print(f"Error in YOLO detection: {e}")
        continue

    # Update Deep SORT tracker
    tracks = tracker.update_tracks(detections, frame=frame)

    # Pose estimation with MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_results = pose.process(frame_rgb)

    # Check for theft
    check_theft(detections, tracks, pose_results, frame, frame_height)

    # Draw tracks
    for track in tracks:
        if not track.is_confirmed():
            continue
        track_id = track.track_id
        ltrb = track.to_ltrb()
        x1, y1, x2, y2 = map(int, ltrb)
        cls_id = track.det_class if hasattr(track, 'det_class') else 0
        label = f"ID {track_id} {model.names[cls_id]}"
        color = (0, 255, 0) if cls_id == 0 else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Draw pose landmarks
    if pose_results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(
            frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Display alert status and FPS
    status = "Suspicious" if theft_alerts and (time.time() - last_alert_time) < CONFIG["alert_cooldown"] else "Normal"
    status_color = (0, 0, 255) if status == "Suspicious" else (0, 255, 0)
    cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
    
    elapsed_time = time.time() - start_time
    current_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
    cv2.putText(frame, f"FPS: {current_fps:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Write frame to output video
    out.write(frame)

    # Show frame
    cv2.imshow("Theft Detection System", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup
cap.release()
out.release()
cv2.destroyAllWindows()
pose.close()

# Save alerts to log file
with open(CONFIG["log_file"], "a") as f:
    for alert in theft_alerts:
        f.write(f"{alert}\n")

print(f"Processing complete. Output saved to {CONFIG['output_video']} and logs to {CONFIG['log_file']}.")
