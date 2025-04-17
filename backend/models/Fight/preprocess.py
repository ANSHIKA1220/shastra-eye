import numpy as np
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

# Define path to frames directory
DATASET_PATH = r"C:\Users\lenovo\CNN-LSTM-Violence-detection\frames"

# Parameters
IMG_HEIGHT, IMG_WIDTH = 64, 64
BATCH_SIZE = 32

# Initialize ImageDataGenerator
datagen = ImageDataGenerator(rescale=1.0 / 255)

generator = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

# Load all images and labels
X, Y = [], []

print("Loading images and labels...")

for i in range(len(generator)):
    x_batch, y_batch = next(generator)
    X.extend(x_batch)
    Y.extend(y_batch)


X = np.array(X)
Y = np.array(Y)

# Save arrays
print("Saving X.npy and Y.npy...")
np.save("X.npy", X)
np.save("Y.npy", Y)
print("Done.")
