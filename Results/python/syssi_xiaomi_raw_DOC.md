# xiaomi_raw Deployment Document

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
    build-essential=12.10ubuntu1 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install construct==2.10.68 "python-miio>=0.5.12"
python -m pip install homeassistant==2024.4.0
```

## Test Steps

```bash
cd /app/project
python3 -c "import json; json.load(open('custom_components/xiaomi_miio_raw/manifest.json')); print('manifest.json is valid JSON')" 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This project genuinely has no automated Python tests
- The `tests/` directory is misleading — it contains only YAML configuration for manual e2e testing with a physical Xiaomi device
- The CI only runs hassfest and HACS validation, not Python unit tests
- Full testing requires a physical Xiaomi device and Home Assistant runtime
