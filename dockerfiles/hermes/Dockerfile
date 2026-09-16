FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir flask kafka-python

WORKDIR /app

# Lightweight Hermes-style REST front-end over Kafka
RUN cat > /app/hermes_demo.py <<'PY'
from flask import Flask, request, jsonify
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
import json, os, time

app = Flask(__name__)
BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
producer = None

def get_producer():
    global producer
    if producer is None:
        for _ in range(30):
            try:
                producer = KafkaProducer(
                    bootstrap_servers=BOOTSTRAP,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
                return producer
            except Exception as e:
                print("Waiting for Kafka:", e)
                time.sleep(2)
        raise RuntimeError("Kafka unavailable")
    return producer

@app.get("/health")
def health():
    return jsonify(status="ok", service="hermes-demo", kafka=BOOTSTRAP)

@app.get("/")
def index():
    return jsonify(
        service="Hermes-style REST over Kafka",
        endpoints=["POST /topics/<topic>", "GET /health"],
    )

@app.post("/topics/<topic>")
def publish(topic):
    payload = request.get_json(force=True, silent=True) or {"message": request.data.decode("utf-8", "ignore")}
    try:
        admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP, client_id="hermes-demo")
        admin.create_topics([NewTopic(name=topic, num_partitions=1, replication_factor=1)])
        admin.close()
    except TopicAlreadyExistsError:
        pass
    except Exception as e:
        print("topic ensure:", e)
    get_producer().send(topic, payload)
    get_producer().flush()
    return jsonify(ok=True, topic=topic, payload=payload)

if __name__ == "__main__":
    # management/frontend ports answered by same app for demo simplicity
    print("Starting Hermes demo on 8080/8081/8082")
    app.run(host="0.0.0.0", port=8080, threaded=True)
PY

EXPOSE 8080 8081 8082
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8080/health || exit 1
CMD ["python3", "/app/hermes_demo.py"]
