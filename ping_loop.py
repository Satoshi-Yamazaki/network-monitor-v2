import datetime
import time
from config import HOSTS, LOG_DIR
from database import save_ping, save_outage, save_avg_metrics
from metrics import ping_host, medir_speedtest

def ping_loop(data_lock, ping_status, ping_data):
    # Buffers de média
    buffers = {rede: {"ping": [], "download": [], "upload": []} for rede in HOSTS}
    failures = {rede: 0 for rede in HOSTS}
    fall_start_time = {rede: None for rede in HOSTS}
    last_speedtest = 0
    last_avg_calc = 0

    while True:
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        full_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        for rede, host in HOSTS.items():
            # PING
            latency = ping_host(host)
            status = "ok" if latency is not None else "fail"

            # CSV
            log_filename = f"{LOG_DIR}/{rede}_{now.strftime('%Y-%m-%d')}.csv"
            with open(log_filename, "a") as f:
                f.write(f"{full_timestamp},{latency if latency else 'timeout'},{status}\n")

            # DB
            save_ping(full_timestamp, latency, status, rede)

            # Memória compartilhada
            with data_lock:
                ping_status[rede]["current_ping"] = round(latency, 2) if latency else 0
                if rede not in ping_data:
                    ping_data[rede] = []
                ping_data[rede].append({"time": timestamp, "latency": latency if latency else 0})
                if len(ping_data[rede]) > 180:
                    ping_data[rede].pop(0)

            # Buffers para média
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

        # Speedtest a cada 2 minutos
        if time.time() - last_speedtest > 120:
            for rede in HOSTS:
                medir_speedtest(data_lock, ping_status, rede)
            last_speedtest = time.time()

        # Médias a cada 5 minutos
        if time.time() - last_avg_calc > 300:
            for rede in HOSTS:
                avg_ping = round(sum(buffers[rede]["ping"]) / len(buffers[rede]["ping"]), 2) if buffers[rede]["ping"] else 0
                avg_download = round(sum(buffers[rede]["download"]) / len(buffers[rede]["download"]), 2) if buffers[rede]["download"] else 0
                avg_upload = round(sum(buffers[rede]["upload"]) / len(buffers[rede]["upload"]), 2) if buffers[rede]["upload"] else 0
                save_avg_metrics(full_timestamp, avg_ping, avg_download, avg_upload, rede)

                # Limpa buffers
                buffers[rede]["ping"].clear()
                buffers[rede]["download"].clear()
                buffers[rede]["upload"].clear()

            last_avg_calc = time.time()

        time.sleep(1)
