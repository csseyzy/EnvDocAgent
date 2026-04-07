# phasar Deployment Document

## Platform

- Ubuntu 24.04

## Prerequisites

- Ubuntu 24.04
- Docker 24.0
- Git 2.40

## Build Steps

```bash
# 1. Clone project
git clone https://github.com/secure-software-engineering/phasar.git
cd phasar

# 2. Build Docker image with toolchain (enables BuildKit mounts)
DOCKER_BUILDKIT=1 docker buildx build --load -t phasar:clang19-ubuntu24.04 .

# 3. Build project inside the container (artifacts in ./build)
docker run --rm \
  -v "$PWD":/usr/src/phasar \
  -w /usr/src/phasar \
  phasar:clang19-ubuntu24.04 \
  bash -lc 'set -eux; \
    apt-get update; \
    apt-get install -y git=1:2.43.0-1ubuntu7 cmake=3.28.3-1build7 ninja-build; \
    git=1:2.43.0-1ubuntu7 submodule update --init; \
    cmake=3.28.3-1build7 -S . -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_PHASAR_CLANG=OFF \
      -DPHASAR_USE_Z3=ON \
      -DPHASAR_BUILD_MODULES=ON \
      -DPHASAR_LLVM_VERSION=19 \
      -G Ninja; \
    ninja -C build -j$(nproc)'
# Build artifacts located under: ./build

# 4. Install and run example programs (verifies library usage)
docker run --rm \
  -v "$PWD":/usr/src/phasar \
  -w /usr/src/phasar \
  phasar:clang19-ubuntu24.04 \
  bash -lc 'set -eux; \
    cmake -DCMAKE_INSTALL_PREFIX=./INSTALL -P ./build/cmake_install.cmake; \
    PHASAR_ROOT_DIR=$(pwd); \
    cd ./examples/how-to; \
    cmake -S . -B build -Dphasar_ROOT="$PHASAR_ROOT_DIR/INSTALL"; \
    cmake --build ./build --target run_sample_programs; \
    echo examples_ok'

# 5. Run CLI (help) to confirm installation (from mounted workspace)
docker run --rm \
  -v "$PWD":/usr/src/phasar \
  -w /usr/src/phasar \
  phasar:clang19-ubuntu24.04 \
  ./INSTALL/bin/phasar-cli --help

# 6. (Optional) Run unit tests inside the container
docker run --rm \
  -v "$PWD":/usr/src/phasar \
  -w /usr/src/phasar \
  phasar:clang19-ubuntu24.04 \
  bash -lc 'set -eux; cmake --build ./build --target check-phasar-unittests'


```

## Test Steps

```
bash -lc '[ -f build/CMakeCache.txt ] && echo build_ok || (echo build_fail; exit 1)'
```
## Unexpected Issues

- `failed to solve: invalid mount type "bind" only allowed in BuildKit` — Docker BuildKit not enabled. Use `DOCKER_BUILDKIT=1 docker buildx build --load -t phasar:clang19-ubuntu24.04 .`.
- CMake configure/build fails due to missing submodules — git submodules not initialized. Ensure `git submodule update --init` runs inside the container.
- `Command 'clang-19' not found` outside the container — building on host instead of inside prepared Docker image. Use the provided container commands.
- `CMake Error: could not find Ninja` — Ninja generator requested but not installed in container. Install with `apt-get install -y ninja-build`.
