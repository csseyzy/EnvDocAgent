# ok-end-field Deployment Document

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

1. Apply the same ok-script Linux shims (pure-Python `Box.py`, `Logger` shim in `ok/__init__.py`)
2. Filter `requirements.txt` to remove Windows-only packages:
```bash
grep -v -E '^(pywin32|pycaw|pydirectinput|comtypes|ok-d3dshot|mouse)' requirements.txt > requirements.linux.txt
```
3. Tests import from `src.config` and `ok.test.TaskTestCase` which depend on the full ok-script framework


```bash
cd /app/project
pip install --upgrade pip==24.0 setuptools==69.5.1 wheel==0.43.0
pip install Cython==3.0.10
pip install numpy==2.2.6 opencv-python==4.12.0.88
pip install pillow==11.3.0 psutil==7.0.0
pip install PySide6-Essentials==6.9.1 PySide6-Fluent-Widgets==1.8.3
pip install PySideSix-Frameless-Window==0.7.3 darkdetect==0.8.0
pip install typing-extensions==4.14.1 requests==2.32.4
pip install pyappify==1.0.2 packaging==25.0
pip install shapely==2.1.1 pyclipper==1.3.0.post6
pip install onnxocr-ppocrv5==0.0.14
pip install imagehash==4.3.2 scikit-image==0.26.0
pip install ultralytics==8.3.187

# Install ok-script from source with Linux shims applied:
pip install git+https://github.com/ok-oldking/ok-script.git@main --no-build-isolation
```

## Test Steps

```bash
cd /app/project
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- Tests depend on game screenshot images in `tests/images/` and the full ok-script task execution framework
- `ok-script` itself requires Cython compilation and has Windows-only deps
- `onnxocr-ppocrv4==0.0.5` (in `requirements.in`) vs `onnxocr-ppocrv5==0.0.14` (in `requirements.txt`) — version mismatch between files
