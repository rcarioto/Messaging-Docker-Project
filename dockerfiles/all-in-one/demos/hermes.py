#!/usr/bin/env python3
from flask import Flask, request, jsonify
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
import json, os, time

app = Flask(__name__)
BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
producer = None

def get_producer():
    global producer
    if producer is None:
        for _ in range(60):
            try:
                producer = KafkaProducer(
                    bootstrap_servers=BOOTSTRAP,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
                return producer
            except Exception as e:
                print("Waiting for Kafka:", e, flush=True)
                time.sleep(2)
        raise RuntimeError("Kafka unavailable")
    return producer

@app.get("/health")
def health():
    return jsonify(status="ok", service="hermes-demo", kafka=BOOTSTRAP)

@app.get("/")
def index():
    return jsonify(service="Hermes-style REST over Kafka", post="/topics/<topic>")

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
        print("topic ensure:", e, flush=True)
    get_producer().send(topic, payload)
    get_producer().flush()
    return jsonify(ok=True, topic=topic, payload=payload)

if __name__ == "__main__":
    print("Hermes demo listening on :8086", flush=True)
    app.run(host="0.0.0.0", port=8086, threaded=True)
