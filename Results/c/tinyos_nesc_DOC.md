# nesc Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    autoconf=2.71-3 \
    automake=1:1.16.5-1.3ubuntu1 \
    m4=1.4.19-4build1 \
    gettext=0.21-14ubuntu2 \
    flex=2.6.4-8.2build1 \
    bison=2:3.8.2+dfsg-1build2 \
    gperf=3.1-1build1 \
    emacs-nox=1:29.3+1-1ubuntu2 \
    perl=5.38.2-3.2ubuntu0.2 \
    default-jdk=2:1.21-75+exp1
```

## Build Steps

```bash
cd /app/nesc
./Bootstrap
./configure
make -j$(nproc)
make install
```

## Test Steps

```bash
cd /app/nesc
make check -j1

# Full regression suite (requires make install first)
./nregress/runtest
```

## Unexpected Issues

- `make install` must be run before `nregress/runtest` so that `nesc1` is in the expected path
- The regression test output format may differ from standard test runners
