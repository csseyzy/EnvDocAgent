# FlagCX Deployment Document

## Platform

- **Base Image:** nvcr.io/nvidia/cuda:12.4.1-devel-ubuntu22.04
- **Build System:** Make

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.9ubuntu3 \
    cmake=3.22.1-1ubuntu1.22.04.2 \
    git=1:2.34.1-1ubuntu1.11 \
    ninja-build=1.10.1-1 \
    libibverbs-dev=39.0-1 \
    libnuma-dev=2.0.14-3ubuntu2 \
    wget=1.21.2-2ubuntu1.1 \
    pkg-config=0.29.2-1ubuntu3
```

```bash
# OpenMPI 4.1.6
wget -q https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.6.tar.gz
tar xzf openmpi-4.1.6.tar.gz && cd openmpi-4.1.6
./configure --prefix=/usr/local/mpi && make -j$(nproc) install
export PATH=/usr/local/mpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/mpi/lib:$LD_LIBRARY_PATH

# Google Test 1.14.0
git clone --branch v1.14.0 --depth 1 https://github.com/google/googletest.git /tmp/gtest
cd /tmp/gtest && mkdir build && cd build && cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local && make -j$(nproc) install
```

## Build Steps

```bash
cd /app/project

# CPU-only bootstrap mode (no GPU needed):
make USE_BOOTSTRAP=1 -j$(nproc)

# With NVIDIA GPU support:
make USE_NVIDIA=1 DEVICE_HOME=/usr/local/cuda -j$(nproc)

# With kernel compilation:
make USE_NVIDIA=1 COMPILE_KERNEL=1 DEVICE_HOME=/usr/local/cuda -j$(nproc)
```

## Test Steps

```bash
# Unit tests require 8 GPUs and MPI:
cd test/unittest && make MPI_HOME=/usr/local/mpi
mpirun --allow-run-as-root -np 8 \
    -x CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
    -x FLAGCX_LOG_LEVEL=TRACE \
    -x FLAGCX_TOPO_FILE="topo_demo.xml" \
    ./build/bin/main

# For build-only verification (no GPU):
make USE_BOOTSTRAP=1 -j$(nproc) && echo "Build OK"
```

## Unexpected Issues

- **Hard GPU requirement**: Unit tests require 8 NVIDIA GPUs with MPI
- NCCL version mismatch: code expects NCCL >= 2.19 but CUDA 12.4 ships with older NCCL
- No CPU-only test suite available
- Recommend using `USE_BOOTSTRAP=1` for build verification only
