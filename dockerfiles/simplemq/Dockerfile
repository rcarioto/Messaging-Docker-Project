FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir flask gevent

WORKDIR /app

# Self-contained SimpleMQ-style in-memory HTTP queue (gevent)
RUN cat > /app/server.py <<'PY'
from flask import Flask, request, jsonify
from collections import defaultdict, deque
import threading

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
    from gevent.pywsgi import WSGIServer
    print("Starting SimpleMQ on :5000")
    WSGIServer(("0.0.0.0", 5000), app).serve_forever()
PY

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:5000/health || exit 1
CMD ["python3", "/app/server.py"]
