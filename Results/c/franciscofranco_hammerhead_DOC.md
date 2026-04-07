# hammerhead Deployment Document

## Platform

- Base image: `ubuntu:20.04` 
- Cross-compiler: gcc-arm-linux-gnueabihf (GCC 9/10 from Ubuntu 20.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.8ubuntu1 \
    gcc-arm-linux-gnueabihf=4:9.3.0-1ubuntu2 \
    bc=1.07.1-2build1 \
    bison=2:3.5.1+dfsg-1 \
    flex=2.6.4-6.2 \
    libssl-dev=1.1.1f-1ubuntu2 \
    libncurses-dev=6.2-0ubuntu2 \
    device-tree-compiler=1.5.1-1 \
    lzop=1.04-2 \
    git=1:2.25.1-1ubuntu3 \
    ca-certificates=20230311ubuntu0.20.04.1 \
    python2=2.7.17-2ubuntu4
```

## Build Steps


### 1. Create compiler version header

```bash
cd /app/hammerhead
cp include/linux/compiler-gcc4.h include/linux/compiler-gcc11.h
```

(Also create `compiler-gcc12.h`, `compiler-gcc13.h` as copies if using newer GCC)

### 2. Fix missing include in perf_trace_counters.c

```bash
sed -i '1i #include <linux/cpu.h>' arch/arm/mach-msm/perf_trace_counters.c
```

### 3. Disable FTRACE to avoid inline assembly incompatibilities

```bash
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- hammerhead_defconfig

scripts/config --file .config \
    --disable FTRACE \
    --disable FUNCTION_TRACER \
    --disable FUNCTION_GRAPH_TRACER \
    --disable PERSISTENT_TRACER \
    --disable FTRACE_MCOUNT_RECORD

make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- silentoldconfig
```


### On Ubuntu 20.04 (GCC 9/10, recommended)

```bash
cd /app/hammerhead
make ARCH=arm mrproper
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- hammerhead_defconfig
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- \
    KCFLAGS='-Wno-error' \
    -j$(nproc)
```

### On Ubuntu 22.04+ (GCC 11+, requires source patches above)

```bash
cd /app/hammerhead
make ARCH=arm mrproper
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- hammerhead_defconfig

# Apply source modifications (see above)

make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- \
    HOSTCFLAGS='-fcommon' \
    KCFLAGS='-Wno-error -fgnu89-inline -Wno-error=implicit-function-declaration -Wno-error=attributes' \
    -j$(nproc)
```

## Test Steps

```bash
file arch/arm/boot/zImage-dtb
file vmlinux
ls -la System.map
```

## Unexpected Issues

- **Cannot be cleanly built with GCC >= 12 without source patches** -- the original toolchain was GCC 4.8
- `olddefconfig` does not exist in kernel 3.4 -- use `silentoldconfig` instead
- The `yylloc` symbol in dtc causes multiple-definition errors with GCC 10+ default `-fno-common` -- requires `HOSTCFLAGS='-fcommon'`
- `perf_trace_counters.c` is missing `#include <linux/cpu.h>` for hotplug APIs
- FTRACE features in `hammerhead_defconfig` use inline assembly incompatible with modern GCC
- Building this kernel takes ~10-30 minutes even on fast hardware -- timeout budget must account for this
- **No test suite exists** -- the only meaningful verification is a successful kernel image build
