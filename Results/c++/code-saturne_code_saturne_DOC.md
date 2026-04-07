# code_saturne Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Build System:** Autotools (autoconf/automake)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.10ubuntu1 \
    gfortran=4:13.2.0-7ubuntu1 \
    autoconf=2.71-3 \
    automake=1:1.16.5-1.3ubuntu1 \
    libtool=2.4.7-7build1 \
    pkg-config=1.8.1-2build1 \
    python3=3.12.3-0ubuntu2 \
    python3-dev=3.12.3-0ubuntu2 \
    python3-pip=24.0+dfsg-1ubuntu1 \
    libopenmpi-dev=4.1.6-7ubuntu2 \
    openmpi-bin=4.1.6-7ubuntu2 \
    libblas-dev=3.12.0-3build1 \
    liblapack-dev=3.12.0-3build1 \
    zlib1g-dev=1:1.3.dfsg-3.1ubuntu2 \
    libhdf5-dev=1.10.10+repack-3.1ubuntu4 \
    libcgns-dev=4.4.0+dfsg1-2build1 \
    libscotch-dev=7.0.4-1build2 \
    libmetis-dev=5.1.0.dfsg-7build4 \
    doxygen=1.9.8+ds-2build5 \
    graphviz=2.43.0-6ubuntu2 \
    wget=1.21.4-1ubuntu4 \
    git=1:2.43.0-1ubuntu7
```

## Build Steps

```bash
cd /app/project
./sbin/bootstrap

cd /app && mkdir -p build && cd build
../project/configure --prefix=/app/install --disable-gui
make -j$(nproc)
make install
```

## Test Steps

```bash
cd /app/build

# Build test binaries
make check

# Run individual test binaries (make check only builds, doesn't execute):
cd tests
./bft_backtrace_test
./bft_error_test
./bft_mem_usage_test
./bft_mem_test
./bft_printf_test
./cs_core_test
./cs_file_test
./cs_geom_test
./cs_map_test
./cs_sizes_test
./cs_tree_test
./cs_rank_neighbors_test
./cs_random_test

# MPI tests:
mpirun --allow-run-as-root -np 2 ./cs_all_to_all_test
mpirun --allow-run-as-root -np 2 ./cs_interface_test

# Tests compiled via cs_compile_build.py:
PYTHONPATH=/app/project/python/code_saturne/base \
    python3 -B /app/project/build-aux/cs_compile_build.py \
    -o cs_blas_test /app/project/tests/cs_blas_test.cpp
./cs_blas_test
```

## Unexpected Issues

- `make check` builds but **doesn't run tests** — `TESTS=$(check_PROGRAMS)` is commented out in `tests/Makefile.am`
- Must run each test binary individually
- Many test binaries are compiled via a custom Python build script (`cs_compile_build.py`), not standard automake
- MPI tests need `mpirun --allow-run-as-root` in Docker
- Out-of-source build is required
- The GitHub repo URL uses underscore (`code_saturne`) not hyphen
