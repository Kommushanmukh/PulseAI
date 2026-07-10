import sqlite3
from datetime import datetime, date
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(BASE_DIR, 'pulseai.db'))

def top_apps_today():
    today = date.today().isoformat()
    results = conn.execute('''
        SELECT window, COUNT(*) as count
        FROM activities
        WHERE timestamp LIKE ?
        AND window != 'Task Switching'
        GROUP BY window
        ORDER BY count DESC
        LIMIT 5
    ''', (f'{today}%',)).fetchall()
    
    print(f"\n📊 Top apps today ({today}):")
    for i, (window, count) in enumerate(results, 1):
        seconds = count * 10
        minutes = seconds // 60
        print(f"{i}. {window} — {minutes} mins")

top_apps_today()