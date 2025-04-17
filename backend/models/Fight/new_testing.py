import cv2
import numpy as np
from tensorflow.keras.models import load_model
from collections import deque

# Load model
model = load_model(r"C:\Users\lenovo\CNN-LSTM-Violence-detection\violence_detection_model.h5")

# Initialize deque for 16-frame window
frames = deque(maxlen=16)

# Load video
cap = cv2.VideoCapture(r"C:\Users\lenovo\CNN-LSTM-Violence-detection\Dataset\Dataset3\NoFights\NV_8.mp4")

# Labels
labels = ["NoFight", "Fight"]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    resized_frame = cv2.resize(frame, (64, 64))
    normalized_frame = resized_frame.astype("float32") / 255.0
    frames.append(normalized_frame)

    if len(frames) == 16:
        input_seq = np.expand_dims(frames, axis=0)
        prediction = model.predict(input_seq)[0]
        print("Raw Prediction:", prediction)  # DEBUG LINE
        label = labels[np.argmax(prediction)]
        confidence = np.max(prediction)
        text = f"{label} ({confidence:.2f})"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Fight Detection Test", frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
