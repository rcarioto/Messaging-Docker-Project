# Troubleshooting: Host cannot reach Docker published ports (Avahi / `docker0`)

This note covers a host networking failure seen with the `messaging-lab` container (and any other container that publishes ports). Brokers can be healthy **inside** Docker while tools on the host fail against `localhost`.

## Symptoms

- Container is up and healthy, e.g. `docker ps` shows `messaging-lab` as `Up … (healthy)`.
- Processes inside the container work:
  ```bash
  docker exec messaging-lab redis-cli ping          # PONG
  docker exec messaging-lab supervisorctl status  # redis/kafka/… RUNNING
  ```
- From the **host**, published ports look open but clients fail:
  - Redis: `Timeout reading from localhost:6379`, `Connection reset by peer`
  - Kafka / KafkaClient: `Disconnected: connection reset by peer`, `Failed to get metadata: Local: Broker transport failure`, hints about `advertised.listeners`
  - HTTP checks to other published ports (e.g. `5000`, `15672`) also fail or hang
- TCP connect to `127.0.0.1:6379` or `:9092` may succeed (Docker’s `docker-proxy` accepts the socket), then the protocol handshake times out or resets.

These look like Redis/Kafka misconfiguration, but they are usually **host ↔ Docker bridge** problems.

## What the issue actually is

Docker’s default bridge (`docker0`) should own something like:

```text
inet 172.17.0.1/16  … docker0
```

with containers on `172.17.0.0/16` and port publishing (`-p 6379:6379`, `-p 9092:9092`, …) forwarded through that bridge.

**Avahi** (mDNS / Zeroconf on Linux) can attach a link-local IPv4 address to `docker0` when the normal Docker address is missing, for example:

```text
inet 169.254.x.x/16  … docker0:avahi
```

When that happens:

1. Docker still expects gateway `172.17.0.1` (see `docker network inspect bridge`).
2. The host interface only has Avahi’s `169.254…` address (and `docker0` may even show as `DOWN` / `NO-CARRIER`).
3. Published ports still appear in `ss` / `netstat` via `docker-proxy`.
4. Traffic from host tools never reliably reaches the process in the container → timeouts and “connection reset by peer”.

Inside the container network namespace, brokers keep working, which is why `docker exec …` succeeds while `localhost` from the host fails.

## Quick diagnosis

```bash
ip -4 addr show docker0
docker network inspect bridge --format '{{json .IPAM.Config}}'
```

**Broken (typical):**

```text
# docker0 only has Avahi link-local, missing 172.17.0.1
inet 169.254.13.197/16 … docker0:avahi

# but Docker still thinks the bridge is 172.17.0.0/16
[{"Subnet":"172.17.0.0/16","Gateway":"172.17.0.1"}]
```

**Healthy:**

```text
inet 172.17.0.1/16 … docker0
```

Also compare:

```bash
docker exec messaging-lab redis-cli ping          # should be PONG
redis-cli -h 127.0.0.1 -p 6379 ping             # fails when docker0 is broken
```

## Immediate repair

Restore the Docker bridge, restart Docker, then start the lab again:

```bash
sudo ip link set docker0 up
sudo ip addr flush dev docker0
sudo systemctl restart docker

docker start messaging-lab
# If the container was removed after the daemon restart, recreate it:
# docker run -d --name messaging-lab --shm-size=1g \
#   -p 6379:6379 -p 61616:61616 -p 61613:61613 -p 1883:1883 -p 5672:5672 -p 8161:8161 \
#   -p 5675:5675 -p 15672:15672 -p 9092:9092 -p 4222:4222 -p 8222:8222 \
#   -p 5000:5000 -p 8086:8086 \
#   rcarioto/messaging-lab:latest
```

Verify:

```bash
ip -4 addr show docker0    # expect 172.17.0.1/16
redis-cli -h 127.0.0.1 -p 6379 ping
```

## Lasting fix

Stop Avahi from managing `docker0` (preferred if you still want `.local` / printer discovery), or disable Avahi if you do not need mDNS.

### Option A — Keep Avahi, ignore Docker interfaces

```bash
sudo cp /etc/avahi/avahi-daemon.conf /etc/avahi/avahi-daemon.conf.bak

# Ensure Avahi ignores docker/veth bridges (under [server])
grep -q 'deny-interfaces=docker0' /etc/avahi/avahi-daemon.conf || \
  sudo sed -i '/^\[server\]/a deny-interfaces=docker0,docker1,br-+,veth*' /etc/avahi/avahi-daemon.conf

sudo systemctl restart avahi-daemon
```

Then run the **Immediate repair** steps once so `docker0` is healthy again.

### Option B — Disable Avahi entirely

Use this on a lab/server machine that does not need mDNS:

```bash
sudo systemctl stop avahi-daemon
sudo systemctl disable avahi-daemon
sudo systemctl stop avahi-daemon.socket 2>/dev/null || true
sudo systemctl disable avahi-daemon.socket 2>/dev/null || true
```

Then run the **Immediate repair** steps.

### What Avahi is

Avahi implements **mDNS / DNS-SD** (similar to Apple Bonjour): resolving names like `hostname.local` and discovering printers or shares on the LAN. Many Docker-focused workstations do not need it.

## After repair: smoke tests for messaging-lab

```bash
redis-cli -h 127.0.0.1 -p 6379 ping
curl -s http://127.0.0.1:5000/health
curl -s http://127.0.0.1:8222/varz | head

# Kafka (example with KafkaClient + venv)
# source ~/messaging_tools/mq_env/bin/activate
# python KafkaClient.py 127.0.0.1:9092 --topic-list
```

If in-container checks pass but host checks still fail, re-check `ip -4 addr show docker0` for `172.17.0.1/16`.
