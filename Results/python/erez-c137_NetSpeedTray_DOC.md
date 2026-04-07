# NetSpeedTray Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Python: 3.12 (system Python). README says 3.11+.
- This is a **Windows-only** application (uses pywin32, WMI, ctypes.windll, winreg). Testing on Linux requires stubbing Windows-only modules.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    python3=3.12.3-0ubuntu2 python3-pip=24.0+dfsg-1ubuntu1.1 python3-venv=3.12.3-0ubuntu2 python3-dev=3.12.3-0ubuntu2 \
    build-essential=12.10ubuntu1 pkg-config=1.8.1-2build1 \
    libgl1 libglib2.0-0 libxkbcommon0 libdbus-1-3 \
    libegl1 libfontconfig1 \
    xvfb=2:21.1.12-1ubuntu1
```




## Build Steps

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip setuptools wheel
./.venv/bin/pip install numpy pandas matplotlib pillow psutil pyqt6 pytest pytest-mock freezegun parameterized
```

## Test Steps

```bash
MPLBACKEND=Agg QT_QPA_PLATFORM=offscreen PYTHONPATH=$PWD/src \
    ./.venv/bin/python -m pytest -v
```


## Unexpected Issues

- **Windows-native application.** `pywin32` and `wmi` are listed in requirements.txt but cannot install on Linux. Must install individual packages manually.
- **6 failing tests** in settings-related tests due to `utils/styles.get_accent_color()` fallback path raising `AttributeError` on non-Windows.
- **`conftest.py` stubs required** to mock Windows-only modules (winreg, win32api, ctypes.windll, etc.).
- **`MPLBACKEND=Agg`** and **`QT_QPA_PLATFORM=offscreen`** required for headless environments.
- **`PYTHONPATH=src`** required -- the project is not a distributable package; it's run directly via `python src/monitor.py`.
