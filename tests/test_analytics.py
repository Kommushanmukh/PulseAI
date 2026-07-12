import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import tempfile
from datetime import datetime

def test_database_creation():
    """Test that database and table can be created"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            window TEXT,
            type TEXT,
            duration_seconds INTEGER
        )
    ''')
    conn.commit()
    
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    
    assert ('activities',) in tables
    conn.close()

def test_data_insertion():
    """Test that activity data can be inserted and retrieved"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            window TEXT,
            type TEXT,
            duration_seconds INTEGER
        )
    ''')
    
    conn.execute('''
        INSERT INTO activities (timestamp, window, type, duration_seconds)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().isoformat(), 'VS Code', 'window_activity', 10))
    conn.commit()
    
    result = conn.execute('SELECT COUNT(*) FROM activities').fetchone()
    assert result[0] == 1
    conn.close()

def test_analytics_query():
    """Test that analytics query returns correct results"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            window TEXT,
            type TEXT,
            duration_seconds INTEGER
        )
    ''')
    
    # Insert test data
    for _ in range(5):
        conn.execute('''
            INSERT INTO activities (timestamp, window, type, duration_seconds)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), 'VS Code', 'window_activity', 10))
    
    conn.commit()
    
    result = conn.execute('''
        SELECT window, COUNT(*) as count
        FROM activities
        GROUP BY window
        ORDER BY count DESC
    ''').fetchall()
    
    assert len(result) == 1
    assert result[0][0] == 'VS Code'
    assert result[0][1] == 5
    conn.close()