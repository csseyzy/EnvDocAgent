# 9legacy Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    qemu-system-x86=1:8.2.2+ds-0ubuntu1.13 \
    qemu-utils=1:8.2.2+ds-0ubuntu1.13 \
    curl=8.5.0-2ubuntu10.8 \
    wget=1.21.4-1ubuntu4.1 \
    bzip2=1.0.8-5.1build0.1 \
    p7zip-full=16.02+transitional.1
```

## Build Steps

Plan 9 source uses Plan 9 C dialect and `mkfile` build system. It cannot be compiled with standard GCC/glibc.

```bash
cd /app/9legacy
# Extract binaries from ISO if available
curl -s -o /tmp/9legacy.iso.bz2 http://9legacy.org/download/9legacy.iso.bz2
bunzip2 /tmp/9legacy.iso.bz2
7z x -o/tmp/iso_root /tmp/9legacy.iso
```

## Test Steps

Test files use Plan 9 C dialect (`#include <u.h>`, `#include <libc.h>`) and Plan 9 build system (`mkfile`). They **cannot** be compiled with GCC.

To run tests, boot Plan 9 in QEMU:

```bash
qemu-system-x86_64 -m 512 -hda /tmp/9legacy.iso -nographic -serial stdio
```

Inside Plan 9:

```
cd /sys/src/libmp && mk test && ./test
cd /sys/src/libthread && mk test && ./test
cd /sys/src/cmd/cpp && mk test
```

## Unexpected Issues

- All test files use Plan 9 C dialect -- they cannot be compiled with GCC/glibc
- Tests require booting Plan 9 in QEMU, which is a full OS boot
- `sys/src/cmd/test.c` is the Plan 9 `test(1)` command implementation, not a test suite
- `sys/src/cmd/cpp/test.c` is a 4-line preprocessor test input file, not a compiled test
- Tests are **not runnable in a standard Docker CI environment** without a full Plan 9 QEMU boot
