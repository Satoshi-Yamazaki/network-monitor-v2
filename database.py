import sqlite3
import os
from config import DB_FILE, LOG_DIR, INTERFACES

def init_db():
    os.makedirs(LOG_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    for iface in INTERFACES:
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS ping_log_{iface} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            latency REAL,
            status TEXT
        )""")
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS outages_{iface} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER
        )""")
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS speedtest_{iface} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            download REAL,
            upload REAL,
            ping REAL
        )""")
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS metrics_avg_{iface} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            avg_ping REAL,
            avg_download REAL,
            avg_upload REAL
        )""")
    conn.commit()
    conn.close()

# Inserção
def save_ping(timestamp, latency, status, interface):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(f"INSERT INTO ping_log_{interface} (timestamp, latency, status) VALUES (?, ?, ?)",
                 (timestamp, latency if latency else None, status))
    conn.commit()
    conn.close()

def save_outage(start_time, end_time, duration, interface):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(f"INSERT INTO outages_{interface} (start_time, end_time, duration) VALUES (?, ?, ?)",
                 (start_time, end_time, duration))
    conn.commit()
    conn.close()

def save_speedtest(timestamp, download, upload, ping, interface):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(f"INSERT INTO speedtest_{interface} (timestamp, download, upload, ping) VALUES (?, ?, ?, ?)",
                 (timestamp, download, upload, ping))
    conn.commit()
    conn.close()

def save_avg_metrics(timestamp, avg_ping, avg_download, avg_upload, interface):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(f"INSERT INTO metrics_avg_{interface} (timestamp, avg_ping, avg_download, avg_upload) VALUES (?, ?, ?, ?)",
                 (timestamp, avg_ping, avg_download, avg_upload))
    conn.commit()
    conn.close()

def contar_quedas(interface):
    import datetime
    hoje = datetime.datetime.now().date()
    dias3 = hoje - datetime.timedelta(days=2)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    table = f"outages_{interface}"
    c.execute(f"SELECT COUNT(*) FROM {table}")
    total = c.fetchone()[0]
    c.execute(f"SELECT COUNT(*) FROM {table} WHERE DATE(start_time)=?", (hoje,))
    hoje_count = c.fetchone()[0]
    c.execute(f"SELECT COUNT(*) FROM {table} WHERE DATE(start_time)>=?", (dias3,))
    dias3_count = c.fetchone()[0]

    conn.close()
    return {
        "quedas_total": total,
        "quedas_hoje": hoje_count,
        "quedas_3dias": dias3_count
    }
