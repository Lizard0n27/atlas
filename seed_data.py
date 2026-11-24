# seed_data.py
import sqlite3
from datetime import date, timedelta

DB_NAME = "atlas.db"

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect_db() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        age INTEGER NOT NULL,
        height REAL NOT NULL,
        goal TEXT NOT NULL CHECK(goal IN ('lose', 'gain', 'maintain')),
        maintenance_cal INTEGER NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        weight REAL NOT NULL,
        calories INTEGER NOT NULL,
        trained INTEGER NOT NULL CHECK(trained IN (0, 1)),
        entry_date TEXT NOT NULL,
        UNIQUE(user_id, entry_date)
        )""")

init_db()

# User
with connect_db() as conn:
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO users (username, age, height, goal, maintenance_cal)
        VALUES (?, ?, ?, ?, ?)
    """, ("demo", 25, 180.0, "lose", 2500))

# 7 Einträge
today = date.today()
entries = [
    (today - timedelta(days=6), 82.5, 2600, 1),
    (today - timedelta(days=5), 82.3, 2550, 0),
    (today - timedelta(days=4), 82.1, 2500, 1),
    (today - timedelta(days=3), 81.9, 2450, 1),
    (today - timedelta(days=2), 81.7, 2400, 0),
    (today - timedelta(days=1), 81.5, 2350, 1),
    (today, 81.3, 2300, 1),
]

with connect_db() as conn:
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", ("demo",))
    user_id = c.fetchone()[0]

    for entry_date, weight, calories, trained in entries:
        c.execute("""
            INSERT OR REPLACE INTO entries (user_id, weight, calories, trained, entry_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, weight, calories, trained, entry_date.isoformat()))

print("Demo data created!")
