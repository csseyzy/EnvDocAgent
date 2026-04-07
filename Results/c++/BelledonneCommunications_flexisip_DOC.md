# flexisip Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Build System:** CMake + Ninja

## Prerequisites

```bash
apt-get update && apt-get install -y \
    gcc-14=14.2.0-4ubuntu2 \
    g++-14=14.2.0-4ubuntu2 \
    cmake=3.28.3-1build7 \
    ninja-build=1.11.1-2 \
    make=4.3-4.1build2 \
    python3=3.12.3-0ubuntu2 \
    python3-pystache=0.6.5-1 \
    python3-six=1.16.0-4 \
    doxygen=1.9.8+ds-2build5 \
    yasm=1.3.0-4 \
    libssl-dev=3.0.13-0ubuntu3 \
    libboost-dev=1.83.0.1ubuntu2 \
    libboost-system-dev=1.83.0.1ubuntu2 \
    libboost-thread-dev=1.83.0.1ubuntu2 \
    libcpp-jwt-dev=1.4+ds-3 \
    libhiredis-dev=0.14.1-4 \
    libjansson-dev=2.14-2build2 \
    libjsoncpp-dev=1.9.5-6build1 \
    libsqlite3-dev=3.45.1-1ubuntu2 \
    libpq-dev=16.2-1ubuntu4 \
    default-libmysqlclient-dev=1.1.0-1ubuntu1 \
    libnghttp2-dev=1.59.0-1build1 \
    libsnmp-dev=5.9.4+dfsg-1.1ubuntu3 \
    libxerces-c-dev=3.2.4+debian-1.2build1 \
    libsrtp2-dev=2.5.0-2build1 \
    libgsm1-dev=1.0.22-1build1 \
    libopus-dev=1.4-1build1 \
    libmbedtls-dev=2.28.8-1 \
    libspeex-dev=1.2.1-2ubuntu2 \
    libspeexdsp-dev=1.2.1-1build2 \
    libxml2-dev=2.9.14+dfsg-1.3ubuntu3 \
    redis-server=5:7.0.15-1build2 \
    libvpx-dev=1.14.0-1ubuntu2 \
    libavcodec-dev=7:6.1.1-3ubuntu5 \
    libavutil-dev=7:6.1.1-3ubuntu5 \
    libswscale-dev=7:6.1.1-3ubuntu5 \
    libasound2-dev=1.2.11-1build2 \
    libpulse-dev=1:16.1+dfsg1-2ubuntu10 \
    libturbojpeg0-dev=2.1.5-2ubuntu2 \
    libv4l-dev=1.26.1-4build1 \
    libxv-dev=2:1.0.11-1.1build1 \
    libbsd-dev=0.12.1-1build1 \
    libprotobuf-dev=3.21.12-8.2build1 \
    protobuf-compiler=3.21.12-8.2build1 \
    xsdcxx=4.2.0-3build1 \
    mariadb-server=1:10.11.7-0ubuntu0.24.04.1 \
    git=1:2.43.0-1ubuntu7
```

## Build Steps

```bash
# MySQL client library compatibility
ln -s /usr/lib/x86_64-linux-gnu/libmysqlclient.so /usr/lib/x86_64-linux-gnu/libmariadbclient.so

# Full git history required for version detection
git fetch --unshallow
```


```bash
cd /app/project
git submodule update --init --recursive

export CC=gcc-14 CXX=g++-14
cmake -S . -B ./build -G "Ninja" \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_INSTALL_PREFIX="/app/project/build/install" \
    -DENABLE_UNIT_TESTS=ON \
    -DENABLE_STRICT_LINPHONESDK=OFF \
    -DINTERNAL_JSONCPP=OFF

cmake --build ./build -j$(nproc)
```

## Test Steps

```bash
cd /app/project/build
bin/flexisip_tester --resource-dir "../tester/" 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- Requires gcc >= 14 or clang >= 20 (C++20 standard)
- The linphone-sdk submodule must be recursively cloned
- MariaDB vs MySQL client library conflict on Ubuntu 24.04 — needs symlink
- Full git history required — `git clone --depth 1` is insufficient (build uses `git describe`)
