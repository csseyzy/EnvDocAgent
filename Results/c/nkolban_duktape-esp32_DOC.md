# duktape-esp32 Deployment Document

## Platform

- Base image: `ubuntu:22.04`
- Python: 2.7 (for Duktape configure.py) and 3.10 (for general tooling)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.9ubuntu3 \
    gcc=4:11.2.0-1ubuntu1 \
    git=1:2.34.1-1ubuntu1 \
    libssl-dev=3.0.2-0ubuntu1 \
    libcrypto++-dev=8.6.0-2build1 \
    python2=2.7.18-3 \
    python3=3.10.6-1~22.04 \
    python3-pip=22.0.2+dfsg-1ubuntu0.4 \
    python3-yaml=5.4.1-1ubuntu1
```

## Build Steps


```bash
cd /app/duktape_esp32

# Step 1: Clone duktape into components/
make duktape_install

# Step 2: Configure duktape sources (requires Python 2 + PyYAML)
python2 ./components/duktape/tools/configure.py \
    --rom-support \
    --rom-auto-lightfunc \
    --config-metadata components/duktape/config/ \
    --source-directory components/duktape/src-input \
    --option-file components/duktape/config/examples/low_memory.yaml \
    --option-file data/duktape/ESP32-Duktape.yaml \
    --fixup-file main/include/duktape_fixup.h \
    --output-directory components/duktape/src

# Step 3: Build the Linux native version
cd linux
make clean
make all
```

## Test Steps

```bash
cd /app/duktape_esp32/linux
./esp32-duktape-linux ../tests/fileSystem1.js
echo "Exit code: $?"
```

## Unexpected Issues

- This is an **embedded firmware project** -- the main build cross-compiles for Xtensa ESP32 and cannot produce a runnable binary on x86 Linux
- Only the `linux/` subdirectory produces a native Linux binary (subset of full ESP32 firmware)
- `configure.py` uses Python 2 syntax -- must use `python2` interpreter
- The project is **archived/unmaintained** (last commit ~2018), targets ESP-IDF v3.x which is EOL
- The JavaScript test files in `tests/` are designed for the ESP32 runtime and may not all work on the Linux build
- ESP32-specific modules (WiFi, GPIO, BLE, etc.) are excluded from the Linux build
- `linux/Makefile` links against `-lcrypto` -- requires `libssl-dev`
