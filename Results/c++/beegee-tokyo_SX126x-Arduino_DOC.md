# SX126x-Arduino Deployment Document

## Platform

- **Base Image:** ubuntu:20.04
- **Build System:** arduino-cli (cross-compilation)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.25.1-1ubuntu3 \
    python3.8 \
    python3-pip \
    wget=1.20.3-1ubuntu2 \
    curl=7.68.0-1ubuntu2 \
    unzip \
    tar \
    ca-certificates=20230311ubuntu0.20.04.1

update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
```

## Build Steps

```bash
# Install arduino-cli 0.11.0
mkdir -p /app/project/bin
export PATH=$PATH:/app/project/bin
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh -s 0.11.0

# Clone CI helper repository
git clone --depth 1 https://github.com/RAKWireless/WisBlock-CI.git /app/project/ci

# Run CI install script (installs board cores)
export GITHUB_WORKSPACE=/app/project
bash ci/actions_install.sh

# Initialize arduino-cli
arduino-cli config init && arduino-cli core update-index
```

## Test Steps

```bash
export GITHUB_WORKSPACE=/app/project
mkdir -p /root/Arduino/libraries

# Build for each platform:
python3 ci/build_platform.py esp32
python3 ci/build_platform.py nrf52840
python3 ci/build_platform.py esp8266
python3 ci/build_platform.py nrf52832
```

## Unexpected Issues

- This is not a traditional C++ project — it's an Arduino library requiring `arduino-cli` and cross-compilation
- No unit tests exist; verification is successful compilation for each target platform
- The CI helper repo (`WisBlock-CI`) provides the `build_platform.py` script and `actions_install.sh`
- `GITHUB_WORKSPACE` environment variable must be set (CI-specific)
- Installing board cores (ESP32, nRF52, etc.) is time-consuming and accounts for most of the build time
