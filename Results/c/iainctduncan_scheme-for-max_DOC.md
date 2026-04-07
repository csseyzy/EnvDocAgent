# scheme-for-max Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    build-essential=12.10ubuntu1 \
    ca-certificates=20240203
```

## Build Steps


### Step 1: Initialize submodules

```bash
cd /app/project
git submodule update --init --recursive
```

### Step 2: Build the s7 test harness

```bash
cd /app/project/test-code/s7-test
gcc -c s7.c
gcc s7-test.c -L. -I. s7.o -lm -o s7-test
```

## Test Steps

```bash
cd /app/project/test-code/s7-test
./s7-test
```

## Unexpected Issues

- The main DXGL project (Max external) cannot be built on Linux — it requires the Max SDK and macOS/Windows. Only the auxiliary s7 test harness is buildable.
- Optional: add `#include <string.h>` to `s7-test.c` to suppress implicit declaration warnings for `strlen`/`strcpy`.
