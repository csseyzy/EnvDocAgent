# pitivi Deployment Document

## Platform

- **Base Image:** debian:bookworm
- **Python Version:** 3.11

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    python3=3.11.2-1+b1 \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
    python3-setuptools=66.1.1-1 \
    python3-wheel=0.38.4-2 \
    build-essential=12.9 \
    meson=1.0.1-5 \
    ninja-build=1.11.1-1 \
    pkg-config=1.8.1-1 \
    git=1:2.43.0-1ubuntu7 \
    gstreamer1.0-tools=1.22.0-2+deb12u1 \
    gstreamer1.0-plugins-base=1.22.0-3+deb12u1 \
    gstreamer1.0-plugins-good=1.22.0-4+deb12u1 \
    gstreamer1.0-plugins-bad=1.22.0-4+deb12u1 \
    gstreamer1.0-plugins-ugly=1.22.0-2+deb12u1 \
    gstreamer1.0-libav=1.22.0-1+deb12u1 \
    gstreamer1.0-x=1.22.0-3+deb12u1 \
    gstreamer1.0-alsa=1.22.0-3+deb12u1 \
    gir1.2-gstreamer-1.0=1.22.0-2+deb12u1 \
    gir1.2-ges-1.0=1.22.0-1+deb12u1 \
    gir1.2-gtk-3.0=3.24.38-2 \
    gir1.2-pango-1.0=1.50.12+ds-1 \
    gir1.2-peas-1.0=1.34.0-1+b1 \
    libgirepository1.0-dev=1.74.0-3 \
    python3-gi=3.42.2-3+b1 \
    python3-gi-cairo=3.42.2-3+b1 \
    python3-cairo-dev=1.20.1-5+b1 \
    libcairo2-dev=1.16.0-7 \
    python3-numpy=1:1.24.2-1 \
    python3-matplotlib=3.6.3-1+b1 \
    xvfb=2:21.1.7-3+deb12u8 \
    dbus=1.14.10-1~deb12u1 \
    locales=2.36-9+deb12u9 \
    glib-networking=2.74.0-2 \
    gsettings-desktop-schemas=43.0-1 \
    libglib2.0-dev=2.74.6-2+deb12u4
```

## Build Steps

```bash
sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

cd /app/project
pip3 install pytest==7.4.4 pycairo==1.25.1 scipy==1.11.4 librosa==0.10.1

glib-compile-schemas data/

meson setup builddir
cd builddir && ninja && cd ..
cp builddir/configure.py pitivi/configure.py
```

## Test Steps

```bash
LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
GSETTINGS_SCHEMA_DIR=/app/project/data \
PITIVI_DEVELOPMENT=1 \
dbus-run-session -- xvfb-run -a python3 -m pytest tests/ -x --timeout=120 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- tests in `test_clipproperties_color.py` may fail due to GStreamer version mismatches between GES and core plugins
- Requires X11 display server (xvfb) and D-Bus session
- `inotify` warnings in Docker are cosmetic (fd limits)
- Using Debian testing (instead of bookworm) causes version skew between GStreamer packages
