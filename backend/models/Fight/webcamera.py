import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from collections import deque

# Load the trained model
model = load_model(r"C:\Users\lenovo\CNN-LSTM-Violence-detection\violence_detection_model.h5")  # or "your_model_name.keras" if you saved it that way

# Define labels
labels = ['Fights', 'NoFights']

# Set frame size and sequence length
IMG_SIZE = 64
SEQ_LENGTH = 16

# Initialize webcam
cap = cv2.VideoCapture(0)
frames = deque(maxlen=SEQ_LENGTH)

print("📷 Starting real-time violence detection... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Resize and preprocess
    resized_frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    normalized_frame = resized_frame.astype("float32") / 255.0
    frames.append(normalized_frame)

    # Prediction only when we have 16 frames
    if len(frames) == SEQ_LENGTH:
        input_frames = np.array(frames).reshape(1, SEQ_LENGTH, IMG_SIZE, IMG_SIZE, 3)
        prediction = model.predict(input_frames, verbose=0)
        label = labels[np.argmax(prediction)]

        # Add label to frame
        color = (0, 255, 0) if label == "NoFights" else (0, 0, 255)
        cv2.putText(frame, f"Prediction: {label}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.rectangle(frame, (5, 5), (frame.shape[1]-5, frame.shape[0]-5), color, 2)

    # Show frame
    cv2.imshow("Violence Detection (Press 'q' to quit)", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("👋 Exiting...")
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
