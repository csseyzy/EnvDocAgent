# kernel (Sony Xperia) Deployment Document

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
    libelf-dev=0.190-1.1build4 \
    libssl-dev=3.0.13-0ubuntu3.7 \
    dwarves=1.25-0ubuntu3 \
    pkg-config=1.8.1-2build1 \
    rsync=3.2.7-1ubuntu1.2 \
    perl=5.38.2-3.2ubuntu0.2 \
    python3=3.12.3-0ubuntu2 \
    libcap-dev=1:2.66-5ubuntu2.2 \
    libnuma-dev=2.0.18-1ubuntu0.24.04.1 \
    libmnl-dev=1.0.4-4 \
    libmount-dev=2.39.3-9ubuntu6.5
```

## Build Steps

```bash
cd /app/kernel
make ARCH=x86 headers_install
make -C tools/testing/selftests TARGETS="proc timers" all
```

## Test Steps

```bash
cd /app/kernel
make -C tools/testing/selftests \
    TARGETS="proc timers size lib exec splice kcmp ipc mqueue sigaltstack" \
    run_tests
```

For quick test mode:

```bash
make quicktest=1 -C tools/testing/selftests run_tests
```

## Unexpected Issues

- Kernel selftests run in **userspace** and test the **host kernel**, not the compiled kernel source
- Many selftest targets (`kvm`, `cpu-hotplug`, `memory-hotplug`, `livepatch`, `ftrace`, `firmware`) require root privileges or specific kernel configs unavailable in containers
- Safe container targets: `proc`, `size`, `lib`, `exec`, `splice`, `kcmp`, `ipc`, `mqueue`, `sigaltstack`, `timers`
- Unsafe targets: `kvm`, `bpf`, `cpu-hotplug`, `memory-hotplug`, `livepatch`, `ftrace`, `firmware`, `net`, `netfilter`
