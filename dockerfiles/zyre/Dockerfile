FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libzmq3-dev procps \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pyzmq

WORKDIR /app

# Zyre-style peer group messaging demo using ZeroMQ pub/sub
RUN cat > /app/zyre_demo.py <<'PY'
import time
import zmq
import socket
import os

PORT = int(os.environ.get("ZYRE_PORT", "5670"))
GROUP = "demo-group"
NODE = socket.gethostname()

ctx = zmq.Context.instance()
pub = ctx.socket(zmq.PUB)
pub.bind(f"tcp://*:{PORT}")
sub = ctx.socket(zmq.SUB)
sub.connect(f"tcp://127.0.0.1:{PORT}")
sub.setsockopt_string(zmq.SUBSCRIBE, GROUP)
sub.RCVTIMEO = 1000

print(f"Zyre-style node '{NODE}' started on :{PORT}, group={GROUP}")
n = 0
while True:
    n += 1
    msg = f"{GROUP} Hello from Zyre demo node={NODE} msg=#{n}"
    pub.send_string(msg)
    print("Sent:", msg)
    try:
        got = sub.recv_string()
        print("Recv:", got)
    except zmq.Again:
        pass
    time.sleep(5)
PY

EXPOSE 5670
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD pgrep -f zyre_demo.py || exit 1
CMD ["python3", "/app/zyre_demo.py"]
