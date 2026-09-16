#!/bin/bash

# Messaging Middleware Docker Stack Startup Script
# This script starts all messaging middleware services

set -e

echo "🚀 Starting Messaging Middleware Docker Stack"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories if they don't exist
echo "📁 Creating necessary directories..."
mkdir -p data/{activemq,rabbitmq,zookeeper,kafka,redis,pulsar,nats,zeromq,rocketmq,emqx,artemis}
mkdir -p config/{activemq,rabbitmq,kafka,redis,pulsar,nats,zeromq,rocketmq,emqx,artemis}

# Set proper permissions
echo "🔐 Setting proper permissions..."
chmod -R 755 data/
chmod -R 755 config/

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose pull

# Start all services
echo "🔄 Starting all services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Display service URLs and credentials
echo ""
echo "🌐 Service URLs and Credentials"
echo "================================"
echo ""
echo "📊 ActiveMQ Classic:"
echo "   - Web Console: http://localhost:8161/admin"
echo "   - Username: admin"
echo "   - Password: admin"
echo "   - Ports: 61616 (OpenWire), 61613 (STOMP), 1883 (MQTT), 5672 (AMQP)"
echo ""
echo "🐰 RabbitMQ:"
echo "   - Management UI: http://localhost:15672"
echo "   - Username: guest"
echo "   - Password: guest"
echo "   - Ports: 5672 (AMQP), 15672 (Management)"
echo ""
echo "📈 Apache Kafka:"
echo "   - Kafka UI: http://localhost:8080"
echo "   - Ports: 9092 (Kafka), 2181 (Zookeeper)"
echo ""
echo "🔴 Redis:"
echo "   - Redis Commander: http://localhost:8081"
echo "   - Port: 6379"
echo ""
echo "⭐ Apache Pulsar:"
echo "   - Web Admin: http://localhost:8080"
echo "   - Ports: 6650 (Pulsar), 8080 (Web Admin)"
echo ""
echo "🛰️  NATS:"
echo "   - Monitor: http://localhost:8222"
echo "   - Ports: 4222 (NATS), 8222 (HTTP Monitor)"
echo ""
echo "🚀 Apache RocketMQ:"
echo "   - Dashboard: http://localhost:8082"
echo "   - Ports: 9876 (NameServer), 10909 (Broker)"
echo ""
echo "📡 EMQ X (MQTT):"
echo "   - Dashboard: http://localhost:18083"
echo "   - Ports: 1883 (MQTT), 8883 (MQTT/SSL), 8083 (MQTT/WebSocket)"
echo ""
echo "🎭 Apache Artemis:"
echo "   - Web Console: http://localhost:8161/console"
echo "   - Ports: 61616 (OpenWire), 61613 (STOMP), 8161 (Web Console)"
echo ""

# Check if services are healthy
echo "🏥 Health Check Status:"
echo "======================="

services=("activemq" "rabbitmq" "kafka" "redis" "pulsar" "nats" "rocketmq-namesrv" "emqx" "artemis")

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Not running"
    fi
done

echo ""
echo "🎉 Messaging Middleware Stack is ready!"
echo ""
echo "📝 Next steps:"
echo "   - Open the web consoles to explore the services"
echo "   - Check the samples/ directory for example code"
echo "   - Run tests with: ./tests/run_tests.sh"
echo ""
echo "🛑 To stop all services: docker-compose down"
echo "📋 To view logs: docker-compose logs -f"
echo "🔧 To restart a service: docker-compose restart <service-name>"
echo ""

# Optional: Start monitoring
if [ "$1" = "--monitor" ]; then
    echo "📊 Starting monitoring mode..."
    docker-compose logs -f
fi 