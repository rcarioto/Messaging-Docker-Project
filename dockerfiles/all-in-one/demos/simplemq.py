#!/usr/bin/env python3
from flask import Flask, request, jsonify
from collections import defaultdict, deque
import threading
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
queues = defaultdict(deque)
lock = threading.Lock()

@app.get("/health")
def health():
    return jsonify(status="ok", service="simplemq")

@app.get("/")
def index():
    with lock:
        return jsonify(queues={k: len(v) for k, v in queues.items()})

@app.post("/send")
def send():
    data = request.get_json(force=True, silent=True) or {}
    queue = data.get("queue", "default")
    message = data.get("message", "")
    with lock:
        queues[queue].append(message)
    return jsonify(ok=True, queue=queue, size=len(queues[queue]))

@app.get("/receive/<queue>")
def receive(queue):
    with lock:
        if not queues[queue]:
            return jsonify(message=None), 204
        return jsonify(message=queues[queue].popleft(), queue=queue)

if __name__ == "__main__":
    print("SimpleMQ listening on :5000", flush=True)
    WSGIServer(("0.0.0.0", 5000), app).serve_forever()
