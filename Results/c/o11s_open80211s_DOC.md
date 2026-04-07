# open80211s Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    bc=1.07.1-3ubuntu4 \
    bison=2:3.8.2+dfsg-1build2 \
    flex=2.6.4-8.2build1 \
    libncurses-dev=6.4+20240113-1ubuntu2 \
    perl=5.38.2-3.2ubuntu0.2 \
    kmod=31+20240202-2ubuntu7.1 \
    xz-utils=5.6.1+really5.4.5-1ubuntu0.2 \
    cpio=2.15+dfsg-1ubuntu2 \
    libelf-dev=0.190-1.1build4
```

## Build Steps

```bash
cd /app/open80211s
make defconfig
scripts/config --disable BLK_DEV_INITRD
make olddefconfig
make -j$(nproc) HOSTCFLAGS="-fcommon" CC="gcc -fno-pie -no-pie" bzImage
```

## Test Steps

### RAID-6 userspace unit test (most reliable)

```bash
cd /app/open80211s/lib/raid6/test
make raid6test
./raid6test
```

### Kernel selftests

```bash
cd /app/open80211s/tools/testing/selftests
make
make run_tests
```

## Unexpected Issues

- The kernel build requires `-fcommon` and `-fno-pie` flags for GCC 13+ compatibility
- Most selftests require running on the actual built kernel, not in a Docker container
- `lib/raid6/test` is the most reliably runnable userspace test
- `tools/perf` tests require kernel perf event support
- The 32 test files are primarily kernel selftests and RAID-6 unit tests
