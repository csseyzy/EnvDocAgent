# ecnu-sa-labs Deployment Document

## Platform

- OS: Ubuntu 24.04
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.10ubuntu1 \
    clang=1:18.1.3-1ubuntu1 \
    afl++=4.09c-1ubuntu3
```

## Build Steps

```bash
git clone --depth 1 https://github.com/ecnu-sa-labs/ecnu-sa-labs.git /app/ecnu-sa-labs
cd /app/ecnu-sa-labs/lab1
make all
```

## Test Steps

```bash
cd /app/ecnu-sa-labs/lab1
./autograder.sh
```

## Unexpected Issues

- `tree` not installed in base image; use `find` or `ls -R`.
- AFL fuzz steps timeout at 30s and exit non-zero; Makefile ignores these errors.
