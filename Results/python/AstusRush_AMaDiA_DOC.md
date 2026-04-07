# AMaDiA Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Python: 3.12 (system Python). Originally designed for Python 3.7 but works on 3.12 with warnings.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    python3=3.12.3-0ubuntu2 python3-pip=24.0+dfsg-1ubuntu1.1 python3-venv=3.12.3-0ubuntu2 build-essential=12.10ubuntu1 \
    xvfb=2:21.1.12-1ubuntu1 \
    libgl1 libx11-6 libxext6 libxrender1=1:0.9.10-1.1build1 libxcb1 libxkbcommon-x11-0 \
    libx11-xcb1 libsm6 libglib2.0-0 libfontconfig1 libfreetype6 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
    libxcb-render-util0 libxcb-xinerama0 libxcb-shm0 libxcb-shape0 \
    libxcb-sync1 libxcb-xfixes0 libxcb-xkb1 libxrandr2 libxi6 \
    libxcursor1 libxcomposite1 libxdamage1 \
    libnss3=2:3.98-1build1 libnspr4 libxtst6 libdbus-1-3 libasound2t64
```


```bash
python3 -m venv /opt/venv
. /opt/venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install PyQtWebEngine
```


## Build Steps
```
export MPLBACKEND=Agg QT_QPA_PLATFORM=offscreen XDG_RUNTIME_DIR=/tmp QTWEBENGINE_DISABLE_SANDBOX=1

python3 -c "import sympy, numpy, matplotlib, scipy; print('Core scientific stack OK')"
QT_QPA_PLATFORM=offscreen python3 -c "import PyQt5; from PyQt5 import QtWidgets; app=QtWidgets.QApplication([]); print('PyQt5 OK')"
XDG_RUNTIME_DIR=/tmp QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 \
    python3 -c "from PyQt5.QtWebEngineWidgets import QWebEngineView; print('PyQtWebEngine OK')"
```
## Test Steps

```bash

XDG_RUNTIME_DIR=/tmp QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 \
    timeout 5s python3 AMaDiA.py
```



## Unexpected Issues

- **PyQtWebEngine not in requirements.txt.** Must be installed separately. The bundled `AGeLib` module imports `QWebEngineView`.
- **Many system libs needed for Qt/WebEngine.** The xcb, NSS, ALSA, DBus, Xtst libraries are all required at runtime even in offscreen mode.
- **SyntaxWarnings on Python 3.12** -- invalid escape sequences in several files. Non-fatal.
- **`QT_QPA_PLATFORM=offscreen`** and **`QTWEBENGINE_DISABLE_SANDBOX=1`** required for headless environments.
- **No formal test suite.** Validation is via smoke tests only.
- **No source code modifications needed.**
