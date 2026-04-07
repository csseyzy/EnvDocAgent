# rvcc Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Cross-compiler: gcc-riscv64-linux-gnu
- Emulator: qemu-user (RISC-V user-mode)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    cmake=3.28.3-1build7 \
    binutils=2.42-4ubuntu2 \
    file=1:5.45-3build1 \
    gcc-riscv64-linux-gnu=4:13.2.0-7ubuntu1 \
    binutils-riscv64-linux-gnu=2.42-4ubuntu2 \
    qemu-user=1:8.2.2+ds-0ubuntu1
```

## Build Steps

Set up the RISC-V toolchain symlinks expected by the Makefile:

```bash
mkdir -p /opt/riscv/bin
ln -sf /usr/bin/riscv64-linux-gnu-gcc /opt/riscv/bin/riscv64-unknown-linux-gnu-gcc
ln -sf /usr/bin/riscv64-linux-gnu-ar /opt/riscv/bin/riscv64-unknown-linux-gnu-ar
ln -sf /usr/bin/riscv64-linux-gnu-as /opt/riscv/bin/as
ln -sf /usr/bin/riscv64-linux-gnu-ld /opt/riscv/bin/ld
ln -sf /usr/bin/riscv64-linux-gnu-ar /opt/riscv/bin/ar
ln -sf /usr/bin/qemu-riscv64 /opt/riscv/bin/qemu-riscv64
ln -sfn /usr/riscv64-linux-gnu /opt/riscv/sysroot
mkdir -p /opt/riscv/sysroot/usr
ln -sfn ../include /opt/riscv/sysroot/usr/include

cd /app/rvcc
make clean
make
```

## Test Steps

```bash
cd /app/rvcc
make -j1 CC=/opt/riscv/bin/riscv64-unknown-linux-gnu-gcc RISCV=/opt/riscv PATH=/opt/riscv/bin:$PATH test
```

## Unexpected Issues

- The Makefile expects `$(RISCV)/sysroot/usr/include` to exist -- the symlink setup handles this
- The Makefile expects tools (`as`, `ld`, `ar`) in `$PATH` with standard names
- The "no tests" report is incorrect -- test executables were compiled and run via QEMU
