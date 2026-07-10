import sqlite3
import os
import ollama
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(BASE_DIR, 'pulseai.db'))

def get_weekly_data():
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    results = conn.execute('''
        SELECT window, COUNT(*) as count
        FROM activities
        WHERE timestamp >= ?
        AND window != 'Task Switching'
        GROUP BY window
        ORDER BY count DESC
        LIMIT 10
    ''', (week_ago,)).fetchall()
    return results

def generate_summary():
    data = get_weekly_data()
    if not data:
        print("No data yet. Run the tracker for a few days first.")
        return
    
    activity_text = "\n".join([
        f"- {window}: {count * 10 // 60} minutes"
        for window, count in data
    ])
    
    prompt = f"""You are a productivity coach. Based on this week's computer activity data, give a brief 5-line insight report:

{activity_text}

Focus on: what they worked on most, any distractions, and one actionable suggestion."""

    response = ollama.chat(
        model='mistral',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    print("\n🤖 Weekly AI Summary:")
    print(response['message']['content'])

generate_summary()