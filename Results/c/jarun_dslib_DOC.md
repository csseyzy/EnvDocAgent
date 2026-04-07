# dslib Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Compiler: gcc 13

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.10ubuntu1 \
    gcc=4:13.2.0-7ubuntu1 \
    binutils=2.42-4ubuntu2 \
    make=4.3-4.1build2 \
    cmake=3.28.3-1build7 \
    ca-certificates=20240203
```

## Build Steps

### Using Make (primary)

```bash
cd /app/dslib
make
make install
ldconfig
make test
```

### Using CMake (alternative)

```bash
cd /app/dslib
mkdir build && cd build
cmake ..
make
```

## Test Steps

### Using Make

```bash
cd /app/dslib/test
timeout 60 ./test_dlist_1
timeout 60 ./test_queue_1
timeout 60 ./test_stack_1
timeout 60 ./test_bst_1
timeout 60 ./test_avl_1
timeout 120 ./avl_Thread_Safe_Test
```

### Using CTest

```bash
cd /app/dslib/build
ctest --output-on-failure --timeout 120
```

## Unexpected Issues

- **`avl_Thread_Safe_Test` can hang or run indefinitely** under AddressSanitizer/UndefinedBehaviorSanitizer -- always use `timeout`
- Tests are compiled with `-fsanitize=address,undefined -lpthread` which significantly slows execution
- Tests statically link all `src/*.c` files (not linking against installed `libds.so`), so `make install` is technically not required for test compilation
- The CMake build path properly registers CTest targets and is the more robust option for CI
- Only 1 Docker build was needed -- the build itself was fine, only the test execution timed out
