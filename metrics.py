import subprocess
import datetime
import speedtest  # pip install speedtest-cli
from database import save_speedtest

def ping_host(target_host, interface=None):
    """
    Faz ping para target_host usando a interface especificada (opcional).
    Retorna latency em ms ou None em timeout/erro.
    """
    try:
        cmd = ["ping", "-c", "1", "-W", "1"]
        if interface:
            cmd += ["-I", interface]
        cmd.append(target_host)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            for part in result.stdout.split():
                if "time=" in part:
                    try:
                        return float(part.split("time=")[1].replace("ms", ""))
                    except:
                        return float(part.split("=")[1])
        return None
    except Exception:
        return None

def medir_speedtest(iface, data_lock, ping_status):
    """
    Mede download/upload/ping via speedtest-cli (módulo Python).
    Observação: não força uso de interface. Pode usar rota padrão do sistema.
    """
    try:
        s = speedtest.Speedtest()
        s.get_best_server()
        download = round(s.download() / 1_000_000, 2)
        upload = round(s.upload() / 1_000_000, 2)
        ping_val = round(s.results.ping, 2)

        with data_lock:
            ping_status[iface]["download"] = download
            ping_status[iface]["upload"] = upload

        save_speedtest(iface, datetime.datetime.now().isoformat(), download, upload, ping_val)
        print(f"[{datetime.datetime.now().isoformat()}] {iface} speedtest salvo -> D:{download} Mbps U:{upload} Mbps Ping:{ping_val} ms")
    except Exception as e:
        print(f"Erro no speedtest {iface}:", e)
