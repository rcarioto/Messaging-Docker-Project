# Messaging Lab — Usage Guide

Pull one Docker image and run the main message brokers locally for development and testing.

**Image:** [rcarioto/messaging-lab](https://hub.docker.com/r/rcarioto/messaging-lab) (`rcarioto/messaging-lab:latest`)

**Requirements:** Docker Engine or Docker Desktop with about **6–8 GB RAM** available to Docker.

---

## Quick start

```bash
docker pull rcarioto/messaging-lab:latest

docker run --rm --name messaging-lab --shm-size=1g \
  -p 6379:6379 \
  -p 61616:61616 -p 61613:61613 -p 1883:1883 -p 5672:5672 -p 8161:8161 \
  -p 5675:5675 -p 15672:15672 \
  -p 9092:9092 \
  -p 4222:4222 -p 8222:8222 \
  -p 5000:5000 -p 8086:8086 \
  rcarioto/messaging-lab:latest
```

Stop it with `Ctrl+C`, or if it was started detached (`-d`):

```bash
docker stop messaging-lab
```

If port `6379` is already in use (for example a host Redis), stop that service first or map Redis to another host port (e.g. `-p 6380:6379`).

---

## What is included

| Software | Role | Host port(s) | UI / notes |
|---|---|---|---|
| **Redis** | Cache / pub-sub | `6379` | `redis-cli -h localhost ping` |
| **ActiveMQ Classic** | JMS / multi-protocol broker | `61616` OpenWire, `61613` STOMP, `1883` MQTT, `5672` AMQP, `8161` console | http://localhost:8161/admin — `admin` / `admin` |
| **RabbitMQ** | AMQP broker | `5675` AMQP, `15672` management | http://localhost:15672 — `guest` / `guest` |
| **Kafka** (KRaft) | Streaming log | `9092` | No separate ZooKeeper |
| **NATS** | Lightweight messaging | `4222`, monitor `8222` | http://localhost:8222 |
| **SimpleMQ** demo | HTTP in-memory queue | `5000` | http://localhost:5000/health |
| **Hermes-style** demo | REST → Kafka | `8086` | http://localhost:8086/health |

RabbitMQ AMQP is on **5675** so ActiveMQ can use the standard AMQP port **5672**.

---

## How to test

### Redis
```bash
redis-cli -h localhost -p 6379 ping
redis-cli -h localhost -p 6379 PUBLISH demo "hello"
```

### RabbitMQ
```bash
curl -u guest:guest http://localhost:15672/api/overview
# AMQP clients: host=localhost port=5675
```

### ActiveMQ
```bash
curl -u admin:admin http://localhost:8161/admin/
# OpenWire: tcp://localhost:61616
# MQTT:    tcp://localhost:1883
```

### Kafka
```bash
docker exec messaging-lab kafka-topics.sh --bootstrap-server localhost:9092 --list
docker exec messaging-lab kafka-topics.sh --bootstrap-server localhost:9092 \
  --create --topic test --partitions 1 --replication-factor 1
docker exec messaging-lab bash -c \
  'echo "hello-kafka" | kafka-console-producer.sh --bootstrap-server localhost:9092 --topic test'
docker exec messaging-lab kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic test --from-beginning --timeout-ms 5000
```

### NATS
```bash
curl -s http://localhost:8222/varz | head
# Clients: nats://localhost:4222
```

### SimpleMQ
```bash
curl -s http://localhost:5000/health
curl -s -X POST http://localhost:5000/send \
  -H 'Content-Type: application/json' \
  -d '{"queue":"demo","message":"hi"}'
curl -s http://localhost:5000/receive/demo
```

### Hermes-style (REST → Kafka)
```bash
curl -s http://localhost:8086/health
curl -s -X POST http://localhost:8086/topics/demo \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello from hermes"}'
```

---

## Full multi-container stack

This GitHub repo also defines a Docker Compose layout that runs a larger set of brokers as individual containers (Pulsar, RocketMQ, EMQX, Artemis, DDS demos, and more). It needs about **8 GB+ RAM**.

You do **not** need to pull `rcarioto/messaging-lab` for this path. Clone the repo and let Compose pull/build service images:

```bash
git clone https://github.com/rcarioto/Messaging-Docker-Project.git
cd Messaging-Docker-Project
docker compose pull
docker compose up -d --build
```

See `README.md` and `QUICK_START.md` for service URLs and credentials.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Port already allocated | Stop the conflicting host process, or change the left-hand side of `-p HOST:CONTAINER` |
| Container unhealthy / OOM | Give Docker more RAM (6–8 GB+); check `docker logs messaging-lab` |
| `permission denied` on Docker socket | Add your user to the `docker` group, then re-login |
| Wrong Docker context | `docker context use default` |

```bash
docker logs messaging-lab
docker exec messaging-lab supervisorctl status
```
