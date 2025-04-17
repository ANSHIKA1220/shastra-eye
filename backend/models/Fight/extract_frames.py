import cv2
import os

# Path to all datasets
dataset_base_path = r"C:\Users\lenovo\CNN-LSTM-Violence-detection\Dataset"
output_base_path = r"C:\Users\lenovo\CNN-LSTM-Violence-detection\ExtractedFrames"

# Function to extract frames from a video
def extract_frames(video_path, output_folder, frame_rate=5):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return
    
    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_rate == 0:
            frame_name = os.path.join(output_folder, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_name, frame)
            saved_count += 1

        frame_count += 1

    cap.release()

# Loop over all three datasets
for dataset in ['Dataset1', 'Dataset2', 'Dataset3']:
    for category in ['Fights', 'NoFights']:
        input_folder = os.path.join(dataset_base_path, dataset, category)
        output_folder = os.path.join(output_base_path, dataset, category)

        os.makedirs(output_folder, exist_ok=True)

        for video_file in os.listdir(input_folder):
            if video_file.endswith(('.mp4', '.avi', '.mov')):
                video_path = os.path.join(input_folder, video_file)
                video_output_folder = os.path.join(output_folder, os.path.splitext(video_file)[0])
                os.makedirs(video_output_folder, exist_ok=True)
                print(f"Extracting: {video_path}")
                extract_frames(video_path, video_output_folder)
