import datetime
import time
from config import INTERFACES, LOG_DIR, HOST
from database import save_ping, save_outage, save_avg_metrics
from metrics import ping_host, medir_speedtest

def ping_loop(data_lock, ping_status, ping_data):
    consecutive_failures = {iface: 0 for iface in INTERFACES}
    fall_start_time = {iface: None for iface in INTERFACES}
    ping_buffer = {iface: [] for iface in INTERFACES}
    download_buffer = {iface: [] for iface in INTERFACES}
    upload_buffer = {iface: [] for iface in INTERFACES}
    last_speedtest = {iface: 0 for iface in INTERFACES}
    last_avg_calc = {iface: 0 for iface in INTERFACES}

    while True:
        now = datetime.datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        full_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        for iface_name, iface_dev in INTERFACES.items():
            # ping usando interface física
            latency = ping_host(HOST, interface=iface_dev)
            status = "ok" if latency is not None else "fail"

            # CSV log por interface
            log_filename = now.strftime(f"{LOG_DIR}/{iface_name}_%Y-%m-%d.csv")
            with open(log_filename, "a") as f:
                f.write(f"{full_timestamp},{latency if latency is not None else 'timeout'},{status}\n")

            # DB
            save_ping(iface_name, full_timestamp, latency, status)

            # Update memória (protegido por lock)
            with data_lock:
                ping_status[iface_name]["current_ping"] = round(latency, 2) if latency is not None else 0
                ping_data[iface_name].append({
                    "time": timestamp,
                    "latency": latency if latency is not None else 0,
                    "download": ping_status[iface_name].get("download", 0),
                    "upload": ping_status[iface_name].get("upload", 0)
                })
                if len(ping_data[iface_name]) > 180:
                    ping_data[iface_name].pop(0)

            # Buffers para médias
            if latency is not None:
                ping_buffer[iface_name].append(latency)
            if ping_status[iface_name].get("download", 0) > 0:
                download_buffer[iface_name].append(ping_status[iface_name]["download"])
            if ping_status[iface_name].get("upload", 0) > 0:
                upload_buffer[iface_name].append(ping_status[iface_name]["upload"])

            # Detecta quedas
            if latency is None:
                consecutive_failures[iface_name] += 1
                if consecutive_failures[iface_name] == 10:
                    fall_start_time[iface_name] = datetime.datetime.now() - datetime.timedelta(seconds=9)
            else:
                if consecutive_failures[iface_name] >= 10 and fall_start_time[iface_name]:
                    fall_end_time = datetime.datetime.now()
                    duration = int((fall_end_time - fall_start_time[iface_name]).total_seconds())
                    save_outage(iface_name, fall_start_time[iface_name].isoformat(), fall_end_time.isoformat(), duration)
                consecutive_failures[iface_name] = 0
                fall_start_time[iface_name] = None

            # Speedtest a cada 2 minutos por interface
            if time.time() - last_speedtest[iface_name] > 120:
                medir_speedtest(iface_name, data_lock, ping_status)
                last_speedtest[iface_name] = time.time()

            # Salva médias a cada 5 minutos por interface
            if time.time() - last_avg_calc[iface_name] > 300:
                avg_ping = round(sum(ping_buffer[iface_name]) / len(ping_buffer[iface_name]), 2) if ping_buffer[iface_name] else 0
                avg_download = round(sum(download_buffer[iface_name]) / len(download_buffer[iface_name]), 2) if download_buffer[iface_name] else 0
                avg_upload = round(sum(upload_buffer[iface_name]) / len(upload_buffer[iface_name]), 2) if upload_buffer[iface_name] else 0

                save_avg_metrics(iface_name, full_timestamp, avg_ping, avg_download, avg_upload)

                ping_buffer[iface_name].clear()
                download_buffer[iface_name].clear()
                upload_buffer[iface_name].clear()
                last_avg_calc[iface_name] = time.time()

        time.sleep(1)
