# MatrixPilot Deployment Document

## Platform

- OS: Ubuntu 24.04
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.10ubuntu1 \
    make=4.3-4.1build2 \
    graphviz=2.42.2-9ubuntu0.1 \
    default-jre \
    python3=3.12.3-0ubuntu2.1 python3-pip=24.0+dfsg-1ubuntu1.3 \
    pkg-config=1.8.1-2build1 \
    wget=1.21.4-1ubuntu4 curl=8.5.0-2ubuntu10.8 unzip=6.0-28ubuntu4 \
    sed findutils
```

- `build-essential` (gcc-13 13.3.0, g++-13 13.3.0) — C/C++ toolchain for SIL host build
- `graphviz` (2.42.2) — `dot` used by state machine graph generation rules
- `default-jre` (OpenJDK 21.0.10+7) — Java runtime for `Tools/Smc.jar` (State Machine Compiler)
- `python3` (3.12.3) — optional scripting support

## Build Steps

```bash
git clone --depth 1 https://github.com/MatrixPilot/MatrixPilot.git /app/project
cd /app/project
mkdir -p build && cd build
make -f ../makefile -j$(nproc)
```

## Test Steps

```bash
cd /app/project/build
timeout 5s ./MatrixPilot-SIL.out
```

## Unexpected Issues

- Many `-Waddress-of-packed-member` warnings from MAVLink headers during build. Build still succeeds.
- SIL binary expects external simulator connections (X-Plane/HILSIM); no output in headless CI is expected.
- Firmware targets (UDB/AUAV) require Microchip XC16 toolchain, not available in this container. Only SIL host build is feasible.
