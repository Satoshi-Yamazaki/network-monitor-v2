import datetime
import time
import threading
from config import HOST, LOG_DIR
from database import save_ping, save_outage, save_avg_metrics
from metrics import ping_host, medir_speedtest

def ping_loop(data_lock, ping_status, ping_data):
    consecutive_failures = 0
    fall_start_time = None
    ping_buffer, download_buffer, upload_buffer = [], [], []
    last_speedtest = 0
    last_avg_calc = 0

    while True:
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        full_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        latency = ping_host(HOST)
        status = "ok" if latency is not None else "fail"

        # CSV
        log_filename = now.strftime(f"{LOG_DIR}/%Y-%m-%d.csv")
        with open(log_filename, "a") as f:
            f.write(f"{full_timestamp},{latency if latency else 'timeout'},{status}\n")

        # DB
        save_ping(full_timestamp, latency, status)

        # Update memory
        with data_lock:
            ping_status["current_ping"] = round(latency, 2) if latency else 0
            ping_data.append({"time": timestamp, "latency": latency if latency else 0})
            if len(ping_data) > 180:
                ping_data.pop(0)

        # Média buffers
        if latency is not None:
            ping_buffer.append(latency)
        if ping_status["download"] > 0:
            download_buffer.append(ping_status["download"])
        if ping_status["upload"] > 0:
            upload_buffer.append(ping_status["upload"])

        # Quedas
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

        # Speedtest 2min
        if time.time() - last_speedtest > 120:
            medir_speedtest(data_lock, ping_status)
            last_speedtest = time.time()

        # Médias 5min
        if time.time() - last_avg_calc > 300:
            avg_ping = round(sum(ping_buffer) / len(ping_buffer), 2) if ping_buffer else 0
            avg_download = round(sum(download_buffer) / len(download_buffer), 2) if download_buffer else 0
            avg_upload = round(sum(upload_buffer) / len(upload_buffer), 2) if upload_buffer else 0

            save_avg_metrics(full_timestamp, avg_ping, avg_download, avg_upload)
            print(f"[{full_timestamp}] Médias salvas -> Ping: {avg_ping} ms, Down: {avg_download} Mbps, Up: {avg_upload} Mbps")

            ping_buffer.clear()
            download_buffer.clear()
            upload_buffer.clear()
            last_avg_calc = time.time()

        time.sleep(1)
