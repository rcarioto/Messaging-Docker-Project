#!/bin/bash
set -euo pipefail

CLUSTER_ID_FILE=/var/lib/kafka/cluster.id
CONFIG=/opt/kafka/config/kraft/server.properties

# Advertise both in-container and host-friendly listeners
cat > "$CONFIG" <<'EOF'
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@localhost:9093
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
advertised.listeners=PLAINTEXT://localhost:9092
inter.broker.listener.name=PLAINTEXT
controller.listener.names=CONTROLLER
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
log.dirs=/var/lib/kafka/kraft-combined-logs
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
num.partitions=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
group.initial.rebalance.delay.ms=0
EOF

if [ ! -f "$CLUSTER_ID_FILE" ]; then
  /opt/kafka/bin/kafka-storage.sh random-uuid > "$CLUSTER_ID_FILE"
  /opt/kafka/bin/kafka-storage.sh format -t "$(cat "$CLUSTER_ID_FILE")" -c "$CONFIG"
fi

exec /opt/kafka/bin/kafka-server-start.sh "$CONFIG"
