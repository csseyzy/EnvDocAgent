# apt-dater Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    autoconf=2.71-3 \
    automake=1:1.16.5-1.3ubuntu1 \
    pkg-config=1.8.1-2build1 \
    gettext=0.21-14ubuntu2 \
    autopoint=0.21-14ubuntu2 \
    libglib2.0-dev=2.80.0-6ubuntu3.8 \
    libxml2-dev=2.9.14+dfsg-1.3ubuntu3.7 \
    libncurses-dev=6.4+20240113-1ubuntu2 \
    libpopt-dev=1.19+dfsg-1build1 \
    xsltproc=1.1.39-0exp1ubuntu0.24.04.3 \
    docbook-xsl=1.79.2+dfsg-7 \
    xxd=2:9.1.0016-1ubuntu7.8
```

## Build Steps

```bash
cd /app/apt_dater
mkdir -p m4
autoreconf -fi
./configure
make -j$(nproc)
```

## Test Steps

```bash
cd /app/apt_dater
TERM=xterm LC_ALL=C make check -j1
```

Additionally, the standalone regex test:

```bash
cd /app/apt_dater/test
bash test.sh
```

## Unexpected Issues

- `make check` may fail if `TERM` is not set (ncurses dependency) -- use `TERM=xterm`
- `test/test.sh` requires `grep` with `--perl-regexp` support (PCRE)
- The `xxd` package must be installed (needed by the build)
- `autopoint` is needed for `autoreconf -fi`
