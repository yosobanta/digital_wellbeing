import sqlite3
from datetime import datetime, date
import os
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT NOT NULL,
                window_title TEXT,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                duration_seconds INTEGER NOT NULL,
                date DATE NOT NULL
            )
        ''')
        conn.commit()

def save_session(app_name, window_title, start_time, end_time, duration_seconds):
    if duration_seconds <= 0:
        return
        
    current_date = start_time.date().isoformat()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (app_name, window_title, start_time, end_time, duration_seconds, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (app_name, window_title, start_time.isoformat(), end_time.isoformat(), duration_seconds, current_date))
        conn.commit()

def get_daily_usage(target_date=None):
    if target_date is None:
        target_date = date.today().isoformat()
    elif isinstance(target_date, date):
        target_date = target_date.isoformat()
        
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT app_name, SUM(duration_seconds) as total_seconds
            FROM sessions
            WHERE date = ?
            GROUP BY app_name
            ORDER BY total_seconds DESC
        ''', (target_date,))
        return cursor.fetchall()

if __name__ == "__main__":
    init_db()
