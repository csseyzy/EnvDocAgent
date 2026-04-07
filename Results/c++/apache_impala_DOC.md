# impala Deployment Document

## Platform

- Docker 24.0.7

## Prerequisites

```
- Linux (runs on Linux systems only)
- Docker 24.0.7
- Docker Compose 2.20.2
- Git (tested with 2.34.1)
```

## Build Steps

```bash
# 1. Clone project
git clone https://github.com/apache/impala.git
cd impala

# 2. Create Docker network for quickstart
docker network create -d bridge quickstart-network || true

# 3. Configure environment variables for quickstart
export QUICKSTART_IP=$(docker network inspect quickstart-network -f '{{(index .IPAM.Config 0).Gateway}}')
export QUICKSTART_LISTEN_ADDR=$QUICKSTART_IP
export IMPALA_QUICKSTART_IMAGE_PREFIX="apache/impala:81d5377c2-"

# 4. Start services with Docker Compose
docker-compose -f docker/quickstart.yml up -d

# 5. Wait for services to initialize
sleep 30

```

## Test Steps

```
docker-compose -f docker/quickstart.yml exec catalogd impala-shell -i "$QUICKSTART_IP" -q "select 1;"
```

## Unexpected Issues

- `docker-compose: command not found` — Docker Compose plugin not installed. Install the Docker Compose v2 plugin on Debian/Ubuntu.
- `network with name quickstart-network already exists` — Network was created previously. Remove and recreate the network.
- `impala-shell: command not found` inside container — services not fully initialized. Wait 30-60s and retry.
- `Can't connect to Impala at $QUICKSTART_IP` (connection refused) — services not ready or environment variables not set. Ensure `QUICKSTART_IP` is set and services are Up.
- `Port 25000 is already in use` — another service is using the impalad web UI port. Free the port and restart.
