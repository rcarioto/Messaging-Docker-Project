#!/bin/bash

# Test script for new messaging services
# Tests Hermes, SimpleMQ, Zyre, Chronicle Queue, and DDS implementations

set -e

echo "Testing new messaging services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test HTTP endpoint
test_http_endpoint() {
    local service=$1
    local url=$2
    local timeout=${3:-10}
    
    echo -n "Testing $service... "
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Function to test container health
test_container_health() {
    local container=$1
    local timeout=${2:-30}
    
    echo -n "Testing $container container health... "
    
    # Wait for container to be healthy
    local count=0
    while [ $count -lt $timeout ]; do
        if docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null | grep -q "healthy"; then
            echo -e "${GREEN}✓ HEALTHY${NC}"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    echo -e "${RED}✗ UNHEALTHY${NC}"
    return 1
}

# Function to test container running
test_container_running() {
    local container=$1
    
    echo -n "Testing $container container running... "
    
    if docker ps --format "table {{.Names}}" | grep -q "^$container$"; then
        echo -e "${GREEN}✓ RUNNING${NC}"
        return 0
    else
        echo -e "${RED}✗ NOT RUNNING${NC}"
        return 1
    fi
}

# Test results tracking
passed=0
failed=0

echo "=== Testing New Messaging Services ==="

# Test Hermes
if test_container_running "hermes"; then
    passed=$((passed + 1))
    if test_http_endpoint "Hermes API" "http://localhost:8086/health" 15; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
    fi
    if test_http_endpoint "Hermes Frontend" "http://localhost:8088" 15; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
    fi
else
    failed=$((failed + 1))
fi

# Test SimpleMQ
if test_container_running "simplemq"; then
    passed=$((passed + 1))
    if test_http_endpoint "SimpleMQ API" "http://localhost:5000" 15; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
    fi
else
    failed=$((failed + 1))
fi

# Test Zyre (demo container)
if test_container_running "zyre"; then
    passed=$((passed + 1))
    echo -e "${YELLOW}Note: Zyre is a demo application, checking if process is running...${NC}"
    if docker exec zyre ps aux | grep -q "zyre_demo.py"; then
        echo -e "${GREEN}✓ Zyre demo running${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗ Zyre demo not running${NC}"
        failed=$((failed + 1))
    fi
else
    failed=$((failed + 1))
fi

# Test Chronicle Queue (demo container)
if test_container_running "chronicle"; then
    passed=$((passed + 1))
    echo -e "${YELLOW}Note: Chronicle Queue is a demo application, checking if process is running...${NC}"
    if docker exec chronicle ps aux | grep -q "ChronicleDemo"; then
        echo -e "${GREEN}✓ Chronicle Queue demo running${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗ Chronicle Queue demo not running${NC}"
        failed=$((failed + 1))
    fi
else
    failed=$((failed + 1))
fi

# Test OpenDDS (demo container)
if test_container_running "opendds"; then
    passed=$((passed + 1))
    echo -e "${YELLOW}Note: OpenDDS is a demo application, checking if process is running...${NC}"
    if docker exec opendds ps aux | grep -q "demo"; then
        echo -e "${GREEN}✓ OpenDDS demo running${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗ OpenDDS demo not running${NC}"
        failed=$((failed + 1))
    fi
else
    failed=$((failed + 1))
fi

# Test Fast DDS (demo container)
if test_container_running "fastdds"; then
    passed=$((passed + 1))
    echo -e "${YELLOW}Note: Fast DDS is a demo application, checking if process is running...${NC}"
    if docker exec fastdds ps aux | grep -q "fastdds_demo.py"; then
        echo -e "${GREEN}✓ Fast DDS demo running${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗ Fast DDS demo not running${NC}"
        failed=$((failed + 1))
    fi
else
    failed=$((failed + 1))
fi

echo ""
echo "=== Test Summary ==="
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo "Total: $((passed + failed))"

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All new services are working correctly!${NC}"
    exit 0
else
    echo -e "${RED}Some services failed. Check the logs with: docker-compose logs [service-name]${NC}"
    exit 1
fi 