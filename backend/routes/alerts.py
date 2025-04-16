from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from firebase_admin import firestore
from utils.alert_manager import send_alert
from typing import List, Dict
import datetime

router = APIRouter()

# Initialize Firestore client
db = firestore.client()

@router.get("/logs", response_model=List[Dict])
async def get_alert_logs():
    """
    Retrieve the last 10 threat logs from Firebase.
    """
    try:
        query = db.collection("threat_logs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10)
        docs = query.stream()
        logs = [
            {"id": doc.id, "timestamp": doc.to_dict().get("timestamp"), "threats": doc.to_dict().get("threats")}
            for doc in docs
        ]
        return JSONResponse(logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")

@router.post("/manual")
async def trigger_manual_alert(threats: List[str] = ["test_threat"]):
    """
    Trigger a manual alert for testing purposes.
    """
    try:
        if not threats:
            raise HTTPException(status_code=400, detail="At least one threat type is required")
        
        # Log to Firebase
        doc_ref = db.collection("threat_logs").document()
        doc_ref.set({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "threats": threats,
            "manual": True
        })
        
        # Send Twilio alert
        send_alert(threats)
        
        return JSONResponse({"status": "Manual alert triggered", "threats": threats})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering alert: {str(e)}")

@router.get("/status")
async def alert_system_status():
    """
    Check if the alert system is operational.
    """
    return JSONResponse({"status": "Alert system operational"})