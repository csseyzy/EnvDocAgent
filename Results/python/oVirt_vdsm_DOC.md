# vdsm (Virtual Desktop Server Manager) Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** 3.12

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    python3=3.12.3-0ubuntu2 \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
    python3-venv=3.12.3-0ubuntu2 \
    python3-dev=3.12.3-0ubuntu2 \
    build-essential=12.10ubuntu1 \
    make=4.3-4.1build2 \
    autoconf=2.71-3 \
    automake=1:1.16.5-1.3ubuntu1 \
    libtool=2.4.7-7build1 \
    gettext=0.21-14ubuntu2 \
    pkg-config=1.8.1-2build1 \
    python3-yaml=6.0.1-2build2 \
    python3-dateutil=2.8.2-3ubuntu1 \
    python3-dbus=1.3.2-5build3 \
    libnl-3-200=3.7.0-0.3build1 \
    libnl-genl-3-200=3.7.0-0.3build1 \
    libnl-route-3-200=3.7.0-0.3build1 \
    rpm=4.18.2+dfsg-2.1build2 \
    libvirt-dev=10.0.0-2ubuntu8 \
    libcairo2-dev=1.18.0-3build1 \
    libgirepository1.0-dev=1.80.1-1 \
    gobject-introspection=1.80.1-1 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
./autogen.sh && ./configure && make

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install pytest==8.3.4 pytest-cov==6.0.0 pytest-timeout==2.3.1 pyasyncore==1.0.4
pip install decorator==5.1.1 libvirt-python==10.0.0 python-dateutil==2.9.0
```

## Test Steps

```bash
cd /app/project
. .venv/bin/activate
PYTHONPATH="/app/project/lib:/usr/lib/python3/dist-packages" \
python -m pytest \
    -m 'not (integration or slow or stress)' \
    --durations=10 \
    tests/common tests/lib \
    -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- The full tox `lib` environment uses a `profile` wrapper script that may not exist in the test container
- Many system-level dependencies needed (libvirt, dbus, nmstate, libnl) for full test coverage
- The 5 test failures (out of 290) are likely due to missing system services (libvirtd, dbus-daemon) in the container
- The project is designed for CentOS/RHEL, so running on Ubuntu requires extra dependency resolution
- The autotools build (`autogen.sh && configure && make`) is needed to generate config files
