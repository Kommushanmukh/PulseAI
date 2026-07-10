import time
import json
import pygetwindow as gw
from datetime import datetime
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def get_active_window():
    try:
        window = gw.getActiveWindow()
        return window.title if window else "Unknown"
    except:
        return "Unknown"

def track_activity():
    print("PulseAI Real Tracker running...")
    while True:
        window_title = get_active_window()
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "window_activity",
            "window": window_title,
            "duration_seconds": 10
        }
        producer.send('activity-events', value=event)
        print(f"Sent: {window_title}")
        time.sleep(2)

if __name__ == "__main__":
    track_activity()