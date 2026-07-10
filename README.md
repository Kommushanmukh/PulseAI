# PulseAI — Personal Activity Intelligence

Know yourself through your own data.

PulseAI passively tracks your computer activity, streams it through Kafka, 
stores it locally, and generates AI-powered productivity insights using a 
local LLM — no cloud, no API keys, 100% private.

## Architecture

Window Tracker → Kafka → Consumer → SQLite → Analytics → Ollama (Mistral)

## Features

- Real-time window activity tracking
- Kafka-powered event streaming
- Local SQLite persistence
- Daily top apps report
- Weekly AI summary powered by Mistral (runs 100% locally)

## Tech Stack

- Python, Kafka, Docker, SQLite, Ollama, Mistral

## Setup

1. Install dependencies
pip install -r requirements.txt

2. Start Kafka
docker-compose up -d

3. Start Ollama
ollama serve

4. Run the tracker (terminal 1)
python producers/vscode_tracker.py

5. Run the consumer (terminal 2)
python consumers/activity_consumer.py

6. View today's insights
python analytics/insights.py

7. Generate weekly AI summary
python analytics/weekly_summary.py

## Project Structure

PulseAI/
├── producers/
│   └── vscode_tracker.py      # Tracks active window
├── consumers/
│   └── activity_consumer.py   # Stores events to SQLite
├── analytics/
│   ├── insights.py            # Daily app usage report
│   └── weekly_summary.py      # AI-powered weekly summary
├── docker-compose.yml         # Kafka + Zookeeper
└── requirements.txt