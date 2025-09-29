import threading
from ping_loop import ping_loop
from api import create_app
from database import init_db
from config import HOSTS

ping_data = {rede: [] for rede in HOSTS}
ping_status = {rede: {"current_ping": 0, "download": 0, "upload": 0} for rede in HOSTS}
data_lock = threading.Lock()

init_db()

t = threading.Thread(target=ping_loop, args=(data_lock, ping_status, ping_data), daemon=True)
t.start()

app = create_app(ping_status, ping_data, data_lock)
app.run(host="0.0.0.0", port=5000)
