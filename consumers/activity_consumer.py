import signal
import sys
import json
import sqlite3
from kafka import KafkaConsumer
from datetime import datetime
import os

# Setup database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(BASE_DIR, 'pulseai.db'))
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        window TEXT,
        type TEXT,
        duration_seconds INTEGER
    )
''')
conn.commit()

consumer = KafkaConsumer(
    'activity-events',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("PulseAI Consumer storing events...")
for message in consumer:
    event = message.value
    if event['window'] == 'Task Switching':
        continue
    cursor.execute('''
        INSERT INTO activities (timestamp, window, type, duration_seconds)
        VALUES (?, ?, ?, ?)
    ''', (event['timestamp'], event['window'], event['type'], event['duration_seconds']))
    conn.commit()
    print(f"Stored: {event['window']} at {event['timestamp']}")


def shutdown(sig, frame):
    print("\nShutting down gracefully...")
    conn.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
