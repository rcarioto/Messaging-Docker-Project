# Messaging Middleware Docker Project

This project provides a comprehensive Docker container setup with multiple open-source messaging middleware applications for development, testing, and learning purposes.

There are **two ways** to run messaging software from this project:

| Path | What it is | When to use |
|---|---|---|
| **All-in-one image** | Single container on Docker Hub | Quick local lab (Redis, ActiveMQ, RabbitMQ, Kafka, NATS, demos) |
| **Compose stack** | Many containers from this repo | Full set of brokers (Pulsar, RocketMQ, EMQX, Artemis, DDS demos, …) |

**Full pull/run details:** **[docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)**  
- All-in-one image: [`rcarioto/messaging-lab`](https://hub.docker.com/r/rcarioto/messaging-lab)  
- This Compose repo: [`rcarioto/Messaging-Docker-Project`](https://github.com/rcarioto/Messaging-Docker-Project)

## Included Messaging Middleware

### 1. **Apache ActiveMQ** (v5.17.6)
- **Type**: Message Broker
- **Protocols**: JMS, AMQP, MQTT, STOMP, OpenWire
- **Features**: Message persistence, clustering, security
- **Port**: 61616 (OpenWire), 61613 (STOMP), 1883 (MQTT), 5672 (AMQP)
- **Web Console**: http://localhost:8161/admin (admin/admin)

### 2. **RabbitMQ** (v3.12)
- **Type**: Message Broker
- **Protocols**: AMQP, MQTT, STOMP
- **Features**: Message routing, clustering, management UI
- **Port**: 5672 (AMQP), 15672 (Management UI)
- **Web Console**: http://localhost:15672 (guest/guest)

### 3. **Apache Kafka** (v3.6.1)
- **Type**: Distributed Streaming Platform
- **Protocols**: Kafka Protocol
- **Features**: High-throughput, fault-tolerant, real-time streaming
- **Port**: 9092 (Kafka), 2181 (Zookeeper)
- **Web Console**: http://localhost:8080 (Kafka UI)

### 4. **Redis** (v7.2)
- **Type**: In-Memory Data Store with Pub/Sub
- **Protocols**: Redis Protocol
- **Features**: Pub/Sub messaging, caching, persistence
- **Port**: 6379
- **Web Console**: http://localhost:8081 (Redis Commander)

### 5. **Apache Pulsar** (v3.2.2)
- **Type**: Distributed Pub-Sub Messaging System
- **Protocols**: Pulsar Protocol, Kafka Protocol
- **Features**: Multi-tenancy, geo-replication, streaming
- **Port**: 6650 (Pulsar), 8080 (Web Admin)
- **Web Console**: http://localhost:8080 (Pulsar Admin)

### 6. **NATS** (v2.10.7)
- **Type**: Cloud Native Messaging System
- **Protocols**: NATS Protocol
- **Features**: Lightweight, high-performance, simple
- **Port**: 4222 (NATS), 8222 (HTTP Monitor)
- **Web Console**: http://localhost:8222 (NATS Monitor)

### 7. **ZeroMQ** (v4.3.5)
- **Type**: High-Performance Asynchronous Messaging Library
- **Protocols**: ZMQ Protocol
- **Features**: Socket patterns, high throughput, low latency
- **Port**: Various (depending on pattern)

### 8. **Apache RocketMQ** (v5.1.4)
- **Type**: Distributed Messaging and Streaming Platform
- **Protocols**: RocketMQ Protocol
- **Features**: High availability, high throughput, distributed
- **Port**: 9876 (NameServer), 10909 (Broker)
- **Web Console**: http://localhost:8080 (RocketMQ Dashboard)

### 9. **Hermes** (Allegro)
- **Type**: Message Broker built on Kafka
- **Protocols**: REST API, Kafka Protocol
- **Features**: Reliable, fault-tolerant REST interface, adaptive push mechanisms
- **Port**: 8086 (HTTP API), 8087 (Management API), 8088 (Frontend)
- **Web Console**: http://localhost:8088 (Hermes Frontend)

### 10. **SimpleMQ**
- **Type**: Simple Message Queue System
- **Protocols**: HTTP API
- **Features**: Real-time messaging, easy setup, no complex configurations
- **Port**: 5000 (HTTP API)
- **Web Console**: http://localhost:5000 (SimpleMQ API)

### 11. **Zyre** (Demo)
- **Type**: Distributed Messaging Framework (ZeroMQ-based)
- **Protocols**: ZMQ Protocol
- **Features**: Peer-to-peer messaging, service discovery, group messaging
- **Port**: 5670 (Zyre port)
- **Note**: Demo application showing Zyre capabilities

### 12. **Chronicle Queue** (Demo)
- **Type**: High-Performance Persisted Messaging Library
- **Protocols**: Java API
- **Features**: Ultra-low latency, high throughput, persistence
- **Note**: Demo application showing Chronicle Queue capabilities

### 13. **OpenDDS** (Demo)
- **Type**: Data Distribution Service (DDS) Implementation
- **Protocols**: DDS Protocol
- **Features**: Real-time data distribution, QoS policies, type safety
- **Note**: Demo application showing OpenDDS capabilities

### 14. **Fast DDS** (Demo)
- **Type**: eProsima Fast DDS Implementation
- **Protocols**: DDS Protocol
- **Features**: High-performance DDS, Python bindings, real-time systems
- **Note**: Demo application showing Fast DDS capabilities

## Quick Start

### Prerequisites
- Docker Engine or Docker Desktop
- Docker Compose (v2: `docker compose`)
- About **6–8 GB RAM** for the all-in-one image, or **8 GB+** for the full Compose stack

### Option A — All-in-one image (recommended for most users)

**Pull the image from Docker Hub first**, then run it. Compose is not used for this path.

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

Ports, credentials, and smoke tests: **[docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)**.

### Option B — Full multi-container Compose stack

Clone this repo, then start Compose. A separate pull of `rcarioto/messaging-lab` is **not** required for this path — Compose pulls each service image (and builds custom demos) from the definitions in `docker-compose.yml`.

Optional but recommended: pull published images first so downloads finish before containers start:

```bash
git clone https://github.com/rcarioto/Messaging-Docker-Project.git
cd Messaging-Docker-Project

docker compose pull          # refresh/pre-download Hub images
docker compose up -d --build # start stack; build local demo images

docker compose ps
docker compose logs -f
```

Or use `./start.sh`, which creates `data/` / `config/` dirs, runs `docker compose pull`, then `docker compose up -d`.

### Individual Service Management

```bash
# Start specific service
docker-compose up -d activemq

# Stop specific service
docker-compose stop kafka

# Restart specific service
docker-compose restart rabbitmq
```

## Service URLs and Credentials

| Service | URL | Username | Password | Default Port |
|---------|-----|----------|----------|--------------|
| ActiveMQ Admin | http://localhost:8161/admin | admin | admin | 8161 |
| RabbitMQ Management | http://localhost:15672 | guest | guest | 15672 |
| Kafka UI | http://localhost:8080 | - | - | 8080 |
| Redis Commander | http://localhost:8081 | - | - | 8081 |
| Pulsar Admin | http://localhost:8080 | - | - | 8080 |
| NATS Monitor | http://localhost:8222 | - | - | 8222 |
| RocketMQ Dashboard | http://localhost:8082 | - | - | 8082 |
| Hermes Frontend | http://localhost:8088 | - | - | 8088 |
| SimpleMQ API | http://localhost:5000 | - | - | 5000 |

## Connection Examples

### ActiveMQ (JMS)
```java
// JMS Connection
ConnectionFactory factory = new ActiveMQConnectionFactory("tcp://localhost:61616");
Connection connection = factory.createConnection();
```

### RabbitMQ (AMQP)
```python
import pika
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
```

### Kafka
```java
// Kafka Producer
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
```

### Redis (Pub/Sub)
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.publish('channel', 'message')
```

### NATS
```go
import "github.com/nats-io/nats.go"
nc, _ := nats.Connect("nats://localhost:4222")
```

### Hermes
```bash
# REST API
curl -X POST http://localhost:8086/topics/my-topic \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from Hermes"}'
```

### SimpleMQ
```python
import requests
response = requests.post('http://localhost:5000/send', 
                        json={'message': 'Hello from SimpleMQ'})
```

### Zyre
```python
import zyre
node = zyre.Zyre("my-node")
node.start()
node.join("my-group")
node.shout("my-group", "Hello from Zyre")
```

### Chronicle Queue
```java
SingleChronicleQueue queue = SingleChronicleQueueBuilder.single("/tmp/my-queue").build();
ExcerptAppender appender = queue.acquireAppender();
appender.writeText("Hello from Chronicle Queue");
```

### DDS (OpenDDS/Fast DDS)
```cpp
// C++ example for DDS
DDS::DomainParticipantFactory_var dpf = TheParticipantFactoryWithArgs(argc, argv);
DDS::DomainParticipant_var participant = dpf->create_participant(42, PARTICIPANT_QOS_DEFAULT, 0, 0);
```

## Configuration

Each service has its configuration in the respective directories:
- `config/activemq/` - ActiveMQ configuration
- `config/rabbitmq/` - RabbitMQ configuration
- `config/kafka/` - Kafka configuration
- `config/redis/` - Redis configuration
- `config/pulsar/` - Pulsar configuration
- `config/nats/` - NATS configuration
- `config/rocketmq/` - RocketMQ configuration

## Monitoring and Management

### Health Checks
```bash
# Check all services health
docker-compose ps

# Check specific service logs
docker-compose logs activemq
```

### Resource Usage
```bash
# Monitor resource usage
docker stats
```

## Development and Testing

### Sample Applications
The `samples/` directory contains example applications for each messaging platform:
- Java examples for ActiveMQ, Kafka, RabbitMQ
- Python examples for Redis, NATS
- Go examples for NATS, ZeroMQ
- Node.js examples for all platforms

### Performance Testing
Use the included performance testing scripts in `tests/` directory:
```bash
# Run performance tests
./tests/run_performance_tests.sh
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports are not used by other services
2. **Memory Issues**: Increase Docker memory allocation
3. **Permission Issues**: Check file permissions in config directories

### Logs and Debugging
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs activemq

# Follow logs in real-time
docker-compose logs -f rabbitmq
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Apache Software Foundation
- Pivotal Software (RabbitMQ)
- Redis Labs
- NATS.io
- Apache Pulsar Community
- Apache RocketMQ Community 