# ApertusVR Deployment Document

## Platform

- OS: Ubuntu 24.04
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.10ubuntu1 \
    cmake=3.28.3-1ubuntu3 \
    clang-14 \
    libc++-14-dev \
    libc++abi-14-dev \
    pkg-config=1.8.1-2build1 \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libx11-dev=2:1.8.7-1build1 libxrandr-dev libxi-dev libxinerama-dev libxcursor-dev libxxf86vm-dev \
    libsdl2-dev
export CC=clang-14
export CXX=clang++-14
```

## Build Steps

```bash
git clone --depth 1 https://github.com/MTASZTAKI/ApertusVR.git /app/apertusvr
cd /app/apertusvr
mkdir -p build && cd build
cmake ..
cmake --build . -j$(nproc)
```

## Test Steps

```bash
cd /app/apertusvr/build
ctest --output-on-failure
```


## Unexpected Issues

- Clang 14 required: CMakeLists.txt requires Clang. Set `CC=clang-14` and `CXX=clang++-14`.

