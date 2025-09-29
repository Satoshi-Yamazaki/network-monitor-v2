import os

# Arquivo de banco e pasta de logs
DB_FILE = os.path.join("logs", "monitor.db")
LOG_DIR = "logs"

# Hosts alvo para ping (um por rede, pode ser igual)
HOSTS = {
    "prefeitura": "8.8.8.8",
    "conectada": "1.1.1.1"
}

# Mapear nomes lógicos para interfaces do sistema
INTERFACES = {
    "prefeitura": "enp0s3",
    "conectada": "enp0s8"
}
