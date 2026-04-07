# metron Deployment Document

## Platform

- **Base Image:** ubuntu:22.04
- **Build System:** Hancho + Ninja

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.34.1-1ubuntu1.11 \
    build-essential=12.9ubuntu3 \
    ninja-build=1.10.1-1 \
    python3=3.10.6-1~22.04.1 \
    python3-pip=22.0.2+dfsg-1ubuntu0.5 \
    libicu-dev=70.1-2 \
    libsdl2-dev=2.0.20+dfsg-2ubuntu1.22.04.1 \
    pkg-config=0.29.2-1ubuntu3
```

## Build Steps

```bash
pip3 install hancho==0.2.0
```

```bash
# Clone sibling dependencies FIRST (critical!)
cd /app
git clone --depth 1 https://github.com/CLIUtils/CLI11
git clone --depth 1 https://github.com/aappleby/metrolib
git clone --depth 1 https://github.com/aappleby/matcheroni

cd /app/project

# Fix symlinks to point to sibling repos
rm -rf symlinks/metrolib symlinks/matcheroni symlinks/metron
ln -sf /app/metrolib symlinks/metrolib
ln -sf /app/matcheroni symlinks/matcheroni
ln -sf /app/project symlinks/metron

# Build using Hancho
hancho build.hancho
ninja -j$(nproc)
```

## Test Steps

```bash
cd /app/project
hancho test.hancho
ninja -j$(nproc) 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- **Hancho build system** is uncommon — agents don't recognize it
- Sibling repo dependency pattern (not submodules) is unusual and confusing for automated tools
- Full test suite requires FPGA toolchain (Verilator, Yosys, Icarus, nextpnr-ice40, gcc-riscv64)
- The `build.py` mentioned in README doesn't exist — README is outdated
- The actual build of `metron` binary is fast (~30s); basic tests complete in ~1-2 min
