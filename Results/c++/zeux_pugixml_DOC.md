# pugixml Deployment Document

## Platform

- OS: Ubuntu 24.04
- Version: 1.15

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    cmake=3.28.3-1build7 \
    make=4.3-4.1build2
```

- `build-essential` (GCC 13.3.0, g++ 13.3.0) — C++ toolchain
- `cmake` (3.28.3) — CMake build system (optional, for CMake build path)
- `make` (4.3) — GNU Make

## Build Steps

### Option A: Make

```bash
git clone --depth 1 https://github.com/zeux/pugixml.git /app/project
cd /app/project
make all -j$(nproc)
```

### Option B: CMake

```bash
git clone --depth 1 https://github.com/zeux/pugixml.git /app/project
cd /app/project
mkdir -p build && cd build
cmake .. -DPUGIXML_BUILD_TESTS=ON
cmake --build . -j$(nproc)
```

## Test Steps

### Option A: Make

```bash
cd /app/project
make test -j$(nproc)
```

Runs the built test binary automatically. Additional test configurations:

```bash
make test cxxstd=c++11 config=release -j$(nproc)
make test cxxstd=c++17 config=debug -j$(nproc)
make test config=sanitize -j$(nproc)
```

### Option B: CMake

```bash
cd /app/project/build
ctest --output-on-failure
```

## Unexpected Issues

- `make test` compiles and runs in one step; there is no separate build-then-test workflow needed with Make.
- CMake tests require `-DPUGIXML_BUILD_TESTS=ON` at configure time; tests are not built by default.
- The default C++ standard is 17 (with CMake >= 3.8) but `CMAKE_CXX_STANDARD_REQUIRED` is OFF, so the compiler may fall back to a lower standard if 17 is not supported.
- Sanitizer tests (`config=sanitize`) require a compiler with AddressSanitizer and UndefinedBehaviorSanitizer support.
