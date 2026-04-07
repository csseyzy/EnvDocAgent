# ok-script Deployment Document

## Platform

- **Base Image:** python:3.12-slim-bookworm
- **Python Version:** 3.12

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    gcc=4:12.2.0-3 \
    g++=4:12.2.0-3 \
    libgl1=1.6.0-1 \
    libglib2.0-0=2.74.6-2+deb12u3 \
    libxcb-xinerama0=1.15-1 \
    libxkbcommon0=1.5.0-1 \
    libegl1=1.6.0-1
```

## Build Steps

1. Create `ok/__init__.py` with pure-Python shim exports:
```python
from ok.util.logger import Logger
from ok.feature.Box import Box
```
3. Skip Windows-only deps (`pywin32`, `pycaw`, `pydirectinput`, `comtypes`, `ok-d3dshot`) on Linux


```bash
cd /app/project
pip install --upgrade pip==24.0 setuptools==69.5.1 wheel==0.43.0
pip install Cython==3.0.10
pip install get-pypi-latest-version==0.0.5
pip install numpy==2.2.6 opencv-python==4.12.0.88
pip install PySide6-Essentials==6.9.1 PySide6-Fluent-Widgets==1.8.3
pip install PySideSix-Frameless-Window==0.7.3 darkdetect==0.8.0
pip install typing-extensions==4.14.1 requests==2.32.4 psutil==7.0.0
pip install pyappify==1.0.2
```

## Test Steps

```bash
cd /app/project
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This is fundamentally a **Windows-only** project (`"Operating System :: Microsoft :: Windows"` in setup.py)
- `.pyx` files use `cdef` Cython syntax that cannot be directly imported as Python
- `setup.py` queries PyPI at import time via `GetPyPiLatestVersion`, which fails without network access
- Tests only test `Box` and `Logger` which are portable; the rest of the framework requires Windows APIs
