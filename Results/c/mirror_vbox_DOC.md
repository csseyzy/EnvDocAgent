# vbox Deployment Document

## Platform

- OS: Ubuntu 24.04 (noble), linux.amd64
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.10ubuntu1 \
    perl=5.38.2-3.2ubuntu0.2 python3=3.12.3-0ubuntu2.1 python3-dev=3.12.3-0ubuntu2.1 \
    python-is-python3=3.11.4-1 \
    yasm=1.3.0-4 nasm=2.16.01-1build1 \
    autoconf=2.71-3 automake=1:1.16.5-1.3ubuntu1 libtool=2.4.7-7build1 pkg-config=1.8.1-2build1 \
    bison=2:3.8.2+dfsg-1build2 flex=2.6.4-8.2build1 \
    xsltproc=1.1.39-0exp1ubuntu0.24.04.3 \
    zip=3.0-13build1 unzip=6.0-28ubuntu4 p7zip-full \
    wget=1.21.4-1ubuntu4 curl=8.5.0-2ubuntu10.8 \
    zlib1g-dev=1:1.3.dfsg-3.1ubuntu2.1 libpng-dev=1.6.43-5ubuntu0.5 \
    libssl-dev=3.0.13-0ubuntu3.7 libxml2-dev=2.9.14+dfsg-1.3ubuntu3.7 libxslt1-dev libcurl4-openssl-dev=8.5.0-2ubuntu10.8 \
    libpam0g-dev=1.5.3-5ubuntu5.5 \
    kbuild=1:0.1.9998svn3604+dfsg-1 \
    acpica-tools=20230628-1 \
    libidl-dev=0.8.14-4build3 \
    libvpx-dev=1.14.0-1ubuntu2.3
```

- `kbuild` — provides `kmk` build tool required by VirtualBox build system
- `acpica-tools` (iasl 20230628) — ACPI compiler required by configure
- `libidl-dev` (0.8.14) — CORBA IDL parser, provides `libIDL-config`
- `libvpx-dev` (1.14.0) — VP8/VP9 video codec library
- `python-is-python3` — symlinks `python` to `python3` for configure's Python check
- `python3-dev` (3.12.3) — Python development headers for Python bindings

## Build Steps

```bash
git clone --depth 1 https://github.com/mirror/vbox.git /app/project
cd /app/project
./configure --build-headless --disable-hardening
source ./env.sh
export KBUILD_PATH=/usr/share/kBuild
export USER=builder
export VBOX_SVN_REV=0
export VBOX_SVN_REV_FALLBACK=0
kmk -C src/VBox/Runtime -j$(nproc)
```

## Test Steps

```bash
cd /app/project
source ./env.sh
export KBUILD_PATH=/usr/share/kBuild
export USER=builder
export VBOX_WITH_TESTCASES=1
kmk -C src/VBox/Runtime/testcase -j$(nproc)
```

## Unexpected Issues

- `env.sh` may not be generated if configure fails partway (e.g., missing `libIDL-config`). Ensure all dependencies are installed before running configure.
- `KBUILD_PATH` must point to `/usr/share/kBuild` (where the Ubuntu `kbuild` package installs kBuild templates), not `$PWD/kBuild`.
- `USER` environment variable must be set (e.g., `export USER=builder`); kmk warns if unset.
- `libidl-2-dev` package does not exist on Ubuntu 24.04; the correct package name is `libidl-dev`.
