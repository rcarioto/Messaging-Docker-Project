# New Messaging Services Added

This document summarizes the new messaging middleware services that have been added to the Docker Compose stack.

## 🆕 New Services Overview

### 1. **Hermes** (Allegro)
- **Repository**: https://github.com/allegro/hermes
- **Type**: Message broker built on top of Kafka
- **Ports**: 8086 (HTTP API), 8087 (Management API), 8088 (Frontend)
- **Features**: 
  - Reliable, fault-tolerant REST interface
  - Adaptive push mechanisms for message sending
  - Built on Apache Kafka for scalability
  - Web-based management interface
- **Dependencies**: Requires Kafka and Zookeeper
- **Demo**: Python client example in `samples/hermes/`

### 2. **SimpleMQ**
- **Repository**: https://github.com/vitorluis/SimpleMQ
- **Type**: Simple message queue system
- **Port**: 5000 (HTTP API)
- **Features**:
  - Real-time messaging with HTTP API
  - Easy setup and configuration
  - No complex broker setup required
  - Perfect for simple messaging needs
- **Demo**: Python client example in `samples/simplemq/`

### 3. **Zyre** (Demo)
- **Type**: Distributed messaging framework (ZeroMQ-based)
- **Port**: 5670
- **Features**:
  - Peer-to-peer messaging
  - Service discovery
  - Group messaging capabilities
  - Built on ZeroMQ for high performance
- **Note**: Demo application showing Zyre capabilities
- **Demo**: Python example in `samples/zyre/`

### 4. **Chronicle Queue** (Demo)
- **Type**: High-performance persisted messaging library
- **Features**:
  - Ultra-low latency messaging
  - High throughput
  - Persistence to disk
  - Java-based implementation
- **Note**: Demo application showing Chronicle Queue capabilities
- **Demo**: Java example in `samples/chronicle/`

### 5. **OpenDDS** (Demo)
- **Type**: Data Distribution Service (DDS) implementation
- **Features**:
  - Real-time data distribution
  - QoS policies
  - Type safety
  - C++ implementation
- **Note**: Demo application showing OpenDDS capabilities
- **Demo**: C++ example in container

### 6. **Fast DDS** (Demo)
- **Type**: eProsima Fast DDS implementation
- **Features**:
  - High-performance DDS
  - Python bindings
  - Real-time systems support
  - Modern DDS implementation
- **Note**: Demo application showing Fast DDS capabilities
- **Demo**: Python example in `samples/dds/`

## 🐳 Docker Configuration

### Dockerfiles Created
- `dockerfiles/hermes/Dockerfile` - Hermes message broker
- `dockerfiles/simplemq/Dockerfile` - SimpleMQ server
- `dockerfiles/zyre/Dockerfile` - Zyre demo application
- `dockerfiles/chronicle/Dockerfile` - Chronicle Queue demo
- `dockerfiles/dds/opendds/Dockerfile` - OpenDDS demo
- `dockerfiles/dds/fastdds/Dockerfile` - Fast DDS demo

### Docker Compose Services Added
```yaml
# Hermes
hermes:
  build: ./dockerfiles/hermes
  ports: ["8086:8080", "8087:8081", "8088:8082"]
  depends_on: [kafka, zookeeper]

# SimpleMQ
simplemq:
  build: ./dockerfiles/simplemq
  ports: ["5000:5000"]

# Zyre Demo
zyre:
  build: ./dockerfiles/zyre
  ports: ["5670:5670"]

# Chronicle Queue Demo
chronicle:
  build: ./dockerfiles/chronicle
  volumes: ["./data/chronicle:/tmp/chronicle-demo"]

# OpenDDS Demo
opendds:
  build: ./dockerfiles/dds/opendds

# Fast DDS Demo
fastdds:
  build: ./dockerfiles/dds/fastdds
```

## 📝 Sample Applications

### Python Examples
- `samples/hermes/hermes_client.py` - Hermes REST API client
- `samples/simplemq/simplemq_client.py` - SimpleMQ HTTP client
- `samples/zyre/zyre_demo.py` - Zyre peer-to-peer messaging demo
- `samples/dds/dds_demo.py` - Fast DDS Python demo

### Java Examples
- `samples/chronicle/ChronicleDemo.java` - Chronicle Queue demo

### Dependencies
- Updated `samples/requirements.txt` with new Python dependencies
- Added Chronicle Queue Maven dependencies

## 🧪 Testing

### Test Script
- `tests/test_new_services.sh` - Comprehensive test script for new services
- Tests container health, HTTP endpoints, and demo applications
- Provides colored output and detailed status reporting

### Manual Testing
```bash
# Test Hermes
curl http://localhost:8086/health
curl http://localhost:8088

# Test SimpleMQ
curl http://localhost:5000

# Test demo applications
docker exec zyre ps aux | grep zyre_demo.py
docker exec chronicle ps aux | grep ChronicleDemo
docker exec opendds ps aux | grep demo
docker exec fastdds ps aux | grep fastdds_demo.py
```

## 🔧 Configuration

### Environment Variables
- Hermes: `SPRING_PROFILES_ACTIVE=docker`
- All services use default configurations for demo purposes

### Volumes
- Chronicle Queue: `./data/chronicle:/tmp/chronicle-demo`
- Other services use in-memory or default storage

### Networks
- All services connected to `messaging-network`
- Internal communication between services

## 📚 Documentation Updates

### README.md
- Added new services to "Included Messaging Middleware" section
- Updated service URLs and credentials table
- Added connection examples for new services
- Updated port mappings

### QUICK_START.md
- Added new services to web interface table
- Added examples for testing new services
- Added test script for new services

## 🚀 Getting Started

### Start New Services
```bash
# Start all new services
docker-compose up -d hermes simplemq zyre chronicle opendds fastdds

# Or start all services including new ones
docker-compose up -d
```

### Test New Services
```bash
# Run comprehensive test
./tests/test_new_services.sh

# Or test individual services
docker-compose logs hermes
docker-compose logs simplemq
```

### Access Web Interfaces
- Hermes Frontend: http://localhost:8088
- SimpleMQ API: http://localhost:5000

## 🔍 Troubleshooting

### Common Issues
1. **Hermes not starting**: Ensure Kafka and Zookeeper are running first
2. **Build failures**: Check Docker has enough memory (8GB+ recommended)
3. **Port conflicts**: Verify ports 8086-8088, 5000, 5670 are available
4. **Demo apps not running**: Check container logs for Python/Java errors

### Logs
```bash
# View logs for new services
docker-compose logs hermes
docker-compose logs simplemq
docker-compose logs zyre
docker-compose logs chronicle
docker-compose logs opendds
docker-compose logs fastdds
```

## 📈 Performance Notes

- **Hermes**: Built on Kafka, suitable for high-throughput scenarios
- **SimpleMQ**: Lightweight, good for simple messaging needs
- **Zyre**: Peer-to-peer, no central broker required
- **Chronicle Queue**: Ultra-low latency, high throughput
- **DDS implementations**: Real-time, deterministic messaging

## 🔮 Future Enhancements

- Add more DDS implementations (OpenSplice, RTI Connext)
- Include MumMQ when available
- Add more comprehensive demo applications
- Performance benchmarking scripts
- Integration tests between services 