import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import sys
import os
import sqlite3
from datetime import datetime, timedelta, date
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'pulseai.db')
PID_FILE = os.path.join(BASE_DIR, '.pulseai.pid')
python = sys.executable

class PulseAI:
    def __init__(self, root):
        self.root = root
        self.root.title("PulseAI")
        self.root.geometry("700x600")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)
        
        self.build_ui()
        self.check_status()
    def clear_output(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1e1e2e")
        header.pack(fill="x", padx=20, pady=(20,10))
        
        tk.Label(header, text="⚡ PulseAI", font=("Segoe UI", 24, "bold"),
                bg="#1e1e2e", fg="#cdd6f4").pack(side="left")
        
        self.status_label = tk.Label(header, text="● Stopped",
                font=("Segoe UI", 12), bg="#1e1e2e", fg="#f38ba8")
        self.status_label.pack(side="right", pady=10)

        # Buttons frame
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=20, pady=10)

        self.start_btn = tk.Button(btn_frame, text="▶  Start Tracking",
                font=("Segoe UI", 11, "bold"), bg="#a6e3a1", fg="#1e1e2e",
                relief="flat", padx=20, pady=10, cursor="hand2",
                command=self.start)
        self.start_btn.pack(side="left", padx=(0,10))

        self.stop_btn = tk.Button(btn_frame, text="■  Stop Tracking",
                font=("Segoe UI", 11, "bold"), bg="#f38ba8", fg="#1e1e2e",
                relief="flat", padx=20, pady=10, cursor="hand2",
                command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=(0,10))

        # Report buttons
        report_frame = tk.Frame(self.root, bg="#1e1e2e")
        report_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(report_frame, text="📊 Daily Report",
                font=("Segoe UI", 10), bg="#89b4fa", fg="#1e1e2e",
                relief="flat", padx=15, pady=8, cursor="hand2",
                command=lambda: self.report('daily')).pack(side="left", padx=(0,10))

        tk.Button(report_frame, text="📅 Weekly Report",
                font=("Segoe UI", 10), bg="#89b4fa", fg="#1e1e2e",
                relief="flat", padx=15, pady=8, cursor="hand2",
                command=lambda: self.report('weekly')).pack(side="left", padx=(0,10))

        tk.Button(report_frame, text="📆 Monthly Report",
                font=("Segoe UI", 10), bg="#89b4fa", fg="#1e1e2e",
                relief="flat", padx=15, pady=8, cursor="hand2",
                command=lambda: self.report('monthly')).pack(side="left", padx=(0,10))

        tk.Button(report_frame, text="🤖 AI Summary",
                font=("Segoe UI", 10), bg="#cba6f7", fg="#1e1e2e",
                relief="flat", padx=15, pady=8, cursor="hand2",
                command=self.ai_summary).pack(side="left")

        # Output area
        output_header = tk.Frame(self.root, bg="#1e1e2e")
        output_header.pack(fill="x", padx=20)

        tk.Label(output_header, text="Output", font=("Segoe UI", 10),
            bg="#1e1e2e", fg="#6c7086").pack(side="left")

        tk.Button(output_header, text="Clear",
        font=("Segoe UI", 9), bg="#45475a", fg="#cdd6f4",
        relief="flat", padx=10, pady=3, cursor="hand2",
        command=self.clear_output).pack(side="right")

        self.output = scrolledtext.ScrolledText(
                self.root, font=("Consolas", 10),
                bg="#181825", fg="#cdd6f4",
                relief="flat", padx=10, pady=10,
                height=22, wrap="word",
                insertbackground="#cdd6f4")
        self.output.pack(fill="both", expand=True, padx=20, pady=(5,20))

    def log(self, text, color="#cdd6f4"):
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.configure(state="disabled")
        self.output.see("end")

    def check_status(self):
        if os.path.exists(PID_FILE):
            self.status_label.config(text="● Running", fg="#a6e3a1")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        else:
            self.status_label.config(text="● Stopped", fg="#f38ba8")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def start(self):
        producer = subprocess.Popen(
            [python, 'producers/vscode_tracker.py'],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        consumer = subprocess.Popen(
            [python, 'consumers/activity_consumer.py'],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        with open(PID_FILE, 'w') as f:
            f.write(f"{producer.pid}\n{consumer.pid}")
        
        self.log("✅ PulseAI started — tracking in background")
        self.log(f"   Producer PID: {producer.pid}")
        self.log(f"   Consumer PID: {consumer.pid}")
        self.check_status()

    def stop(self):
        try:
            with open(PID_FILE, 'r') as f:
                pids = f.read().strip().split('\n')
            for pid in pids:
                subprocess.run(['taskkill', '/F', '/PID', pid.strip()],
                             capture_output=True)
            os.remove(PID_FILE)
            self.log("⛔ PulseAI stopped")
        except FileNotFoundError:
            self.log("⚠️  Not running")
        self.check_status()

    def get_data(self, days):
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

    def report(self, period):
        days = 1 if period == 'daily' else 7 if period == 'weekly' else 30
        data = self.get_data(days)
        
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        
        if not data:
            self.log("⚠️  No data yet. Start tracking first.")
            return

        self.log(f"📊 {period.capitalize()} Report — {date.today()}")
        self.log("─" * 60)
        self.log(f"{'App':<45} {'Time Spent':>10} {'Intervals':>9}")
        self.log("─" * 60)
        
        for window, count in data:
            total_seconds = count * 10
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            hours = minutes // 60
            mins_left = minutes % 60

            if hours > 0:
                time_str = f"{hours}h {mins_left}m"
            elif minutes > 0:
                time_str = f"{minutes}m {seconds}s"
            else:
                time_str = f"{seconds}s"
            short = window[:44] + "…" if len(window) > 44 else window
            self.log(f"{short:<45} {time_str:>10} {count:>8}")
        
        self.log("─" * 60)
        total = sum(c for _, c in data)
        self.log(f"Total tracked: {(total * 10) // 60} minutes")

    def ai_summary(self):
        self.log("🤖 Generating AI summary... please wait")
        thread = threading.Thread(target=self._run_ai)
        thread.daemon = True
        thread.start()

    def _run_ai(self):
        try:
            import ollama
            
            # Start ollama serve silently
            self.log("⚙️  Starting Ollama...")
            ollama_process = subprocess.Popen(
                ['ollama', 'serve'],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Give it 3 seconds to start
            import time
            time.sleep(3)
            
            data = self.get_data(7)
            if not data:
                self.log("⚠️  No data yet.")
                ollama_process.terminate()
                return
            
            activity_text = "\n".join([
                f"- {w}: {(c * 10) // 60} minutes"
                for w, c in data
            ])
            
            self.log("🤖 Generating summary with OLlama...")
            
            response = ollama.chat(
                model='mistral',
                messages=[{
                    'role': 'user',
                    'content': f"""You are a productivity coach. Based on this week's activity:

    {activity_text}

    Give a 5-line insight report: main focus, distractions, one actionable tip."""
                }]
            )
            
            self.log("\n🤖 AI Insights:")
            self.log("─" * 60)
            self.log(response['message']['content'])
            
            # Stop ollama to free RAM
            self.log("\n⚙️  Stopping Ollama to free RAM...")
            ollama_process.terminate()
            subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'],
                        capture_output=True)
            self.log("✅ Done")
            
        except Exception as e:
            self.log(f"⚠️  Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PulseAI(root)
    root.mainloop()