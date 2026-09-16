# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Prerequisites
- Docker and Docker Compose installed
- At least 8GB RAM available for Docker
- Internet connection for downloading images

### 2. Start the Stack
```bash
# Clone or download this project
git clone https://github.com/rcarioto/Messaging-Docker-Project.git
cd Messaging-Docker-Project

# Make scripts executable (if not already done)
chmod +x start.sh tests/run_tests.sh

# Start all messaging middleware services
./start.sh
```

### 3. Verify Everything Works
```bash
# Run the comprehensive test suite
./tests/run_tests.sh
```

## 🌐 Access Your Services

Once started, you can access the web interfaces at:

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| **ActiveMQ** | http://localhost:8161/admin | admin | admin |
| **RabbitMQ** | http://localhost:15672 | guest | guest |
| **Kafka UI** | http://localhost:8080 | - | - |
| **Redis Commander** | http://localhost:8081 | - | - |
| **Pulsar Admin** | http://localhost:8080 | - | - |
| **NATS Monitor** | http://localhost:8222 | - | - |
| **RocketMQ Dashboard** | http://localhost:8082 | - | - |
| **EMQ X Dashboard** | http://localhost:18083 | - | - |
| **Hermes Frontend** | http://localhost:8088 | - | - |
| **SimpleMQ API** | http://localhost:5000 | - | - |

## 📝 Try the Examples

### Python Examples
```bash
# Install dependencies
pip install -r requirements.txt

# Run Redis Pub/Sub example
cd samples/python
python3 redis_pubsub.py

# Run RabbitMQ example
python3 rabbitmq_example.py
```

### Java Examples
```bash
# Compile and run Kafka example
cd samples/java
javac -cp "kafka-clients.jar" KafkaExample.java
java -cp ".:kafka-clients.jar" KafkaExample
```

### Go Examples
```bash
# Install NATS Go client
go get github.com/nats-io/nats.go

# Run NATS example
cd samples/go
go run nats_example.go
```

### Node.js Examples
```bash
# Install dependencies
npm install mqtt

# Run MQTT example
cd samples/nodejs
node mqtt_example.js
```

### New Services Examples
```bash
# Test Hermes (requires Kafka to be running)
cd samples/hermes
python3 hermes_client.py

# Test SimpleMQ
cd samples/simplemq
python3 simplemq_client.py

# Test Zyre demo (ZeroMQ-based messaging)
cd samples/zyre
python3 zyre_demo.py

# Test Chronicle Queue demo (Java)
cd samples/chronicle
javac -cp "chronicle-queue.jar" ChronicleDemo.java
java -cp ".:chronicle-queue.jar" ChronicleDemo

# Test Fast DDS demo
cd samples/dds
python3 dds_demo.py
```

## 🔧 Common Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View service status
docker-compose ps

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart rabbitmq
```

### Individual Service Control
```bash
# Start only Redis
docker-compose up -d redis

# Start only Kafka (includes Zookeeper)
docker-compose up -d zookeeper kafka

# Start only RabbitMQ
docker-compose up -d rabbitmq
```

### Monitoring and Debugging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f kafka

# Check resource usage
docker stats

# Access service shell
docker-compose exec redis redis-cli
docker-compose exec rabbitmq rabbitmqctl status
```

## 🧪 Testing Your Setup

### Quick Health Check
```bash
# Test if services are responding
curl http://localhost:15672  # RabbitMQ
curl http://localhost:8161/admin  # ActiveMQ
curl http://localhost:8080  # Kafka UI
```

### Run Full Test Suite
```bash
# Comprehensive testing
./tests/run_tests.sh
```

### Test New Services
```bash
# Test the newly added services
./tests/test_new_services.sh
```

### Manual Testing
```bash
# Test Redis
redis-cli -h localhost -p 6379 ping

# Test RabbitMQ
curl -u guest:guest http://localhost:15672/api/overview

# Test Kafka
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using a port
   sudo netstat -tulpn | grep :5672
   
   # Stop conflicting service or change ports in docker-compose.yml
   ```

2. **Memory Issues**
   ```bash
   # Increase Docker memory allocation
   # In Docker Desktop: Settings > Resources > Memory
   ```

3. **Service Not Starting**
   ```bash
   # Check logs
   docker-compose logs <service-name>
   
   # Restart service
   docker-compose restart <service-name>
   ```

4. **Permission Issues**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER data/ config/
   chmod -R 755 data/ config/
   ```

### Getting Help

1. Check the service logs: `docker-compose logs <service-name>`
2. Verify Docker has enough resources
3. Ensure no other services are using the same ports
4. Check the full README.md for detailed documentation

## 📚 Next Steps

1. **Explore the Web Interfaces** - Each service has a management UI
2. **Try the Sample Code** - Run examples in the `samples/` directory
3. **Read the Documentation** - Check `README.md` for detailed information
4. **Experiment** - Modify configurations and try different messaging patterns
5. **Scale Up** - Add more instances or configure clustering

## 🎯 What You Can Do Now

- ✅ Send messages between applications using different protocols
- ✅ Explore pub/sub, queue, and streaming patterns
- ✅ Monitor message flows and system health
- ✅ Test different QoS levels and delivery guarantees
- ✅ Compare performance characteristics of different messaging systems
- ✅ Build distributed applications with reliable messaging

Happy messaging! 🚀 