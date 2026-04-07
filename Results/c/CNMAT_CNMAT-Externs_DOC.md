# CNMAT-Externs Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    cmake=3.28.3-1build7 \
    pkg-config=1.8.1-2build1 \
    doxygen=1.9.8+ds-2build5 \
    flex=2.6.4-8.2build1 \
    bison=2:3.8.2+dfsg-1build2 \
    autoconf=2.71-3 \
    automake=1:1.16.5-1.3ubuntu1 \
    libtool=2.4.7-7build1
```

## Build Steps

```bash
cd /app/cnmat_externs

# Build cmmjl sub-library
mkdir -p SDK/MaxSDK-5/c74support/max-includes
git clone https://github.com/Cycling74/max-sdk-base /tmp/max-sdk-base
cp -r /tmp/max-sdk-base/c74support/max-includes/* SDK/MaxSDK-5/c74support/max-includes/
cmake -S cmmjl -B build-cmmjl
cmake --build build-cmmjl
```

## Test Steps

The test files are in `lib/gsl/` (a bundled GNU Scientific Library copy) which uses autotools:

```bash
cd /app/cnmat_externs/lib/gsl
./configure
make -j$(nproc)
make check
```

## Unexpected Issues

- The cmmjl CMakeLists.txt has no `enable_testing()` or `add_test()` calls -- `ctest` reports "No tests were found"
- The 136 "test files" are GSL library tests (a vendored dependency), not tests of CNMAT-Externs itself
- `cmmjl/test/cmmjl_test/` is a Max/MSP external (requires the Max runtime) -- not a standalone test
- GSL configure/build is heavyweight and takes significant time
