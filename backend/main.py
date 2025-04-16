from fastapi import FastAPI, UploadFile, WebSocket, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import cv2
import base64
import numpy as np
from typing import List
from models.weapon_detector import WeaponDetector
from models.fight_detector import FightDetector
from models.theft_detector import TheftDetector
from utils.alert_manager import send_alert
from utils.firebase_logger import log_event, get_recent_logs
import os

app = FastAPI()
security = HTTPBasic()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load detectors
weapon_detector = WeaponDetector()
fight_detector = FightDetector()
theft_detector = TheftDetector()

# Data model for alerting
class FrameInput(BaseModel):
    image_base64: str

# Optional: Authentication (for simplicity, hardcoded)
USERS = {"admin": os.getenv("ADMIN_PASSWORD", "password123")}

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_pw = USERS.get(credentials.username)
    if not correct_pw or correct_pw != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return credentials.username

@app.post("/detect")
async def detect_threat(input_data: FrameInput):
    try:
        img_data = base64.b64decode(input_data.image_base64)
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        result = {
            "weapon": weapon_detector.detect(frame),
            "fight": fight_detector.detect(frame),
            "theft": theft_detector.detect(frame)
        }

        threats = [k for k, v in result.items() if v]

        if threats:
            log_event(threats)
            send_alert(threats)

        return JSONResponse({"threats_detected": threats})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
def root():
    return {"message": "Threat Detection API is running"}

@app.get("/alerts/logs")
async def get_logs():
    try:
        logs = get_recent_logs(limit=10)
        return logs
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.websocket("/video/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            result = {
                "weapon": weapon_detector.detect(frame),
                "fight": fight_detector.detect(frame),
                "theft": theft_detector.detect(frame)
            }

            threats = [k for k, v in result.items() if v]
            if threats:
                log_event(threats)
                send_alert(threats)

            frame_resized = cv2.resize(frame, (640, 480))
            _, buffer = cv2.imencode('.jpg', frame_resized)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            await websocket.send_json({
                "image": frame_base64,
                "threats": threats
            })

    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        cap.release()
        await websocket.close()

# Deployment startup for Render or Railway
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
