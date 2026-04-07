# pycdc Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- CMake: 3.28
- Python: 3.12
- GCC: 13.x

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    cmake=3.28.3-1build7 \
    build-essential=12.10ubuntu1 \
    python3=3.12.3-0ubuntu2
```

## Build Steps

```bash
cd /app/project
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo ..
make -j$(nproc)
```

## Test Steps

```bash
cd /app/project/build
cmake --build . --target check
```

Or equivalently:

```bash
cd /app/project/build
make check
```


## Unexpected Issues

- CMake must find Python 3 at configure time; if it does not, the `check` target is not created
- The test harness is a custom Python script, not CTest or GoogleTest
- Tests compare tokenized output (not raw source text) to handle whitespace/comment differences
- Test failures write diff artifacts to `tests-out/` in the build directory
- Expected failures are tracked in `tests/xfail/` and reported separately
