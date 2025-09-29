import threading
from database import init_db
from api import create_app  # api.py será atualizado depois; mantém mesma assinatura
from config import INTERFACES

# Estruturas em memória por interface
ping_data = { name: [] for name in INTERFACES.keys() }
ping_status = {
    name: {"current_ping": 0, "download": 0, "upload": 0}
    for name in INTERFACES.keys()
}
data_lock = threading.Lock()

# Inicializa banco e tabelas
init_db()

# Não iniciamos ainda os loops; ping_loop.py será implementado depois.
# Criamos a app Flask que receberá essas estruturas quando api.py for atualizado.
app = create_app(ping_status, ping_data, data_lock)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
