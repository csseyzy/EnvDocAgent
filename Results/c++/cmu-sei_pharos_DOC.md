# pharos Deployment Document

## Platform

- Docker Engine (constraint: exact version not specified by upstream; requires support for docker pull and docker run)

## Prerequisites

```
- Docker Engine (constraint: exact version not specified by upstream; requires support for docker pull and docker run)
```

## Build Steps

```bash
# 1. Pull the pre-built Pharos image
docker pull ghcr.io/cmu-sei/pharos

# 2. Verify tools are available in the image
# Show the path to apianalyzer
docker run --rm ghcr.io/cmu-sei/pharos which apianalyzer

# Deterministic help check for apianalyzer (prints OK on success)
docker run --rm ghcr.io/cmu-sei/pharos sh -lc "apianalyzer --help | head -n 1 | grep -q 'apianalyzer' && echo OK"

# Show the path to ooanalyzer
docker run --rm ghcr.io/cmu-sei/pharos which ooanalyzer

# Deterministic help check for ooanalyzer (prints OK on success)
docker run --rm ghcr.io/cmu-sei/pharos sh -lc "ooanalyzer --help | head -n 1 | grep -q 'ooanalyzer' && echo OK"

# 3. Optional: start an interactive tools container shell (useful for manual exploration)
# docker run --rm -it ghcr.io/cmu-sei/pharos bash


```

## Test Steps


See verification commands in Build Steps.

## Unexpected Issues

- `docker: command not found` — Docker not installed.
- `Got permission denied while trying to connect to the Docker daemon socket` — current user not in docker group. Fix with `sudo usermod -aG docker $USER && newgrp docker`.
- `pull access denied for ghcr.io/cmu-sei/pharos` — typo in image name or network issue. Ensure the image name is exactly `ghcr.io/cmu-sei/pharos` and retry.
