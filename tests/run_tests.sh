#!/bin/bash

# Messaging Middleware Test Suite
# This script tests all messaging middleware services

set -e

echo "🧪 Running Messaging Middleware Test Suite"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test results
print_result() {
    local test_name="$1"
    local status="$2"
    local message="$3"
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC} - $test_name: $message"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} - $test_name: $message"
        ((TESTS_FAILED++))
    fi
}

# Function to test HTTP endpoint
test_http_endpoint() {
    local service_name="$1"
    local url="$2"
    local expected_status="$3"
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        print_result "$service_name HTTP" "PASS" "Endpoint $url is accessible"
        return 0
    else
        print_result "$service_name HTTP" "FAIL" "Endpoint $url is not accessible"
        return 1
    fi
}

# Function to test TCP port
test_tcp_port() {
    local service_name="$1"
    local host="$2"
    local port="$3"
    
    if nc -z "$host" "$port" 2>/dev/null; then
        print_result "$service_name TCP" "PASS" "Port $port is open on $host"
        return 0
    else
        print_result "$service_name TCP" "FAIL" "Port $port is not open on $host"
        return 1
    fi
}

# Function to test Redis
test_redis() {
    echo -e "\n${BLUE}Testing Redis...${NC}"
    
    # Test TCP connection
    test_tcp_port "Redis" "localhost" "6379"
    
    # Test Redis commands
    if command -v redis-cli &> /dev/null; then
        if redis-cli -h localhost -p 6379 ping | grep -q "PONG"; then
            print_result "Redis Commands" "PASS" "Redis is responding to commands"
        else
            print_result "Redis Commands" "FAIL" "Redis is not responding to commands"
        fi
    else
        print_result "Redis Commands" "SKIP" "redis-cli not available"
    fi
    
    # Test HTTP endpoint
    test_http_endpoint "Redis Commander" "http://localhost:8081" "200"
}

# Function to test RabbitMQ
test_rabbitmq() {
    echo -e "\n${BLUE}Testing RabbitMQ...${NC}"
    
    # Test TCP connections
    test_tcp_port "RabbitMQ AMQP" "localhost" "5672"
    test_tcp_port "RabbitMQ Management" "localhost" "15672"
    
    # Test HTTP endpoint
    test_http_endpoint "RabbitMQ Management" "http://localhost:15672" "200"
}

# Function to test Kafka
test_kafka() {
    echo -e "\n${BLUE}Testing Apache Kafka...${NC}"
    
    # Test TCP connections
    test_tcp_port "Zookeeper" "localhost" "2181"
    test_tcp_port "Kafka" "localhost" "9092"
    
    # Test HTTP endpoint
    test_http_endpoint "Kafka UI" "http://localhost:8080" "200"
}

# Function to test ActiveMQ
test_activemq() {
    echo -e "\n${BLUE}Testing Apache ActiveMQ...${NC}"
    
    # Test TCP connections
    test_tcp_port "ActiveMQ OpenWire" "localhost" "61616"
    test_tcp_port "ActiveMQ STOMP" "localhost" "61613"
    test_tcp_port "ActiveMQ MQTT" "localhost" "1883"
    test_tcp_port "ActiveMQ AMQP" "localhost" "5672"
    
    # Test HTTP endpoint
    test_http_endpoint "ActiveMQ Web Console" "http://localhost:8161/admin" "200"
}

# Function to test NATS
test_nats() {
    echo -e "\n${BLUE}Testing NATS...${NC}"
    
    # Test TCP connections
    test_tcp_port "NATS" "localhost" "4222"
    test_tcp_port "NATS Monitor" "localhost" "8222"
    
    # Test HTTP endpoint
    test_http_endpoint "NATS Monitor" "http://localhost:8222" "200"
}

# Function to test Pulsar
test_pulsar() {
    echo -e "\n${BLUE}Testing Apache Pulsar...${NC}"
    
    # Test TCP connections
    test_tcp_port "Pulsar" "localhost" "6650"
    
    # Test HTTP endpoint
    test_http_endpoint "Pulsar Admin" "http://localhost:8080" "200"
}

# Function to test RocketMQ
test_rocketmq() {
    echo -e "\n${BLUE}Testing Apache RocketMQ...${NC}"
    
    # Test TCP connections
    test_tcp_port "RocketMQ NameServer" "localhost" "9876"
    test_tcp_port "RocketMQ Broker" "localhost" "10909"
    
    # Test HTTP endpoint
    test_http_endpoint "RocketMQ Dashboard" "http://localhost:8082" "200"
}

# Function to test EMQ X
test_emqx() {
    echo -e "\n${BLUE}Testing EMQ X...${NC}"
    
    # Test TCP connections
    test_tcp_port "EMQ X MQTT" "localhost" "1883"
    test_tcp_port "EMQ X MQTT/SSL" "localhost" "8883"
    test_tcp_port "EMQ X MQTT/WebSocket" "localhost" "8083"
    
    # Test HTTP endpoint
    test_http_endpoint "EMQ X Dashboard" "http://localhost:18083" "200"
}

# Function to test Artemis
test_artemis() {
    echo -e "\n${BLUE}Testing Apache Artemis...${NC}"
    
    # Test TCP connections
    test_tcp_port "Artemis OpenWire" "localhost" "61616"
    test_tcp_port "Artemis STOMP" "localhost" "61613"
    
    # Test HTTP endpoint
    test_http_endpoint "Artemis Web Console" "http://localhost:8161/console" "200"
}

# Function to test Python examples
test_python_examples() {
    echo -e "\n${BLUE}Testing Python Examples...${NC}"
    
    if command -v python3 &> /dev/null; then
        # Check if required packages are installed
        if python3 -c "import redis, pika" 2>/dev/null; then
            print_result "Python Dependencies" "PASS" "Required packages are installed"
            
            # Test Redis Python example
            if [ -f "../samples/python/redis_pubsub.py" ]; then
                print_result "Python Redis Example" "PASS" "Redis example file exists"
            else
                print_result "Python Redis Example" "FAIL" "Redis example file not found"
            fi
            
            # Test RabbitMQ Python example
            if [ -f "../samples/python/rabbitmq_example.py" ]; then
                print_result "Python RabbitMQ Example" "PASS" "RabbitMQ example file exists"
            else
                print_result "Python RabbitMQ Example" "FAIL" "RabbitMQ example file not found"
            fi
        else
            print_result "Python Dependencies" "FAIL" "Required packages not installed"
        fi
    else
        print_result "Python Examples" "SKIP" "Python3 not available"
    fi
}

# Function to test Java examples
test_java_examples() {
    echo -e "\n${BLUE}Testing Java Examples...${NC}"
    
    if command -v java &> /dev/null; then
        print_result "Java Runtime" "PASS" "Java is available"
        
        # Test Kafka Java example
        if [ -f "../samples/java/KafkaExample.java" ]; then
            print_result "Java Kafka Example" "PASS" "Kafka example file exists"
        else
            print_result "Java Kafka Example" "FAIL" "Kafka example file not found"
        fi
    else
        print_result "Java Examples" "SKIP" "Java not available"
    fi
}

# Function to test Go examples
test_go_examples() {
    echo -e "\n${BLUE}Testing Go Examples...${NC}"
    
    if command -v go &> /dev/null; then
        print_result "Go Runtime" "PASS" "Go is available"
        
        # Test NATS Go example
        if [ -f "../samples/go/nats_example.go" ]; then
            print_result "Go NATS Example" "PASS" "NATS example file exists"
        else
            print_result "Go NATS Example" "FAIL" "NATS example file not found"
        fi
    else
        print_result "Go Examples" "SKIP" "Go not available"
    fi
}

# Function to test Node.js examples
test_nodejs_examples() {
    echo -e "\n${BLUE}Testing Node.js Examples...${NC}"
    
    if command -v node &> /dev/null; then
        print_result "Node.js Runtime" "PASS" "Node.js is available"
        
        # Test MQTT Node.js example
        if [ -f "../samples/nodejs/mqtt_example.js" ]; then
            print_result "Node.js MQTT Example" "PASS" "MQTT example file exists"
        else
            print_result "Node.js MQTT Example" "FAIL" "MQTT example file not found"
        fi
    else
        print_result "Node.js Examples" "SKIP" "Node.js not available"
    fi
}

# Function to test Docker services
test_docker_services() {
    echo -e "\n${BLUE}Testing Docker Services...${NC}"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_result "Docker" "FAIL" "Docker is not running"
        return 1
    fi
    
    print_result "Docker" "PASS" "Docker is running"
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_result "Docker Compose" "FAIL" "Docker Compose not available"
        return 1
    fi
    
    print_result "Docker Compose" "PASS" "Docker Compose is available"
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_result "Docker Services" "PASS" "Services are running"
    else
        print_result "Docker Services" "FAIL" "Services are not running"
        return 1
    fi
}

# Main test execution
main() {
    echo "Starting comprehensive test suite..."
    echo "This may take a few minutes..."
    
    # Test Docker services first
    test_docker_services
    
    # Test all messaging middleware services
    test_redis
    test_rabbitmq
    test_kafka
    test_activemq
    test_nats
    test_pulsar
    test_rocketmq
    test_emqx
    test_artemis
    
    # Test example code
    test_python_examples
    test_java_examples
    test_go_examples
    test_nodejs_examples
    
    # Print summary
    echo -e "\n${BLUE}Test Summary${NC}"
    echo "============"
    echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
    
    local total_tests=$((TESTS_PASSED + TESTS_FAILED))
    if [ $total_tests -gt 0 ]; then
        local success_rate=$((TESTS_PASSED * 100 / total_tests))
        echo -e "${BLUE}Success Rate: $success_rate%${NC}"
    fi
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All tests passed! Your messaging middleware stack is working correctly.${NC}"
        exit 0
    else
        echo -e "\n${YELLOW}⚠️  Some tests failed. Please check the service logs for more details.${NC}"
        echo "Run 'docker-compose logs <service-name>' to view specific service logs."
        exit 1
    fi
}

# Run main function
main 