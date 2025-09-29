import sqlite3
import os
from config import DB_FILE, LOG_DIR, INTERFACES

def init_db():
    os.makedirs(LOG_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Criar tabelas separadas por interface
    for name in INTERFACES.keys():
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS ping_log_{name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            latency REAL,
            status TEXT
        )""")

        c.execute(f"""
        CREATE TABLE IF NOT EXISTS outages_{name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER
        )""")

        c.execute(f"""
        CREATE TABLE IF NOT EXISTS speedtest_{name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            download REAL,
            upload REAL,
            ping REAL
        )""")

        c.execute(f"""
        CREATE TABLE IF NOT EXISTS metrics_avg_{name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            avg_ping REAL,
            avg_download REAL,
            avg_upload REAL
        )""")

    conn.commit()
    conn.close()

def _get_conn():
    return sqlite3.connect(DB_FILE)

# Generic save functions that accept interface name
def save_ping(interface, timestamp, latency, status):
    conn = _get_conn()
    conn.execute(f"INSERT INTO ping_log_{interface} (timestamp, latency, status) VALUES (?, ?, ?)",
                 (timestamp, latency if latency is not None else None, status))
    conn.commit()
    conn.close()

def save_outage(interface, start_time, end_time, duration):
    conn = _get_conn()
    conn.execute(f"INSERT INTO outages_{interface} (start_time, end_time, duration) VALUES (?, ?, ?)",
                 (start_time, end_time, duration))
    conn.commit()
    conn.close()

def save_speedtest(interface, timestamp, download, upload, ping):
    conn = _get_conn()
    conn.execute(f"INSERT INTO speedtest_{interface} (timestamp, download, upload, ping) VALUES (?, ?, ?, ?)",
                 (timestamp, download, upload, ping))
    conn.commit()
    conn.close()

def save_avg_metrics(interface, timestamp, avg_ping, avg_download, avg_upload):
    conn = _get_conn()
    conn.execute(f"INSERT INTO metrics_avg_{interface} (timestamp, avg_ping, avg_download, avg_upload) VALUES (?, ?, ?, ?)",
                 (timestamp, avg_ping, avg_download, avg_upload))
    conn.commit()
    conn.close()

# Contagem de quedas: retorna por interface e totals gerais
def contar_quedas():
    import datetime
    hoje = datetime.datetime.now().date()
    dias3 = hoje - datetime.timedelta(days=2)

    conn = _get_conn()
    c = conn.cursor()

    result = {
        "overall": {"quedas_total": 0, "quedas_hoje": 0, "quedas_3dias": 0},
        "by_interface": {}
    }

    # Por interface
    for name in INTERFACES.keys():
        c.execute(f"SELECT COUNT(*) FROM outages_{name}")
        total = c.fetchone()[0] or 0

        c.execute(f"SELECT COUNT(*) FROM outages_{name} WHERE DATE(start_time)=?", (str(hoje),))
        hoje_count = c.fetchone()[0] or 0

        c.execute(f"SELECT COUNT(*) FROM outages_{name} WHERE DATE(start_time)>=?", (str(dias3),))
        dias3_count = c.fetchone()[0] or 0

        result["by_interface"][name] = {
            "quedas_total": total,
            "quedas_hoje": hoje_count,
            "quedas_3dias": dias3_count
        }

        result["overall"]["quedas_total"] += total
        result["overall"]["quedas_hoje"] += hoje_count
        result["overall"]["quedas_3dias"] += dias3_count

    conn.close()
    return result
