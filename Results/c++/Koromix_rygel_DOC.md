# rygel Deployment Document

## Platform

- OS: Ubuntu 24.04
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.10ubuntu1 \
    g++=4:13.2.0-7ubuntu1 \
    clang=1:18.1.3-1ubuntu1 \
    cmake=3.28.3-1ubuntu3 \
    ninja-build=1.11.1-2 \
    pkg-config=1.8.1-2build1 \
    make=4.3-4.1build2 \
    autoconf=2.71-3 automake=1:1.16.5-1.3ubuntu1 libtool=2.4.7-7build1 \
    perl=5.38.2-3.2build2 \
    ruby=1:3.2~ubuntu1 \
    nodejs=18.19.1+dfsg-6ubuntu5 \
    npm=9.2.0~ds1-2 \
    gdb=15.0.50.20240403-0ubuntu1
```

## Build Steps

```bash
git clone --depth 1 https://github.com/Koromix/rygel.git /app/project
cd /app/project
./bootstrap.sh
./felix build test
```

## Test Steps

```bash
cd /app/project
./bin/Debug/test
```


## Unexpected Issues

- Web search for "rygel" returns GNOME DLNA Rygel (unrelated project). Build docs are only in the repo.
