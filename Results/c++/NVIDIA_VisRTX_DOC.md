# VisRTX (TSD component, no CUDA) Deployment Document

## Platform

- OS: Ubuntu 22.04 (jammy)
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.9ubuntu3 \
    cmake=3.22.1-1ubuntu1.22.04.2 \
    ninja-build=1.11.1-2 \
    wget=1.21.4-1ubuntu4 curl=8.5.0-2ubuntu10.8 \
    libtbb-dev \
    pkg-config=1.8.1-2build1 \
    python3=3.10.6-1~22.04.1
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
```

## Build Steps

```bash
git clone --depth 1 https://github.com/NVIDIA/VisRTX.git /app/project
cd /app/project

# Build third-party dependencies (ANARI-SDK 0.16.0, etc.)
mkdir -p build-deps && cd build-deps
cmake -G Ninja ../tsd/cmake/build_deps -DCMAKE_BUILD_TYPE=Release
cmake --build . --parallel
cd /app/project

# Build TSD
mkdir -p build-tsd && cd build-tsd
cmake -G Ninja ../tsd \
    -DCMAKE_PREFIX_PATH=/app/project/deps \
    -DCMAKE_BUILD_TYPE=Release \
    -DTSD_BUILD_APPS=ON \
    -DTSD_BUILD_INTERACTIVE=OFF \
    -DTSD_USE_CUDA=OFF \
    -DTSD_USE_USD=OFF \
    -DTSD_USE_TBB=OFF \
    -DTSD_USE_UI=OFF
cmake --build . --parallel
```

## Test Steps

```bash
cd /app/project/build-tsd
ctest -C Release --output-on-failure
```

## Unexpected Issues

- Locale error on ANARI-SDK extraction: "Pathname cannot be converted from UTF-8 to current locale." Set `LC_ALL=C.UTF-8` and `LANG=C.UTF-8` before building.
- Missing `python3`: ANARI-SDK CMake requires Python 3. Install explicitly.
- Stale `build-deps`: if dependency build fails midway, remove entirely and rebuild.
