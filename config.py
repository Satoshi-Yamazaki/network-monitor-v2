import os

DB_FILE = os.path.join("logs", "monitor.db")
LOG_DIR = "logs"

# Mapeamento: nome lógico -> interface de rede
INTERFACES = {
    "prefeitura": "enp0s3",
    "conectada": "enp0s8"
}

# Host alvo de ping
HOST = "8.8.8.8"
