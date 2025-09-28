import sqlite3
import os
from config import DB_FILE, LOG_DIR

def init_db():
    os.makedirs(LOG_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS ping_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        latency REAL,
        status TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS outages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT,
        end_time TEXT,
        duration INTEGER
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS speedtest (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        download REAL,
        upload REAL,
        ping REAL
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS metrics_avg (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        avg_ping REAL,
        avg_download REAL,
        avg_upload REAL
    )""")
    conn.commit()
    conn.close()

def save_ping(timestamp, latency, status):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO ping_log (timestamp, latency, status) VALUES (?, ?, ?)",
                 (timestamp, latency if latency else None, status))
    conn.commit()
    conn.close()

def save_outage(start_time, end_time, duration):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO outages (start_time, end_time, duration) VALUES (?, ?, ?)",
                 (start_time, end_time, duration))
    conn.commit()
    conn.close()

def save_speedtest(timestamp, download, upload, ping):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO speedtest (timestamp, download, upload, ping) VALUES (?, ?, ?, ?)",
                 (timestamp, download, upload, ping))
    conn.commit()
    conn.close()

def save_avg_metrics(timestamp, avg_ping, avg_download, avg_upload):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO metrics_avg (timestamp, avg_ping, avg_download, avg_upload) VALUES (?, ?, ?, ?)",
                 (timestamp, avg_ping, avg_download, avg_upload))
    conn.commit()
    conn.close()

def contar_quedas():
    import datetime
    hoje = datetime.datetime.now().date()
    dias3 = hoje - datetime.timedelta(days=2)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM outages")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM outages WHERE DATE(start_time)=?", (hoje,))
    hoje_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM outages WHERE DATE(start_time)>=?", (dias3,))
    dias3_count = c.fetchone()[0]

    conn.close()
    return {
        "quedas_total": total,
        "quedas_hoje": hoje_count,
        "quedas_3dias": dias3_count
    }
