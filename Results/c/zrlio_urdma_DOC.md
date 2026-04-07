# urdma Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    build-essential=12.10ubuntu1 \
    autoconf=2.71-3 \
    automake=1:1.16.5-1.3ubuntu1 \
    libtool=2.4.7-7build1 \
    libtool-bin=2.4.7-7build1 \
    pkg-config=1.8.1-2build1 \
    m4=1.4.19-4build1 \
    libibverbs-dev=50.0-2ubuntu0.2 \
    librdmacm-dev=50.0-2ubuntu0.2 \
    libnl-3-dev=3.7.0-0.3build1 \
    libnl-route-3-dev=3.7.0-0.3build1 \
    libjson-c-dev=0.17-1build1 \
    uthash-dev=2.3.0-2 \
    libdpdk-dev=23.11-1build3 \
    dpdk=23.11-1build3 \
    linux-headers-generic \
    ca-certificates=20240203
```

## Build Steps


### Step 1: Build and run unit tests

```bash
cd /app/project
mkdir -p build/tests

```

## Test Steps
```
# Test 1: binheap

gcc -std=gnu11 -O2 -Wall -Wextra -Isrc/util tests/binheap.c src/util/binheap.c -o build/tests/binheap_test
./build/tests/binheap_test

# Test 2: list_test
gcc -std=gnu11 -O2 -Wall -Wextra -I. tests/list_test.c -o build/tests/list_test
./build/tests/list_test
```
## Unexpected Issues

- `./configure` fails because Ubuntu 24.04 ships rdma-core 50.x which no longer exports the `verbs_register_driver` symbols that urdma's PABI detection expects.
- DPDK environment script `/usr/share/dpdk/dpdk-sdk-env.sh` does not exist in Ubuntu's packaged DPDK.
- Only the 2 standalone unit tests under `tests/` are runnable in a container environment.
