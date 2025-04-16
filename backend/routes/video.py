from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse
import cv2
import base64
import asyncio
import json
from models.weapon_detector import WeaponDetector
from models.fight_detector import FightDetector
from models.theft_detector import TheftDetector
from utils.alert_manager import send_alert
from utils.firebase_logger import log_event

router = APIRouter()

weapon_detector = WeaponDetector()
fight_detector = FightDetector()
theft_detector = TheftDetector()

html = """
<!DOCTYPE html>
<html>
    <head><title>Video Stream</title></head>
    <body>
        <h1>Video Stream</h1>
        <img id="video" width="640" height="480">
        <script>
            var ws = new WebSocket("ws://localhost:8000/video/ws");
            ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                document.getElementById("video").src = "data:image/jpeg;base64," + data.image;
            };
        </script>
    </body>
</html>
"""

@router.get("/")
async def get():
    return HTMLResponse(html)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(1)  # Changed to 1, test 0, 1, or other indices
    if not cap.isOpened():
        print("Error: Could not open video capture. Check device index (0, 1, etc.).")
        await websocket.close()
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break

            # Dummy detection
            result = {
                "weapon": weapon_detector.detect(frame),
                "fight": fight_detector.detect(frame),
                "theft": theft_detector.detect(frame)
            }
            threats = [k for k, v in result.items() if v]

            if threats:
                log_event(threats)
                send_alert(threats)

            # Encode frame
            _, buffer = cv2.imencode(".jpg", frame)
            frame_base64 = base64.b64encode(buffer).decode("utf-8")

            # Send data
            await websocket.send_text(json.dumps({"image": frame_base64, "threats": threats}))

            await asyncio.sleep(0.1)  # Control frame rate
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        cap.release()
        await websocket.close()