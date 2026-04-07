# Autopsy-Plugins Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** 3.12

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    python3=3.12.3-0ubuntu2 \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
    python3-venv=3.12.3-0ubuntu2 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
python3 -m pip install --break-system-packages pytest==8.3.4
```

## Test Steps

```bash
cd /app/project/Lat_Long/geographiclib
python3 -m unittest test.test_geodesic -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This is a collection of Autopsy/Jython plugins — most code requires the Autopsy Java platform to run
- The only testable Python code is the vendored `geographiclib` library inside `Lat_Long/`
- The test file imports `from geographiclib.geodesic import Geodesic`, so the working directory must be `Lat_Long/geographiclib` for imports to resolve
- The test file has ~29 test methods (GeodesicTest + PlanimeterTest classes)
