FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential procps \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir cyclonedds

WORKDIR /app

# DDS demo using CycloneDDS Python bindings (OMG DDS; Fast DDS-compatible concepts)
RUN cat > /app/fastdds_demo.py <<'PY'
import time
from dataclasses import dataclass
from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.pub import DataWriter
from cyclonedds.idl import IdlStruct
from cyclonedds.idl.annotations import key

@dataclass
class DemoMsg(IdlStruct, typename="DemoMsg"):
    text: str

print("Starting Fast DDS-style DDS demo (CycloneDDS)...")
participant = DomainParticipant(0)
topic = Topic(participant, "DemoTopic", DemoMsg)
writer = DataWriter(participant, topic)
print("DDS participant/writer created successfully")
n = 0
while True:
    n += 1
    msg = DemoMsg(text=f"Hello from DDS demo #{n}")
    writer.write(msg)
    print("Published:", msg.text)
    time.sleep(10)
PY

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD pgrep -f fastdds_demo.py || exit 1
CMD ["python3", "/app/fastdds_demo.py"]
