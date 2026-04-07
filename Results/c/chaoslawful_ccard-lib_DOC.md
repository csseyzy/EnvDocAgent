# ccard-lib Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    build-essential=12.10ubuntu1 \
    scons=4.5.2+dfsg-1 \
    cmake=3.28.3-1build7 \
    libgtest-dev=1.14.0-1 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Build Google Test static libraries

`libgtest-dev` on Ubuntu 24.04 only provides source. Static libraries must be built manually.

```bash
cd /usr/src/googletest
cmake .
make
cp -a lib/libgtest*.a /usr/lib/
```


## Test Steps

```bash
cd /app/project
scons test
```

## Unexpected Issues

- Upstream code has `-Werror` warnings with GCC 13+ that require patching `src/murmurhash.c` (implicit-fallthrough) and `src/register_set.c` (memset/memcpy element-size).
- `libgtest-dev` on Ubuntu 24.04 only provides source; static libraries must be built from `/usr/src/googletest` before `scons test` will link.
- SCons build uses strict flags: `-Wall -Wextra -Werror -g3 -std=c99`.
