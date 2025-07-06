import sqlite3
import json
import threading
from datetime import datetime

def get_db():
    # Thread-safe connection per thread
    local = threading.local()
    if not hasattr(local, 'conn'):
        local.conn = sqlite3.connect('scan_status.db', check_same_thread=False)
        local.conn.row_factory = sqlite3.Row
    return local.conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scan_status (
        scan_id TEXT PRIMARY KEY,
        status TEXT,
        progress INTEGER,
        result TEXT,
        updated_at TEXT
    )''')
    conn.commit()

def set_scan_status(scan_id, status=None, progress=None, result=None):
    conn = get_db()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('SELECT scan_id FROM scan_status WHERE scan_id=?', (scan_id,))
    exists = c.fetchone()
    if exists:
        c.execute('''UPDATE scan_status SET 
            status=COALESCE(?, status),
            progress=COALESCE(?, progress),
            result=COALESCE(?, result),
            updated_at=?
            WHERE scan_id=?''',
            (status, progress, json.dumps(result) if result is not None else None, now, scan_id))
    else:
        c.execute('''INSERT INTO scan_status (scan_id, status, progress, result, updated_at) VALUES (?, ?, ?, ?, ?)''',
            (scan_id, status or 'running', progress or 1, json.dumps(result) if result is not None else None, now))
    conn.commit()

def get_scan_status(scan_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM scan_status WHERE scan_id=?', (scan_id,))
    row = c.fetchone()
    if not row:
        return None
    return {
        'scan_id': row['scan_id'],
        'status': row['status'],
        'progress': row['progress'],
        'result': json.loads(row['result']) if row['result'] else None,
        'updated_at': row['updated_at']
    }
