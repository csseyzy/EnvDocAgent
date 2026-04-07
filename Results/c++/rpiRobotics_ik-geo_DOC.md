# ik-geo Deployment Document

## Platform

- OS: Ubuntu 24.04
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.10ubuntu1 \
    curl=8.5.0-2ubuntu10.8 \
    python3=3.10.6-1~22.04.1 python3-pip=24.0+dfsg-1ubuntu1.1 python3-dev=3.12.3-0ubuntu2 python3-venv=3.12.3-0ubuntu2 \
    cargo=1.75.0 rustc=1.75.0
```

```bash
pip3 install --break-system-packages numpy==2.4.3 scipy==1.17.1 linearSubproblemSltns==1.0.3
```

## Build Steps

```bash
git clone --depth 1 https://github.com/rpiRobotics/ik-geo.git /app/ik_geo
```

## Test Steps

```bash
cd /app/ik_geo/python
python3 run_all.py
```

## Unexpected Issues

- PEP 668 on Ubuntu 24.04: `pip3 install` requires `--break-system-packages` flag.
- SP6 test failure: `TypeError` in `linearSubproblemSltns==1.0.3` (`sp6_lib.py:102`), not a project defect.
