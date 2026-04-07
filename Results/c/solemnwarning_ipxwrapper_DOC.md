# ipxwrapper Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Cross-compiler: MinGW (i686-w64-mingw32)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    make=4.3-4.1build2 \
    perl=5.38.2-3.2ubuntu0.2 \
    nasm=2.16.01-1build1 \
    gcc-mingw-w64-i686=13.2.0-6ubuntu1+26.1 \
    g++-mingw-w64-i686=13.2.0-6ubuntu1+26.1 \
    binutils-mingw-w64-i686=2.41.90.20240122-1ubuntu1+11.4 \
    zip=3.0-13ubuntu0.2
```

For running tests, also install Wine:

```bash
dpkg --add-architecture i386
apt-get update
apt-get install -y wine32
```

## Build Steps


Fix MinGW 13.x compatibility in `src/winsock.c`:

```bash
perl -0777 -i -pe "s/const PTIMEVAL timeout/const TIMEVAL *timeout/g" src/winsock.c
```


```bash
cd /app/ipxwrapper
make HOST=i686-w64-mingw32 -j$(nproc) test-prep
```

## Test Steps

```bash
wine tests/addr.exe
wine tests/addrcache.exe
wine tests/ethernet.exe
wine tests/ratelimit.exe
```

## Unexpected Issues

- The `.t` Perl test files are integration tests that SSH into a remote Windows machine -- not runnable in Docker
- Only the 4 `.exe` unit tests (`addr`, `addrcache`, `ethernet`, `ratelimit`) are runnable via Wine
- `wine32` requires `dpkg --add-architecture i386` before installation
- `PTIMEVAL` type must be replaced with `TIMEVAL *` for MinGW 13.x compatibility
