#!/bin/bash
set -e
# Bind ActiveMQ connectors for external access
sed -i 's/127.0.0.1/0.0.0.0/g' "$ACTIVEMQ_HOME/conf/jetty.xml" || true
exec "$ACTIVEMQ_HOME/bin/activemq" console
