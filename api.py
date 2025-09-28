from flask import Flask, jsonify, render_template # type: ignore
from database import contar_quedas
from config import HOST

def create_app(ping_status, ping_data, data_lock):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html", host=HOST)

    @app.route("/data")
    def data():
        with data_lock:
            stats = contar_quedas()
            return jsonify({
                "ping": ping_data,
                "current_ping": ping_status["current_ping"],
                "download": ping_status["download"],
                "upload": ping_status["upload"],
                "stats": stats
            })

    return app
