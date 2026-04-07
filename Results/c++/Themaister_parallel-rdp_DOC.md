# parallel-rdp Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Build System:** CMake

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    build-essential=12.10ubuntu1 \
    cmake=3.28.3-1build7 \
    xorg-dev=1:7.7+23ubuntu3 \
    libvulkan-dev=1.3.275.0-1build1 \
    vulkan-tools=1.3.275.0-1build1 \
    vulkan-validationlayers=1.3.275.0-1 \
    mesa-vulkan-drivers=24.0.9-0ubuntu0.3 \
    libvulkan1=1.3.275.0-1build1 \
    python3=3.12.3-0ubuntu2
```

## Build Steps

```bash
cd /app/project
git submodule update --init --recursive
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release --parallel
```

## Test Steps

```bash
cd /app/project/build
# Run tests in PARALLEL for significant speedup:
ctest --output-on-failure -j$(nproc) 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- Tests use software Vulkan (llvmpipe) in Docker — much slower than GPU
- Each test takes ~10-14 seconds on software renderer vs ~1-2s on real GPU
- **Use `ctest -j$(nproc)`** to run tests in parallel — reduces from ~58 min to ~5-10 min
- With real GPU passthrough (`--gpus all`), total ~5 min sequential
