from flask import Flask, request, jsonify
import redis
from rq import Queue
from rq.registry import FailedJobRegistry, FinishedJobRegistry, StartedJobRegistry
from dataset import binance
from binance.client import Client
from flask_cors import CORS, cross_origin
import random
from os import listdir

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'

r = redis.Redis()
q = Queue(connection=r)

months_map = {
    "01": "Jan",
    "02": "Feb",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}


@app.route("/tasks")
def tasks():
    response = {
        'pending': q.get_job_ids()[::-1],
        'finished': FinishedJobRegistry('default', connection=r, queue=q).get_job_ids()[::-1],
        'failed': FailedJobRegistry('default', connection=r, queue=q).get_job_ids()[::-1],
        'running': StartedJobRegistry('default', connection=r, queue=q).get_job_ids()[::-1]
    }
    return jsonify(response)


@app.route("/login", methods=['POST'])
def login():
    payload = request.get_json()
    if payload["email"] == "reddy.nithinpg@gmail.com" and payload["password"] == "12345678":
        return jsonify({"status": True})
    return jsonify({"status": False})


@app.route("/setup", methods=['POST'])
def setup():
    payload = request.get_json()
    if payload["email"] == "reddy.nithinpg@gmail.com" and payload["password"] == "12345678":
        return jsonify({"status": True})
    return jsonify({"status": False})


@app.route("/dataset", methods=['POST'])
def dataset():
    payload = request.get_json()
    d1 = payload["daterange"][0][:10].split("-")
    d2 = payload["daterange"][1][:10].split("-")
    payload["start_date"] = f"{d1[2]} {months_map[d1[1]]}, {d1[0]}"
    payload["end_date"] = f"{d2[2]} {months_map[d2[1]]}, {d2[0]}"

    if payload["exchange"] == "Binance":
        columns = [
            'Open Time',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'Close Time',
            'Quote Asset Volume',
            'Number Of Trades',
            'Taker Buy Base Asset Volume',
            'Taker Buy Quote Asset Volume',
            'Ignore'
        ],
        interval = payload["interval"]
        if interval == "1m":
            payload["interval"] = Client.KLINE_INTERVAL_1MINUTE
        elif interval == "3m":
            payload["interval"] = Client.KLINE_INTERVAL_3MINUTE
        elif interval == "5m":
            payload["interval"] = Client.KLINE_INTERVAL_5MINUTE
        elif interval == "15m":
            payload["interval"] = Client.KLINE_INTERVAL_15MINUTE
        elif interval == "30m":
            payload["interval"] = Client.KLINE_INTERVAL_30MINUTE
        elif interval == "1h":
            payload["interval"] = Client.KLINE_INTERVAL_1HOUR
        elif interval == "2h":
            payload["interval"] = Client.KLINE_INTERVAL_2HOUR
        elif interval == "4h":
            payload["interval"] = Client.KLINE_INTERVAL_4HOUR
        elif interval == "6h":
            payload["interval"] = Client.KLINE_INTERVAL_6HOUR
        elif interval == "8h":
            payload["interval"] = Client.KLINE_INTERVAL_8HOUR
        else:
            return jsonify({"error": True}), 500
        job = q.enqueue(binance, columns=columns, **payload)
        return jsonify({"queued": True, "id": job.id})
    return jsonify({"error": True}), 500


@app.route("/filenames")
def filenames():
    filenames = list(filter(lambda x: x.endswith(".csv"), listdir('data')))
    return jsonify(filenames)


@app.route("/strategies")
def strategies():
    filenames = filter(lambda x: x.endswith(".csv"), listdir('data'))
    return jsonify(filenames)


if __name__ == '__main__':
    app.run(port=5000, debug=True)