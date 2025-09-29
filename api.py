from flask import Flask, jsonify, render_template
from database import contar_quedas
from config import INTERFACES, HOST

def create_app(ping_status, ping_data, data_lock):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html", host=HOST)

    @app.route("/data")
    def data():
        with data_lock:
            stats = {iface: contar_quedas(iface) for iface in INTERFACES}
            return jsonify({
                "ping": ping_data,
                "status": ping_status,
                "stats": stats
            })

    return app
