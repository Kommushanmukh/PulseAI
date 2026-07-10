import sys
import subprocess
import os
import sqlite3
import signal
from datetime import datetime, date, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint


console = Console()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'pulseai.db')

COMMANDS = ['start', 'stop', 'report']

def start():
    console.print(Panel("🚀 Starting PulseAI...", style="bold green"))
    
    # Get venv python path
    python = sys.executable  # this uses the SAME python that's running pulseai.py
    
    producer = subprocess.Popen(
        [python, 'producers/vscode_tracker.py'],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=BASE_DIR
    )
    
    consumer = subprocess.Popen(
        [python, 'consumers/activity_consumer.py'],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=BASE_DIR
    )
    
    with open('.pulseai.pid', 'w') as f:
        f.write(f"{producer.pid}\n{consumer.pid}")
    
    console.print("✅ Tracker running in background")
    console.print("✅ Consumer storing to database")
    console.print("\n[bold]Run [green]python pulseai.py report[/green] anytime for insights[/bold]")

def stop():
    try:
        with open('.pulseai.pid', 'r') as f:
            pids = f.read().strip().split('\n')
        for pid in pids:
            subprocess.run(['taskkill', '/F', '/PID', pid], 
                         capture_output=True)
        os.remove('.pulseai.pid')
        console.print("✅ PulseAI stopped gracefully")
    except FileNotFoundError:
        console.print("⚠️  PulseAI is not running")
    except Exception as e:
        console.print(f"⚠️  {e}")

def get_data(days=1):
    conn = sqlite3.connect(DB_PATH)
    since = (datetime.now() - timedelta(days=days)).isoformat()
    results = conn.execute('''
        SELECT window, COUNT(*) as count
        FROM activities
        WHERE timestamp >= ?
        AND window != 'Task Switching'
        GROUP BY window
        ORDER BY count DESC
        LIMIT 10
    ''', (since,)).fetchall()
    conn.close()
    return results

def report(period='daily'):
    days = 1 if period == 'daily' else 7 if period == 'weekly' else 30
    label = period.capitalize()
    
    data = get_data(days)
    
    if not data:
        console.print("⚠️  No data yet. Run [green]python pulseai.py start[/green] first.")
        return

    # Rich table
    console.print(Panel(f"📊 PulseAI {label} Report — {date.today()}", style="bold blue"))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("App", style="cyan", width=50)
    table.add_column("Time Spent", style="green")
    table.add_column("Sessions", style="yellow")
    
    for window, count in data:
        minutes = (count * 10) // 60
        seconds = (count * 10) % 60
        time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
        # Shorten long window titles
        short_name = window[:47] + "..." if len(window) > 47 else window
        table.add_row(short_name, time_str, str(count))
    
    console.print(table)
    
    # Bar chart in terminal
    

def ai_summary(period='weekly'):
    days = 7 if period == 'weekly' else 30
    data = get_data(days)
    
    if not data:
        console.print("⚠️  No data yet.")
        return
    
    import ollama
    activity_text = "\n".join([
        f"- {window}: {(count * 10) // 60} minutes"
        for window, count in data
    ])
    
    console.print(Panel("🤖 Generating AI Summary...", style="bold yellow"))
    
    response = ollama.chat(
        model='mistral',
        messages=[{
            'role': 'user',
            'content': f"""You are a productivity coach. Based on this {period} activity:

{activity_text}

Give a 5-line insight report covering: main focus areas, distractions, and one actionable tip."""
        }]
    )
    
    console.print(Panel(
        response['message']['content'],
        title="🤖 AI Insights",
        style="bold green"
    ))

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS + ['ai']:
        console.print("\n[bold]PulseAI — Personal Activity Intelligence[/bold]")
        console.print("\nUsage:")
        console.print("  [green]python pulseai.py start[/green]           → Start tracking")
        console.print("  [green]python pulseai.py stop[/green]            → Stop tracking")
        console.print("  [green]python pulseai.py report daily[/green]    → Daily report")
        console.print("  [green]python pulseai.py report weekly[/green]   → Weekly report")
        console.print("  [green]python pulseai.py report monthly[/green]  → Monthly report")
        console.print("  [green]python pulseai.py ai weekly[/green]       → AI summary\n")
        sys.exit(0)
    
    cmd = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else 'daily'
    
    if cmd == 'start':
        start()
    elif cmd == 'stop':
        stop()
    elif cmd == 'report':
        report(arg)
    elif cmd == 'ai':
        ai_summary(arg)