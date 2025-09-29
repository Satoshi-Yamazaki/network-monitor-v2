import datetime
import time
import threading
from config import HOSTS, LOG_DIR
from database import save_ping, save_outage, save_avg_metrics
from metrics import ping_host, medir_speedtest

def ping_loop(data_lock, ping_status, ping_data):
    buffers = {
        "prefeitura": {"ping": [], "download": [], "upload": []},
        "conectada": {"ping": [], "download": [], "upload": []}
    }
    failures = {"prefeitura": 0, "conectada": 0}
    fall_start_time = {"prefeitura": None, "conectada": None}
    last_speedtest = 0
    last_avg_calc = 0

    while True:
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        full_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        for rede, host in HOSTS.items():
            latency = ping_host(host)
            status = "ok" if latency is not None else "fail"

            # CSV separado por rede
            log_filename = now.strftime(f"{LOG_DIR}/{rede}_%Y-%m-%d.csv")
            with open(log_filename, "a") as f:
                f.write(f"{full_timestamp},{latency if latency else 'timeout'},{status}\n")

            # DB
            save_ping(full_timestamp, latency, status, rede)

            # Memória
            with data_lock:
                ping_status[rede]["current_ping"] = round(latency, 2) if latency else 0
                ping_data[rede].append({"time": timestamp, "latency": latency if latency else 0})
                if len(ping_data[rede]) > 180:
                    ping_data[rede].pop(0)

            # Buffer
            if latency is not None:
                buffers[rede]["ping"].append(latency)
            if ping_status[rede]["download"] > 0:
                buffers[rede]["download"].append(ping_status[rede]["download"])
            if ping_status[rede]["upload"] > 0:
                buffers[rede]["upload"].append(ping_status[rede]["upload"])

            # Quedas
            if latency is None:
                failures[rede] += 1
                if failures[rede] == 10:
                    fall_start_time[rede] = datetime.datetime.now() - datetime.timedelta(seconds=9)
            else:
                if failures[rede] >= 10 and fall_start_time[rede]:
                    fall_end_time = datetime.datetime.now()
                    duration = int((fall_end_time - fall_start_time[rede]).total_seconds())
                    save_outage(fall_start_time[rede].isoformat(), fall_end_time.isoformat(), duration, rede)
                failures[rede] = 0
                fall_start_time[rede] = None

        # Speedtest a cada 2min
        if time.time() - last_speedtest > 120:
            for rede in HOSTS.keys():
                medir_speedtest(data_lock, ping_status, rede)
            last_speedtest = time.time()

        # Médias a cada 5min
        if time.time() - last_avg_calc > 300:
            for rede in HOSTS.keys():
                avg_ping = round(sum(buffers[rede]["ping"]) / len(buffers[rede]["ping"]), 2) if buffers[rede]["ping"] else 0
                avg_download = round(sum(buffers[rede]["download"]) / len(buffers[rede]["download"]), 2) if buffers[rede]["download"] else 0
                avg_upload = round(sum(buffers[rede]["upload"]) / len(buffers[rede]["upload"]), 2) if buffers[rede]["upload"] else 0

                save_avg_metrics(full_timestamp, avg_ping, avg_download, avg_upload, rede)
                print(f"[{full_timestamp}] [{rede}] Médias salvas -> Ping: {avg_ping} ms, Down: {avg_download} Mbps, Up: {avg_upload} Mbps")

                buffers[rede]["ping"].clear()
                buffers[rede]["download"].clear()
                buffers[rede]["upload"].clear()

            last_avg_calc = time.time()

        time.sleep(1)
