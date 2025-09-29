from flask import Flask, jsonify, render_template
from database import contar_quedas
from config import HOSTS

def create_app(ping_status, ping_data, data_lock):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html", hosts=HOSTS)

    @app.route("/data")
    def data():
        with data_lock:
            stats_prefeitura = contar_quedas("prefeitura")
            stats_conectada = contar_quedas("conectada")

            return jsonify({
                "prefeitura": {
                    "ping": ping_data["prefeitura"],
                    "current_ping": ping_status["prefeitura"]["current_ping"],
                    "download": ping_status["prefeitura"]["download"],
                    "upload": ping_status["prefeitura"]["upload"],
                    "stats": stats_prefeitura
                },
                "conectada": {
                    "ping": ping_data["conectada"],
                    "current_ping": ping_status["conectada"]["current_ping"],
                    "download": ping_status["conectada"]["download"],
                    "upload": ping_status["conectada"]["upload"],
                    "stats": stats_conectada
                }
            })

    return app
