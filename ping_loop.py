import time
import datetime
from metrics import ping_host, medir_speedtest

# Cada rede tem seu próprio buffer de pings (últimos 300 registros)
def ping_loop(data_lock, ping_status, ping_data):
    buffers = {rede: {"ping": [], "download": [], "upload": []} for rede in ping_status}
    last_avg_calc = time.time()

    while True:
        for rede, host in ping_status.items():
            latency = ping_host(host)
            if latency is None:
                latency = 0  # Marca queda da rede

            with data_lock:
                ping_status[rede]["current_ping"] = latency
                ping_data[rede].append({
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "latency": latency
                })
                # Mantém só os últimos 300 registros
                if len(ping_data[rede]) > 300:
                    ping_data[rede].pop(0)

                buffers[rede]["ping"].append(latency)

        # Calcula médias a cada 5 minutos
        if time.time() - last_avg_calc > 300:
            for rede in ping_status:
                avg_ping = round(sum(buffers[rede]["ping"]) / len(buffers[rede]["ping"]), 2) if buffers[rede]["ping"] else 0
                # Aqui você pode salvar em DB se quiser
                buffers[rede]["ping"].clear()
            last_avg_calc = time.time()

        # Executa speedtest a cada 10 min (exemplo)
        for rede in ping_status:
            medir_speedtest(data_lock, ping_status, rede)

        time.sleep(1)
