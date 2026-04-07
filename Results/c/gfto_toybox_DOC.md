# toybox Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    pkg-config=1.8.1-2build1 \
    libncurses-dev=6.4+20240113-1ubuntu2
```

## Build Steps

```bash
cd /app/toybox
make defconfig
make -j$(nproc)
make install_flat PREFIX=/app/toybox/generated/testdir
```

## Test Steps

```bash
cd /app/toybox
VERBOSE=1 make tests
```

## Unexpected Issues

- `config2help` tool may fail to generate `help.h` -- requires a stub generation workaround
- Some tests (`mount`, `losetup`, `ifconfig`) require root/privileged capabilities inside the container
- Test output uses `PASS:`/`FAIL:` prefix format
