import sqlite3
from datetime import datetime

DB_NAME = 'events.db'

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT,
            description TEXT,
            capacity INTEGER,
            category TEXT,
            created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            registered_at TEXT,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    # ── Migrate old schema: add columns that may not exist yet ──
    existing_event_cols = [row[1] for row in c.execute("PRAGMA table_info(events)").fetchall()]
    if "category" not in existing_event_cols:
        c.execute("ALTER TABLE events ADD COLUMN category TEXT")
    existing_reg_cols = [row[1] for row in c.execute("PRAGMA table_info(registrations)").fetchall()]
    if "phone" not in existing_reg_cols:
        c.execute("ALTER TABLE registrations ADD COLUMN phone TEXT")
    conn.commit()
    conn.close()

def add_event(name, date, location, description, capacity, category):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO events (name, date, location, description, capacity, category, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, date, location, description, capacity, category, now))
    conn.commit()
    conn.close()

def get_events():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM events ORDER BY date ASC')
    events = c.fetchall()
    conn.close()
    return events

def get_event(event_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM events WHERE id = ?', (event_id,))
    event = c.fetchone()
    conn.close()
    return event

def update_event(event_id, name, date, location, description, capacity, category):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE events SET name=?, date=?, location=?, description=?, capacity=?, category=?
        WHERE id=?
    ''', (name, date, location, description, capacity, category, event_id))
    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM registrations WHERE event_id = ?', (event_id,))
    c.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()

def register_participant(event_id, name, email, phone=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT capacity FROM events WHERE id = ?', (event_id,))
    capacity = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM registrations WHERE event_id = ?', (event_id,))
    registered = c.fetchone()[0]
    if registered >= capacity:
        conn.close()
        return False, "Event is at full capacity."
    c.execute('SELECT id FROM registrations WHERE event_id = ? AND email = ?', (event_id, email))
    if c.fetchone():
        conn.close()
        return False, "This email is already registered for the event."
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO registrations (event_id, name, email, phone, registered_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (event_id, name, email, phone, now))
    conn.commit()
    reg_id = c.lastrowid
    conn.close()
    return True, reg_id

def get_participants(event_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM registrations WHERE event_id = ? ORDER BY registered_at ASC', (event_id,))
    participants = c.fetchall()
    conn.close()
    return participants

def get_registrations_by_email(email):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT r.id, e.name, e.date, e.location, r.name, r.registered_at
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        WHERE r.email = ?
        ORDER BY r.registered_at DESC
    ''', (email,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_dashboard_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM events')
    total_events = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM registrations')
    total_registrations = c.fetchone()[0]
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM events WHERE date >= ?", (today,))
    upcoming_events = c.fetchone()[0]
    c.execute('''
        SELECT e.name, COUNT(r.id) as reg_count
        FROM events e LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.id ORDER BY reg_count DESC LIMIT 5
    ''')
    top_events = c.fetchall()
    c.execute('''
        SELECT e.name, e.capacity, COUNT(r.id) as reg_count
        FROM events e LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.id
    ''')
    capacity_data = c.fetchall()
    c.execute('''
        SELECT e.category, COUNT(r.id) as reg_count
        FROM events e LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.category
    ''')
    category_data = c.fetchall()
    c.execute('''
        SELECT DATE(registered_at) as reg_date, COUNT(*) as count
        FROM registrations
        GROUP BY reg_date ORDER BY reg_date ASC
    ''')
    reg_trend = c.fetchall()
    conn.close()
    return {
        "total_events": total_events,
        "total_registrations": total_registrations,
        "upcoming_events": upcoming_events,
        "top_events": top_events,
        "capacity_data": capacity_data,
        "category_data": category_data,
        "reg_trend": reg_trend
    }
