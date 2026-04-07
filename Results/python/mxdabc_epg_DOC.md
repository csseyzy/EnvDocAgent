# epg Deployment Document

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
python3 -m pip install --no-cache-dir --upgrade pip
python3 -m pip install --no-cache-dir -r requirements.txt
```

Key dependencies from `requirements.txt`:
- asgiref==3.7.2
- beautifulsoup4==4.12.2
- Django==4.2.4
- requests==2.31.0
- python-dateutil==2.8.2
- sqlparse==0.4.4

## Test Steps

```bash
cd /app/project/utils/zhtools
python3 -m unittest test_langconv -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- The test file uses `from langconv import *` which requires the working directory to be `utils/zhtools/` (or that directory on `PYTHONPATH`)
- Django's `manage.py test` will NOT discover this test because it is outside any Django app directory
- The `ALLOWED_HOSTS` in settings.py only lists specific domains
