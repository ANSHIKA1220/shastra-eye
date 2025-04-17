
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Dropout, LSTM, TimeDistributed
from tensorflow.keras.utils import to_categorical
import warnings
warnings.filterwarnings("ignore")

# -------------------- Load Data --------------------
def load_dataset(dataset_path=r"C:\Users\lenovo\CNN-LSTM-Violence-detection\Video_Frame", sequence_length=16, image_shape=(64, 64, 3)):
    print("🔄 Loading data...")
    classes = os.listdir(dataset_path)
    all_sequences = []
    all_labels = []

    for class_index, class_name in enumerate(classes):
        class_dir = os.path.join(dataset_path, class_name)
        video_folders = os.listdir(class_dir)
        for video_folder in video_folders:
            video_path = os.path.join(class_dir, video_folder)
            frames = sorted(os.listdir(video_path))
            if len(frames) < sequence_length:
                continue

            sequence = []
            for i in range(sequence_length):
                frame_path = os.path.join(video_path, frames[i])
                image = tf.keras.preprocessing.image.load_img(frame_path, target_size=image_shape[:2])
                image = tf.keras.preprocessing.image.img_to_array(image) / 255.0
                sequence.append(image)
            all_sequences.append(sequence)
            all_labels.append(class_index)

    X = np.array(all_sequences)
    y = to_categorical(all_labels)
    print(f"✅ Classes found in dataset: {classes}")
    print(f"✅ Total videos loaded: {len(X)}")
    return X, y, classes

# -------------------- Build Model --------------------
def build_model(sequence_length=16, image_shape=(64, 64, 3), num_classes=2):
    input_layer = Input(shape=(sequence_length, *image_shape))

    cnn = TimeDistributed(Conv2D(32, (3,3), activation='relu'))(input_layer)
    cnn = TimeDistributed(MaxPooling2D((2,2)))(cnn)
    cnn = TimeDistributed(Conv2D(64, (3,3), activation='relu'))(cnn)
    cnn = TimeDistributed(MaxPooling2D((2,2)))(cnn)
    cnn = TimeDistributed(Conv2D(128, (3,3), activation='relu'))(cnn)
    cnn = TimeDistributed(MaxPooling2D((2,2)))(cnn)
    cnn = TimeDistributed(Flatten())(cnn)

    rnn = LSTM(64)(cnn)
    dropout = Dropout(0.5)(rnn)
    dense1 = Dense(64, activation='relu')(dropout)
    output = Dense(num_classes, activation='softmax')(dense1)

    model = Model(inputs=input_layer, outputs=output)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.summary()
    return model

# -------------------- Main Script --------------------
if __name__ == '__main__':
    # Load dataset
    X, y, class_names = load_dataset()

    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

    # Build model
    model = build_model(sequence_length=16, image_shape=(64, 64, 3), num_classes=len(class_names))

    print("🚀 Training started...")
    history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, batch_size=8)

    # Save the model
    model.save("violence_detection_model.h5")

    # Evaluate
    print("🔍 Evaluating...")
    loss, acc = model.evaluate(X_test, y_test)
    print(f"✅ Test Accuracy: {acc * 100:.2f}%")

    # Predict and show classification report
    y_pred = model.predict(X_test)
    y_pred_labels = np.argmax(y_pred, axis=1)
    y_true_labels = np.argmax(y_test, axis=1)

    print("📊 Classification Report:")
    print(classification_report(y_true_labels, y_pred_labels, target_names=class_names, zero_division=1))
