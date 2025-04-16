import json
from twilio.rest import Client
import os

# Load config from file if env vars are not set
config_path = os.getenv("TWILIO_CONFIG_PATH", "alerts/twilio_config.json")
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", config.get("TWILIO_ACCOUNT_SID"))
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", config.get("TWILIO_AUTH_TOKEN"))
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", config.get("TWILIO_PHONE_NUMBER"))
    ALERT_RECEIVER = os.getenv("ALERT_RECEIVER", config.get("ALERT_RECEIVER"))
else:
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_sid")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
    ALERT_RECEIVER = os.getenv("ALERT_RECEIVER", "+0987654321")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_alert(threats):
    message_body = f"Threat Detected: {', '.join(threats)}"
    try:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=ALERT_RECEIVER
        )
        print(f"Alert sent: {message.sid}")
    except Exception as e:
        print(f"Error sending alert: {e}")