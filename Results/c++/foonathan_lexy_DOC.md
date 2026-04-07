# lexy Deployment Document

## Platform

- CMake 3.10
- Ninja 1.10
- GCC 9.4.0 (C++11)

## Prerequisites

sudo apt-get install -y build-essential cmake ninja-build libboost-all-dev

## Build Steps

```bash
# 1. Clone project
git clone https://github.com/foonathan/lexy.git
cd lexy
# 2. Install dependencies (Ubuntu/Debian)
sudo apt-get update -y
# 3. Configure environment variables (none required for build/tests)
echo "# No environment variables required" > .env
# 4. Initialize (if needed)
echo "No initialization required"
# 5. Configure and build (Debug configuration)
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j 2

```
## Test Steps

See Build Steps above for verification commands.

## Unexpected Issues

- CMake not installed — install with `sudo apt-get install -y cmake=3.28.3-1build7`.
- Ninja build system not installed — install with `sudo apt-get install -y ninja-build=1.11.1-2`.
- C++ compiler toolchain missing — install with `sudo apt-get install -y build-essential=12.10ubuntu1`.
