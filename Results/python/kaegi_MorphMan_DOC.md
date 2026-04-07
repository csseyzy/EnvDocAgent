# MorphMan Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Python: **3.9** (via `ppa:deadsnakes/ppa`). Pinned to match Anki 2.1.54 compatibility.
- Requires PyQt6-WebEngine which pulls in Chromium and ~15 system shared libraries.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 software-properties-common=0.99.48 libegl1

add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3.9 python3.9-venv python3.9-distutils

apt-get install -y \
    libgl1 libfontconfig1 libxkbcommon0 libxkbcommon-x11-0 libatomic1 \
    libnss3=2:3.98-1build1 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxtst6 \
    libxi6 libasound2t64 libxkbfile1
```





## Build Steps

```bash
python3.9 -m ensurepip --upgrade
python3.9 -m venv /opt/pyenv
. /opt/pyenv/bin/activate
python -m pip install --upgrade pip
python -m pip install "aqt[qt5]==2.1.54" "aqt[qt6]==2.1.54" "anki==2.1.54" "PyQt6-WebEngine" pylint
```

## Test Steps

```bash
export QT_QPA_PLATFORM=minimal
export QTWEBENGINE_DISABLE_SANDBOX=1
export PYTHONPATH=./
. /opt/pyenv/bin/activate
python test.py
```


## Unexpected Issues

- **No standard Python packaging.** No setup.py/pyproject.toml/requirements.txt. Dependencies documented only in README.
- **Requires Python 3.9 specifically** to match Anki 2.1.54 compatibility.
- **PyQt6-WebEngine pulls in Chromium** which needs ~15 system shared libraries not in the base Ubuntu image.
- **`QT_QPA_PLATFORM=minimal`** required for headless Qt execution.
- **`QTWEBENGINE_DISABLE_SANDBOX=1`** required to disable Chromium sandbox in container.
- **MorphMan bundles its own MeCab binary** at `morph/deps/mecab/mecab.lin` -- no system MeCab installation needed.
- **No source code modifications needed.**
