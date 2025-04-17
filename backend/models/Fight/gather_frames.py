import os
import shutil

def gather_images(src_root, dst_folder):
    for root, dirs, files in os.walk(src_root):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                src_path = os.path.join(root, file)
                dst_path = os.path.join(dst_folder, file)
                # Handle duplicates by renaming if needed
                count = 1
                while os.path.exists(dst_path):
                    name, ext = os.path.splitext(file)
                    dst_path = os.path.join(dst_folder, f"{name}_{count}{ext}")
                    count += 1
                shutil.copy2(src_path, dst_path)

# Replace with your actual dataset paths
gather_images(r"C:\Users\lenovo\CNN-LSTM-Violence-detection\ExtractedFrames\Dataset1\Fights", r"C:\Users\lenovo\CNN-LSTM-Violence-detection\frames\Fights")
gather_images(r"C:\Users\lenovo\CNN-LSTM-Violence-detection\ExtractedFrames\Dataset1\NoFights", r"C:\Users\lenovo\CNN-LSTM-Violence-detection\frames\NoFights")
gather_images(r"C:\Users\lenovo\CNN-LSTM-Violence-detection\ExtractedFrames\Dataset2\Fights", r"C:\Users\lenovo\CNN-LSTM-Violence-detection\frames\Fights")
gather_images(r"C:\Users\lenovo\CNN-LSTM-Violence-detection\ExtractedFrames\Dataset2\NoFights", r"C:\Users\lenovo\CNN-LSTM-Violence-detection\frames\NoFights")
gather_images(r"C:\Users\lenovo\CNN-LSTM-Violence-detection\ExtractedFrames\Dataset3\Fights", r"C:\Users\lenovo\CNN-LSTM-Violence-detection\frames\Fights")
gather_images(r"C:\Users\lenovo\CNN-LSTM-Violence-detection\ExtractedFrames\Dataset3\NoFights", r"C:\Users\lenovo\CNN-LSTM-Violence-detection\frames\NoFights")

