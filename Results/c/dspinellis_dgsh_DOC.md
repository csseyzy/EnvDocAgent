# dgsh Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    automake=1:1.16.5-1.3ubuntu1 \
    autoconf=2.71-3 \
    libtool=2.4.7-7build1 \
    pkg-config=1.8.1-2build1 \
    texinfo=7.1-3build2 \
    help2man=1.49.3 \
    autopoint=0.21-14ubuntu2 \
    bison=2:3.8.2+dfsg-1build2 \
    gperf=3.1-1build1 \
    gettext=0.21-14ubuntu2 \
    flex=2.6.4-8.2build1 \
    check=0.15.2-2build2 \
    wbritish=2024.01.06-1 \
    wamerican=2024.01.06-1 \
    libfftw3-dev=3.3.10-1ubuntu3 \
    csh=20230828-5 \
    curl=8.5.0-2ubuntu10.8 \
    bzip2=1.0.8-5.1build0.1 \
    file=1:5.45-3build1 \
    locales=2.39-0ubuntu8.3 \
    rsync=3.2.7-1ubuntu1 \
    xz-utils=5.6.1+really5.4.5-1build0.1 \
    patch=2.7.6-7build3
```

## Build Steps

```bash
cd /app/dgsh
git submodule update --init --recursive
make config
FORCE_UNSAFE_CONFIGURE=1 make -C unix-tools configure
make -j$(nproc)
```

## Test Steps

```bash
cd /app/dgsh
make test
```

## Unexpected Issues

- Some tests like `test-dgsh.sh` require network access (fetches web log data)
- `test-negotiate` runs `make && make check` in `core-tools/tests/`
- `FORCE_UNSAFE_CONFIGURE=1` is needed for building unix-tools as root
