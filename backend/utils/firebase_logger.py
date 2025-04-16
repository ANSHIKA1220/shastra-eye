import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")  # ensure this file is securely stored
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Logs a threat event to Firestore
def log_event(threats: list):
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "threats": threats
        }
        db.collection("threat_logs").add(data)
    except Exception as e:
        print("Error logging event:", e)

# Gets recent logs (most recent first)
def get_recent_logs(limit=10):
    try:
        logs_ref = db.collection("threat_logs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
        return [doc.to_dict() for doc in logs_ref.stream()]
    except Exception as e:
        print("Error retrieving logs:", e)
        return []
