import subprocess
import threading
import time
import datetime
import os
import sqlite3
import json
from flask import Flask, jsonify, render_template_string # type: ignore

# ==============================
# Configurações
# ==============================
DB_FILE = "logs/monitor.db"
LOG_DIR = "logs"
HOST = "8.8.8.8"

ping_data = []
ping_status = {"current_ping": 0, "download": 0, "upload": 0}
data_lock = threading.Lock()
app = Flask(__name__)

# ==============================
# HTML da Interface Web
# ==============================
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Monitor de Ping</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            margin: 0;
            padding: 20px;
            font-family: sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 { font-size: 2em; margin-bottom: 10px; }
        canvas { width: 90vw !important; height: 60vh !important; }
        .stats { margin-bottom: 20px; text-align: center; }
    </style>
</head>
<body>
    <h1>Monitor de Ping – {{ host }}</h1>
    <div class="stats">
        <p><strong>Ping Atual:</strong> <span id="currentPing">--</span> ms</p>
        <p><strong>Download:</strong> <span id="downloadSpeed">--</span> Mbps</p>
        <p><strong>Upload:</strong> <span id="uploadSpeed">--</span> Mbps</p>
        <p><strong>Quedas Hoje:</strong> <span id="quedasHoje">--</span></p>
        <p><strong>Quedas 3 Dias:</strong> <span id="quedas3dias">--</span></p>
        <p><strong>Total de Quedas:</strong> <span id="quedasTotal">--</span></p>
    </div>
    <canvas id="pingChart"></canvas>

    <script>
        const ctx = document.getElementById('pingChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Ping (ms)',
                    borderColor: 'rgb(0, 200, 255)',
                    backgroundColor: 'rgba(0, 200, 255, 0.1)',
                    data: [],
                    tension: 0.2
                }]
            },
            options: {
                animation: false,
                scales: {
                    x: { ticks: { color: '#ccc' } },
                    y: { ticks: { color: '#ccc' }, beginAtZero: true }
                }
            }
        });

        async function fetchData() {
            const res = await fetch('/data');
            const data = await res.json();

            chart.data.labels = data.ping.map(d => d.time);
            chart.data.datasets[0].data = data.ping.map(d => d.latency);
            chart.update();

            document.getElementById('currentPing').innerText = data.current_ping;
            document.getElementById('downloadSpeed').innerText = data.download;
            document.getElementById('uploadSpeed').innerText = data.upload;
            document.getElementById('quedasHoje').innerText = data.stats.quedas_hoje;
            document.getElementById('quedas3dias').innerText = data.stats.quedas_3dias;
            document.getElementById('quedasTotal').innerText = data.stats.quedas_total;
        }

        setInterval(fetchData, 1000);
        fetchData();
    </script>
</body>
</html>
"""

# ==============================
# Banco de Dados
# ==============================
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

# ==============================
# Funções de Medição
# ==============================
def ping_host(host):
    try:
        result = subprocess.run(["ping", "-c", "1", "-W", "1", host], capture_output=True, text=True)
        if result.returncode == 0:
            for part in result.stdout.split():
                if "time=" in part:
                    return float(part.split("=")[1])
        return None
    except:
        return None

def medir_speedtest():
    try:
        result = subprocess.run(["speedtest", "--json"], capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)

            # Convertendo para Mbps
            download = round(data["download"] / 1_000_000, 2)
            upload = round(data["upload"] / 1_000_000, 2)
            ping_val = round(data["ping"], 2)

            with data_lock:
                ping_status["download"] = download
                ping_status["upload"] = upload

            save_speedtest(datetime.datetime.now().isoformat(), download, upload, ping_val)
            print(f"[{datetime.datetime.now().isoformat()}] Speedtest salvo -> D: {download} Mbps, U: {upload} Mbps, Ping: {ping_val} ms")
        else:
            print("Speedtest não retornou dados:", result.stderr)
    except Exception as e:
        print("Erro no speedtest:", e)

# ==============================
# Loops principais
# ==============================
def ping_loop():
    consecutive_failures = 0
    fall_start_time = None

    # buffers para médias
    ping_buffer = []
    download_buffer = []
    upload_buffer = []

    last_speedtest = 0
    last_avg_calc = 0

    while True:
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        full_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # Executa ping
        latency = ping_host(HOST)
        status = "ok" if latency is not None else "fail"

        # CSV log
        log_filename = now.strftime(f"{LOG_DIR}/%Y-%m-%d.csv")
        with open(log_filename, "a") as f:
            f.write(f"{full_timestamp},{latency if latency else 'timeout'},{status}\n")

        # SQLite log
        save_ping(full_timestamp, latency, status)

        # Atualiza memória para gráfico
        with data_lock:
            ping_status["current_ping"] = round(latency, 2) if latency else 0
            ping_data.append({"time": timestamp, "latency": latency if latency else 0})
            if len(ping_data) > 180:
                ping_data.pop(0)

        # Buffers para média
        if latency is not None:
            ping_buffer.append(latency)
        if ping_status["download"] > 0:
            download_buffer.append(ping_status["download"])
        if ping_status["upload"] > 0:
            upload_buffer.append(ping_status["upload"])

        # Detecta quedas
        if latency is None:
            consecutive_failures += 1
            if consecutive_failures == 10:
                fall_start_time = datetime.datetime.now() - datetime.timedelta(seconds=9)
        else:
            if consecutive_failures >= 10 and fall_start_time:
                fall_end_time = datetime.datetime.now()
                duration = int((fall_end_time - fall_start_time).total_seconds())
                save_outage(fall_start_time.isoformat(), fall_end_time.isoformat(), duration)
            consecutive_failures = 0
            fall_start_time = None

        # Executa speedtest a cada 2 minutos
        if time.time() - last_speedtest > 120:
            medir_speedtest()
            last_speedtest = time.time()

        # Salva médias a cada 5 minutos
        if time.time() - last_avg_calc > 300:
            if ping_buffer:
                avg_ping = round(sum(ping_buffer) / len(ping_buffer), 2)
            else:
                avg_ping = 0

            if download_buffer:
                avg_download = round(sum(download_buffer) / len(download_buffer), 2)
            else:
                avg_download = 0

            if upload_buffer:
                avg_upload = round(sum(upload_buffer) / len(upload_buffer), 2)
            else:
                avg_upload = 0

            save_avg_metrics(full_timestamp, avg_ping, avg_download, avg_upload)
            print(f"[{full_timestamp}] Médias salvas -> Ping: {avg_ping} ms, Down: {avg_download} Mbps, Up: {avg_upload} Mbps")

            # limpa buffers
            ping_buffer.clear()
            download_buffer.clear()
            upload_buffer.clear()
            last_avg_calc = time.time()

        time.sleep(1)

# ==============================
# API
# ==============================
def contar_quedas():
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

@app.route("/")
def index():
    return render_template_string(html_template, host=HOST)

@app.route("/data")
def data():
    with data_lock:
        stats = contar_quedas()
        return jsonify({
            "ping": ping_data,
            "current_ping": ping_status["current_ping"],
            "download": ping_status["download"],
            "upload": ping_status["upload"],
            "stats": stats
        })

# ==============================
# Inicialização
# ==============================
if __name__ == "__main__":
    init_db()
    t = threading.Thread(target=ping_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
