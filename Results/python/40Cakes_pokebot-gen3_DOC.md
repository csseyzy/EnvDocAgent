# pokebot-gen3 Deployment Document

## Platform

- **Base Image:** python:3.13-bookworm
- **Python Version:** 3.13

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0=2.26.5+dfsg-1 \
    libsdl2-dev=2.26.5+dfsg-1 \
    libzip4=1.7.3-1+b1 \
    libpng16-16=1.6.39-2 \
    libedit2=3.1-20221030-2 \
    libelf1=0.188-2.1 \
    unzip=6.0-28 \
    wget=1.21.3-1+b2
```

## Build Steps

```bash
cd /app/project
python3 -m venv .venv
source .venv/bin/activate

pip install \
    confz==2.0.1 \
    "numpy~=2.1.0" \
    setuptools \
    "ruamel.yaml~=0.18.2" \
    "pypresence~=4.3.0" \
    "obsws-python~=1.6.0" \
    "discord-webhook~=1.2.1" \
    "rich~=13.5.2" \
    "cffi~=1.17.1" \
    "Pillow~=10.4.0" \
    "sounddevice~=0.4.6" \
    "pyperclip3~=0.4.1" \
    "plyer~=2.1.0" \
    "notify-py~=0.3.42" \
    "apispec~=6.3.0" \
    "ttkthemes~=3.2.2" \
    "darkdetect~=0.8.0" \
    "show-in-file-manager~=1.1.4" \
    "aiohttp~=3.10.9" \
    "aiortc~=1.10.0"

# Download libmgba-py
wget -q "https://github.com/hanzi/libmgba-py/releases/download/0.2.0-2/libmgba-py_0.2.0_ubuntu-lunar.zip" -O /tmp/libmgba.zip
unzip -o /tmp/libmgba.zip -d /app/project/
```

## Test Steps

```bash
source .venv/bin/activate
# Only ROM-free tests can pass:
python -m unittest discover -s tests -p "test_map.py" -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- **This project is fundamentally untestable without proprietary ROM files.** The ROMs (Pokemon Emerald, Ruby, FireRed) are copyrighted Nintendo property and cannot be distributed.
- Of 6 test files, only `test_map.py` (pure calculation tests, no emulator) can run without ROMs
- The remaining 5 test files (39 test methods generating 72 parameterized errors) all require save states that reference ROMs
- Recommend marking as **partially testable** — only `test_map.py` is viable
