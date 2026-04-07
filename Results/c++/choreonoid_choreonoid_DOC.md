# choreonoid Deployment Document

## Platform

- OS: Ubuntu 22.04 (jammy)
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    sudo tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.9ubuntu3 \
    cmake=3.22.1-1ubuntu1.22.04.2 \
    pkg-config=1.8.1-2build1 \
    gettext=0.21-4ubuntu4
```

Run project dependency scripts (installs Qt 5.15.3, Eigen 3.4.0, libassimp 5.2.2, libfcl 0.7.0, libode 0.16.2, python3-numpy 1.21.5, etc.):

```bash
cd /app/choreonoid
bash ./.github/script/install-requisites-ubuntu-22.04-for-github-actions.sh
bash ./misc/script/install-requisites-ubuntu-22.04.sh
```

## Build Steps

```bash
git clone --depth 1 https://github.com/choreonoid/choreonoid.git /app/choreonoid
cd /app/choreonoid
cmake -S . -B build
cd build && make -j4
```

## Test Steps

```bash
cd /app/choreonoid/build
ctest --output-on-failure
```

## Unexpected Issues

- Missing `gettext` (0.21): CMake fails on `msgfmt`/`msgcat`. Not included in project dependency scripts.
- No test suite: project has no `add_test()` in CMake. Build success is the only verification.
