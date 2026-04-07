# cppast Deployment Document

## Platform

- CMake 3.11.0
- LLVM/Clang 18.1
- libclang 18 (development headers)
- Ninja 1.10

## Prerequisites

sudo apt-get install -y git
sudo apt-get install -y cmake clang-18 llvm-18-dev libclang-18-dev ninja-build

## Build Steps

```bash
# 0. Install git (Ubuntu/Debian)
sudo apt-get -qq update
# 1. Clone project
git clone https://github.com/foonathan/cppast.git
cd cppast
# 2. Install system dependencies (Ubuntu/Debian)
sudo apt-get -qq update
# 2.1 Verify required toolchain versions (ensure Clang/LLVM 18; ensure CMake >= 3.11; ensure Ninja >= 1.10)
clang-18 --version | head -n1
llvm-config-18 --version
cmake --version | head -n1
# Requirement: at least CMake 3.11.0 (expected line starts with: cmake version 3.11 or newer)
ninja --version
# Enforce version requirements (will exit with error if not met)
clang-18 --version | head -n1 | grep -q 'clang version 18' || { echo 'Error: require Clang 18'; exit 1; }
llvm-config-18 --version | grep -q '^18' || { echo 'Error: require LLVM 18'; exit 1; }
ver=$(cmake --version | head -n1 | awk '{print $3}'); dpkg --compare-versions "$ver" ge "3.11.0" || { echo 'Error: require CMake >= 3.11'; exit 1; }
nver=$(ninja --version); dpkg --compare-versions "$nver" ge "1.10" || { echo 'Error: require Ninja >= 1.10'; exit 1; }
# 3. Configure and build (Release, C++11) using Ninja generator and Clang 18 compilers
cmake -E make_directory build
cd build
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=11 -DCMAKE_C_COMPILER=clang-18 -DCMAKE_CXX_COMPILER=clang++-18 ..
cmake --build . -j
# 4. Run tests to verify build
ctest --output-on-failure
```

## Test Steps

```bash
ctest --output-on-failure
```

## Unexpected Issues

- `No CMAKE_CXX_COMPILER could be found` — CMake cannot find a C++ compiler on minimal systems. Install with `sudo apt-get install -y clang-18`.
- CMake version too old (< 3.11.0) — system CMake does not meet the minimal requirement. Install with `sudo apt-get install -y cmake=3.28.3-1build7`.
- `Could NOT find libclang` (or clang-c headers) — libclang development files not installed. Install with `sudo apt-get install -y libclang-18-dev`.
- `In-source builds are not supported` — must use out-of-source build directory (`cmake -E make_directory build && cd build`).
- Tests fail to run or are not found — build directory not used for running tests or build not completed. Run `cd build && ctest --output-on-failure`.
- `Ninja generator requested but Ninja not found` — Ninja not installed. Install with `sudo apt-get install -y ninja-build=1.11.1-2`.
- LLVM/Clang version mismatch — system installed LLVM/Clang version differs from the required version. Install with `sudo apt-get install -y clang-18 libclang-18-dev llvm-18-dev`.
