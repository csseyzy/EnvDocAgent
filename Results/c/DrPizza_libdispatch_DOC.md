# libdispatch Deployment Document

## Platform

- Base image: `ubuntu:22.04`
- Compiler: clang (for Blocks extension support)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.34.1-1ubuntu1 \
    build-essential=12.9ubuntu3 \
    clang=1:14.0-55~exp2 \
    autoconf=2.71-2 \
    automake=1:1.16.5-1.3 \
    libtool=2.4.6-15build2 \
    pkg-config=0.29.2-1ubuntu3 \
    libblocksruntime-dev=0.4.1-1build1 \
    libbsd-dev=0.11.5-1 \
    libkqueue-dev=2.6.1-1 \
    libc6-dev=2.35-0ubuntu3 \
    linux-libc-dev=5.15.0-25.25
```

## Build Steps


### 1. Create Linux platform header

The project only has Darwin and Windows platform headers. Create `platform/linux/platform.h`:

```bash
cd /app/libdispatch/libdispatch
mkdir -p platform/linux
```


### 2. Add Linux path to platform/platform.h

```bash
sed -i 's|#include "platform/darwin/platform.h"|#ifdef __linux__\n#include "platform/linux/platform.h"\n#else\n#include "platform/darwin/platform.h"\n#endif|' platform/platform.h
```

### 3. Guard EVFILT_OIO references


```bash
cd /app/libdispatch/libdispatch

sh autogen.sh
CC=clang ./configure --with-blocks-runtime=/usr/lib
make -j$(nproc)
```

## Test Steps

```bash
make check
```

## Unexpected Issues

- Linux platform header (`platform/linux/platform.h`) must be created manually since the project only ships Darwin and Windows headers.
- `EVFILT_OIO` is not defined in Linux's libkqueue, references must be wrapped with `#ifdef EVFILT_OIO` to avoid compilation errors.
- `_GNU_SOURCE` must be defined for `getprogname` shim to access `program_invocation_short_name`.
- Some tests (`dispatch_cffd`, `dispatch_proc`, `nsoperation`) depend on macOS-specific APIs and will be skipped on Linux.
- Clang with Blocks extension (`libblocksruntime-dev`) is required instead of GCC, as the project uses Apple's Blocks syntax (`^{}`).
