# Threat Detection System

A real-time system for detecting weapons, fights, and theft using AI models, with SMS alerts and a React dashboard.

## Setup

1. **Clone the repo**:
   ```bash
   git clone <repo-url>
   cd threat-detection-system
   ```

2. **Backend Setup**:
   - Install Python 3.10+.
   - Create a virtual environment: `python -m venv venv`.
   - Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows).
   - Install dependencies: `pip install -r backend/requirements.txt`.
   - Add `firebase_credentials.json` to `backend/` (from Firebase Console).
   - Update `alerts/twilio_config.json` with Twilio credentials.

3. **Frontend Setup**:
   - Install Node.js 18+.
   - Navigate to `frontend/`: `cd frontend`.
   - Install dependencies: `npm install`.
   - Start: `npm start`.

4. **Run with Docker**:
   - Install Docker and Docker Compose.
   - Run: `docker-compose up --build`.

## Usage

- Backend API: `http://localhost:8000`.
- Frontend Dashboard: `http://localhost:3000`.
- WebSocket Stream: `ws://localhost:8000/video/ws`.
- Alert Logs: `http://localhost:8000/alerts/logs`.

## Models

- Weapon Detection: YOLOv8 (`models/yolov8_weights.pt`).
- Fight/Theft Detection: Custom PyTorch models (`fight_model.pt`, `theft_model.pt`).

## Contributing

Feel free to open issues or PRs for improvements!