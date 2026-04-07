# tensile Deployment Document

## Platform

- Base image: `php:7.2-cli` (Debian Buster, GCC 8.3.0)
- C standard: C99
- Compiler: GCC 8.3.0
- TensorFlow C API 1.15.0 (CPU)
- PHP 7.2.34 development headers (required for Zend Engine API target)

## Prerequisites

Debian Buster is EOL, APT sources must point to archive:

```bash
rm -f /etc/apt/sources.list
printf "deb http://archive.debian.org/debian buster main\n" > /etc/apt/sources.list
printf "deb http://archive.debian.org/debian buster-updates main\n" >> /etc/apt/sources.list
```

```bash
apt-get -o Acquire::Check-Valid-Until=false update && \
    apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7 \
    autoconf=2.69-11 \
    gcc=4:8.3.0-1 \
    g++=4:8.3.0-1 \
    make=4.2.1-1.2 \
    libc-dev \
    pkg-config=0.29-6 \
    curl=7.64.0-4+deb10u9 \
    ca-certificates=20240203
```

Download TensorFlow C shared library:

```bash
curl -L https://storage.googleapis.com/tensorflow/libtensorflow/libtensorflow-cpu-linux-x86_64-1.15.0.tar.gz -o /tmp/libtf.tgz
tar -C /app/project -xzf /tmp/libtf.tgz
export LD_LIBRARY_PATH=/app/project/lib:${LD_LIBRARY_PATH}
```

## Build Steps

```bash
cd /app/project

# Generate configure script from config.m4 (autotools)
phpize

# Configure: detect TensorFlow C headers and .so in project root include/ and lib/
./configure --enable-tensile

# Compile C source into shared library tensile.so
make -j1

# Install .so to PHP extension directory
make install

# Register the shared library
echo "extension=tensile.so" > /usr/local/etc/php/conf.d/20-tensile.ini
```

## Test Steps

```bash
cd /app/project
NO_INTERACTION=1 REPORT_EXIT_STATUS=1 TEST_PHP_ARGS="-q" make test
```

## Unexpected Issues

- **GCC version constraint**: Must use GCC 8.x (Debian Buster). The C source uses Zend Engine 3.2 macros (`Z_PARAM_STR`) that have ABI-incompatible changes in newer versions.
- **TensorFlow C API version**: Must use 1.15.0. TensorFlow 2.x C API changes struct layouts and function signatures used by this code.
- **Debian Buster EOL**: All `apt-get update` must use `-o Acquire::Check-Valid-Until=false`.
- **Linker path**: `LD_LIBRARY_PATH` must include `lib/` at project root, otherwise `libtensorflow.so` cannot be found at link time and runtime.

