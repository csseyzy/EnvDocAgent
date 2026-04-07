# clp Deployment Document

## Platform

- Ubuntu 22.04
- Docker 24.0.7

## Prerequisites

```
- Ubuntu 22.04
- Docker 24.0.7
```

## Build Steps

```bash
# 1. Clone project
git clone https://github.com/y-scope/clp.git
cd clp
# 2. Pull runtime image (core container)
docker pull ghcr.io/y-scope/clp/clp-core-x86-ubuntu-jammy:main
# 3. Initialize data directory
mkdir -p /tmp/clp-data
# 4. Start service (container kept alive)
docker run -d --name clp-core \
  -v /tmp/clp-data:/data \
  ghcr.io/y-scope/clp/clp-core-x86-ubuntu-jammy:main \
  sleep infinity
```
## Test Steps

```
until docker exec clp-core true; do sleep 1; done
```
## Unexpected Issues

- `The container name "clp-core" is already in use` — a container with the same name exists. Remove with `docker rm -f clp-core` and recreate.
- `Cannot connect to the Docker daemon` — Docker service not started. Fix with `sudo systemctl start docker && sudo systemctl enable docker`.
- CMake 4.x not supported when building from source — CMake version >= 4.0.0 is not supported per project constraints. Use CMake 3.23.0 when building natively on Ubuntu 22.04.
- No manual configuration required for the core container quick test. For advanced usage (e.g., building packages, web UI, API server), refer to project documentation.
