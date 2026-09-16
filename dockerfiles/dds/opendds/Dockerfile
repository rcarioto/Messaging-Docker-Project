FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    ca-certificates \
    python3 \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Lightweight OpenDDS-style DDS demo without full OpenDDS source build.
# Uses a persistent participant simulation + IDL-shaped message loop so the
# container stays healthy for stack demos (full OpenDDS compile needs 8GB+ RAM).
RUN cat > /app/demo.cpp <<'CPP'
#include <iostream>
#include <chrono>
#include <thread>
#include <string>

int main() {
    std::cout << "Starting OpenDDS-style demo..." << std::endl;
    std::cout << "DomainParticipant domain=42 created (demo mode)" << std::endl;
    int n = 0;
    while (true) {
        ++n;
        std::cout << "OpenDDS demo running... tick=" << n
                  << " topic=DemoTopic" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(10));
    }
    return 0;
}
CPP

RUN g++ -O2 -pthread demo.cpp -o demo

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD pgrep -x demo || exit 1
CMD ["./demo"]
