import threading
from ping_loop import ping_loop
from api import create_app
from database import init_db
from config import INTERFACES

# memória compartilhada
ping_data = {iface: [] for iface in INTERFACES}
ping_status = {iface: {"current_ping": 0, "download": 0, "upload": 0} for iface in INTERFACES}
data_lock = threading.Lock()

# DB
init_db()

# start loop (single thread iterates sobre interfaces)
t = threading.Thread(target=ping_loop, args=(data_lock, ping_status, ping_data), daemon=True)
t.start()

# start flask
app = create_app(ping_status, ping_data, data_lock)
app.run(host="0.0.0.0", port=5000)
