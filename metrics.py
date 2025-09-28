import subprocess
import json
import datetime
from database import save_speedtest

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

import speedtest # type: ignore
import datetime

def medir_speedtest(data_lock, ping_status):
    try:
        s = speedtest.Speedtest()
        s.get_best_server()
        download = round(s.download() / 1_000_000, 2)  # Mbps
        upload = round(s.upload() / 1_000_000, 2)      # Mbps
        ping_val = round(s.results.ping, 2)

        with data_lock:
            ping_status["download"] = download
            ping_status["upload"] = upload

        save_speedtest(datetime.datetime.now().isoformat(), download, upload, ping_val)
        print(f"[{datetime.datetime.now().isoformat()}] Speedtest salvo -> D: {download} Mbps, U: {upload} Mbps, Ping: {ping_val} ms")

    except Exception as e:
        print("Erro no speedtest:", e)