# u-boot (Rockchip) Deployment Document

## Platform

- Base image: `ubuntu:22.04`
- Cross-compiler: gcc-aarch64-linux-gnu (for ARM64 targets)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.9ubuntu3 \
    gcc-aarch64-linux-gnu=4:11.2.0-1ubuntu1 \
    gcc-arm-linux-gnueabihf=4:11.2.0-1ubuntu1 \
    bison=2:3.8.2+dfsg-1build1 \
    flex=2.6.4-8build2 \
    libssl-dev=3.0.2-0ubuntu1 \
    bc=1.07.1-3build1 \
    device-tree-compiler=1.6.1-1 \
    python3=3.10.6-1~22.04 \
    python3-pip=22.0.2+dfsg-1ubuntu0.4 \
    python3-dev=3.10.6-1~22.04 \
    python3-setuptools=59.6.0-1.2ubuntu0.22.04.1 \
    swig=4.0.2-1ubuntu1 \
    libpython3-dev=3.10.6-1~22.04 \
    libncurses5-dev=6.3-2ubuntu0.1 \
    u-boot-tools=2022.01+dfsg-2ubuntu2 \
    git=1:2.34.1-1ubuntu1 \
    wget=1.21.2-2ubuntu1 \
    cpio=2.13+dfsg-7ubuntu0.1
```

## Build Steps

### Strategy A: Cross-compile for a Rockchip board (recommended)

```bash
cd /app/u_boot

make CROSS_COMPILE=aarch64-linux-gnu- evb-rk3399_defconfig
make CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc)
```

### Strategy B: Build host tools only (no cross-compiler needed)

```bash
cd /app/u_boot

make sandbox_defconfig O=build-sandbox
make tools-only O=build-sandbox -j$(nproc) || true
```

## Test Steps

### Python dtoc tests (recommended, only pytest-style test in this fork)

```bash
pip3 install pytest
cd /app/u_boot
python3 -m pytest tools/dtoc/test_dtoc.py -v
```

### Build verification (for cross-compiled kernel)

```bash
file u-boot
file u-boot.bin
ls -la u-boot.img 2>/dev/null || true
```

## Unexpected Issues

- **sandbox_defconfig is broken** in this Rockchip fork -- Rockchip-specific code leaks into common paths causing missing headers (`asm/arch/hotkey.h`, `asm/arch/rk_atags.h`)
- `olddefconfig` does not exist in U-Boot 2017.09 -- use `silentoldconfig` instead
- The `make.sh` script expects `../rkbin/tools` and Linaro cross-compiler toolchains at specific paths
- The `tcheck` make target does not exist in this fork
- The test/py/ pytest suite requires a working sandbox binary which cannot be built in this fork
- Rockchip C unit tests (test/rockchip/) only run on actual hardware
- Cross-compiling for `evb-rk3399_defconfig` is the most reliable build path
- The dtoc Python tests are the only tests runnable in Docker without hardware
