# Realking_kernel_sm8250 Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Compiler: clang/LLVM (project uses LLVM toolchain)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    bc=1.07.1-3ubuntu4 \
    bison=2:3.8.2+dfsg-1build2 \
    flex=2.6.4-8.2build1 \
    libssl-dev=3.0.13-0ubuntu3.7 \
    libncurses-dev=6.4+20240113-1ubuntu2 \
    libelf-dev=0.190-1.1build4 \
    dwarves=1.25-0ubuntu3 \
    clang=1:18.0-59~exp2 \
    lld=1:18.0-59~exp2 \
    llvm=1:18.0-59~exp2 \
    python3=3.12.3-0ubuntu2 \
    rsync=3.2.7-1ubuntu1.2 \
    perl=5.38.2-3.2ubuntu0.2 \
    pkg-config=1.8.1-2build1 \
    libcap-dev=1:2.66-5ubuntu2.2
```

## Build Steps

```bash
cd /app/realking_kernel_sm8250
make ARCH=x86 headers_install
make -C tools/testing/selftests all CC=clang HOSTCC=clang PYTHON=python3 PYTHON2=python3 WERROR=0
```

## Test Steps

```bash
cd /app/realking_kernel_sm8250
make -C tools/testing/selftests \
    TARGETS="proc exec splice size lib kcmp ipc mqueue sigaltstack timers" \
    run_tests CC=clang HOSTCC=clang PYTHON=python3 PYTHON2=python3
```

## Unexpected Issues

- Same fundamental limitation as all kernel projects: selftests run against the **host kernel**, not the compiled source
- `WERROR=0` is needed because clang 18 is stricter than the GCC version the kernel was written for
- `python2` is not available in Ubuntu 24.04; use `PYTHON=python3 PYTHON2=python3` or symlink
- Safe container targets: `proc`, `exec`, `timers`, `splice`, `size`, `lib`, `kcmp`, `ipc`, `mqueue`, `sigaltstack`
