# EFL (Enlightenment Foundation Libraries) Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    meson=1.3.2-1ubuntu1 \
    ninja-build=1.11.1-2 \
    pkg-config=1.8.1-2build1 \
    check=0.15.2-2build1 \
    clang=1:18.0-59~exp2 \
    python3=3.12.3-0ubuntu2 \
    libssl-dev=3.0.13-0ubuntu3.7 \
    libsystemd-dev=255.4-1ubuntu8 \
    libjpeg-dev=8c-2ubuntu11 \
    libglib2.0-dev=2.80.0-6ubuntu3.8 \
    libgstreamer1.0-dev=1.24.2-1 \
    libgstreamer-plugins-base1.0-dev=1.24.2-1 \
    liblua5.2-dev=5.2.4-3build1 \
    libluajit-5.1-dev=2.1.0+git20231223.c525bcb-0.2 \
    libfreetype6-dev=2.13.2+dfsg-1build3 \
    libfontconfig1-dev=2.15.0-1.1ubuntu2 \
    libfribidi-dev=1.0.13-3build1 \
    libharfbuzz-dev=8.3.0-2build2 \
    libibus-1.0-dev=1.5.29-1build2 \
    libx11-dev=2:1.8.7-1build1 \
    libxext-dev=2:1.3.4-1build2 \
    libxrender-dev=1:0.9.10-1.1build1 \
    libxdamage-dev=1:1.1.6-1build1 \
    libgl1-mesa-dev=24.0.5-1ubuntu1 \
    libxcursor-dev=1:1.2.1-1build1 \
    libxcomposite-dev=1:0.4.6-1build2 \
    libxinerama-dev=2:1.1.4-3build1 \
    libxrandr-dev=2:1.5.4-1 \
    libxtst-dev=2:1.2.3-1.1build1 \
    libxss-dev=1:1.2.3-1build3 \
    libopenjp2-7-dev=2.5.0-2build3 \
    libwebp-dev=1.3.2-0.4build3 \
    libgif-dev=5.2.2-1ubuntu1 \
    libtiff-dev=4.5.1+git230720-4ubuntu2 \
    libpng-dev=1.6.43-5build1 \
    zlib1g-dev=1:1.3.dfsg-3.1ubuntu2 \
    libpoppler-dev=24.02.0-1ubuntu9 \
    libpoppler-cpp-dev=24.02.0-1ubuntu9 \
    librsvg2-dev=2.58.0+dfsg-1build1 \
    libudev-dev=255.4-1ubuntu8 \
    libmount-dev=2.39.3-9ubuntu6.5 \
    libdbus-1-dev=1.14.10-4ubuntu4 \
    libpulse-dev=1:16.1+dfsg1-2ubuntu10 \
    libsndfile1-dev=1.2.2-1ubuntu5 \
    libunwind-dev=1.6.2-3build1 \
    libdrm-dev=2.4.120-2build1 \
    libinput-dev=1.25.0-1ubuntu2 \
    libavahi-client-dev=0.8-13ubuntu6 \
    libexif-dev=0.6.24-2build2 \
    libcurl4-openssl-dev=8.5.0-2ubuntu10 \
    xvfb=2:21.1.12-1ubuntu1.5 \
    dbus=1.14.10-4ubuntu4 \
    gettext=0.21-14ubuntu2 \
    doxygen=1.9.8+ds-2build5
```

## Build Steps

```bash
cd /app/efl
meson setup build -Dcrypto=openssl
meson compile -C build -j$(nproc)
```

## Test Steps

```bash
xvfb-run -a dbus-run-session -- meson test -C build -v --no-rebuild --print-errorlogs --timeout-multiplier 2
```

For a subset of reliable non-GUI tests:

```bash
xvfb-run -a dbus-run-session -- meson test -C build -v --no-rebuild --print-errorlogs --timeout-multiplier 2 \
    eina eolian eo-suite emile-suite eet-suite eldbus-suite ecore_con-suite ector-suite efreet-suite eio-suite
```

## Unexpected Issues

- Many EFL tests require a display server; `xvfb-run` provides a virtual framebuffer but GPU-accelerated tests (Evas, Elementary) will still fail
- `dbus-run-session` is required for tests using D-Bus (Eldbus, Efreet)
- `--timeout-multiplier 2` is needed because tests are slow in Docker
- Tests like `elementary`, `evas`, `ecore` are very flaky in containers due to missing hardware acceleration
