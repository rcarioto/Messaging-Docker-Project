FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 \
    ACTIVEMQ_HOME=/opt/activemq \
    KAFKA_HOME=/opt/kafka \
    NATS_HOME=/opt/nats \
    PATH=/opt/kafka/bin:/opt/nats:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# System packages: Java, Redis, RabbitMQ, Python demos, supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-11-jre-headless \
        redis-server \
        rabbitmq-server \
        supervisor \
        curl \
        ca-certificates \
        python3 \
        python3-pip \
        python3-flask \
        netcat-openbsd \
        procps \
        gnupg \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir kafka-python gevent

# ActiveMQ Classic
ARG ACTIVEMQ_VERSION=5.17.6
RUN curl -fsSL "https://archive.apache.org/dist/activemq/${ACTIVEMQ_VERSION}/apache-activemq-${ACTIVEMQ_VERSION}-bin.tar.gz" \
      | tar -xz -C /opt \
    && mv "/opt/apache-activemq-${ACTIVEMQ_VERSION}" /opt/activemq \
    && useradd -r -s /sbin/nologin activemq \
    && chown -R activemq:activemq /opt/activemq

# Apache Kafka (KRaft, no ZooKeeper)
ARG KAFKA_VERSION=3.6.1
ARG SCALA_VERSION=2.13
RUN curl -fsSL "https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz" \
      | tar -xz -C /opt \
    && mv "/opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION}" /opt/kafka \
    && mkdir -p /var/lib/kafka/kraft-combined-logs \
    && useradd -r -s /sbin/nologin kafka \
    && chown -R kafka:kafka /opt/kafka /var/lib/kafka

# NATS Server
ARG NATS_VERSION=2.10.7
RUN curl -fsSL "https://github.com/nats-io/nats-server/releases/download/v${NATS_VERSION}/nats-server-v${NATS_VERSION}-linux-amd64.tar.gz" \
      | tar -xz -C /opt \
    && mv "/opt/nats-server-v${NATS_VERSION}-linux-amd64" /opt/nats \
    && chmod +x /opt/nats/nats-server

# Redis / RabbitMQ config tweaks for container use
RUN sed -i 's/^bind 127.0.0.1.*/bind 0.0.0.0/' /etc/redis/redis.conf \
    && sed -i 's/^protected-mode yes/protected-mode no/' /etc/redis/redis.conf \
    && sed -i 's/^daemonize yes/daemonize no/' /etc/redis/redis.conf \
    && printf '%s\n' \
         'listeners.tcp.default = 5675' \
         'management.tcp.port = 15672' \
         'management.tcp.ip = 0.0.0.0' \
         'loopback_users.guest = false' \
         'default_user = guest' \
         'default_pass = guest' \
       > /etc/rabbitmq/rabbitmq.conf \
    && rabbitmq-plugins enable --offline rabbitmq_management

# Demos + supervisor config
COPY demos/ /opt/demos/
COPY scripts/ /opt/scripts/
COPY supervisord.conf /etc/supervisor/conf.d/messaging.conf
RUN chmod +x /opt/scripts/*.sh /opt/demos/*.py \
    && mkdir -p /var/log/supervisor /data/chronicle

# Default ports (main brokers on standard ports; RabbitMQ AMQP on 5675)
EXPOSE \
    6379 \
    5672 8161 61613 61616 1883 \
    5675 15672 \
    9092 \
    4222 8222 \
    5000 8086

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=5 \
  CMD curl -sf http://127.0.0.1:15672/ >/dev/null \
   && curl -sf http://127.0.0.1:5000/health >/dev/null \
   && redis-cli ping | grep -q PONG \
   || exit 1

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
