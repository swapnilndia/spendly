import sqlite3
import os
from datetime import date
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spendly.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123", method="pbkdf2:sha256")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash)
    )
    user_id = cursor.lastrowid

    today = date.today()
    y, m = today.year, today.month

    def month_day(day):
        d = min(day, today.day)
        return date(y, m, d).strftime("%Y-%m-%d")

    sample_expenses = [
        (user_id, 12.50,  "Food",          month_day(2),  "Lunch at cafe"),
        (user_id, 45.00,  "Transport",     month_day(4),  "Monthly bus pass"),
        (user_id, 120.00, "Bills",         month_day(6),  "Electricity bill"),
        (user_id, 35.00,  "Health",        month_day(8),  "Pharmacy"),
        (user_id, 20.00,  "Entertainment", month_day(11), "Movie tickets"),
        (user_id, 65.00,  "Shopping",      month_day(14), "Clothing"),
        (user_id, 8.75,   "Other",         month_day(17), "Miscellaneous"),
        (user_id, 22.00,  "Food",          month_day(20), "Weekly groceries"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses
    )
    conn.commit()
    conn.close()
