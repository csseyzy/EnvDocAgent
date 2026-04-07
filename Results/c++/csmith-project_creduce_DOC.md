# creduce Deployment Document

## Platform

- Base image: `ubuntu:18.04`
- LLVM/Clang: 9.x
- CMake: 3.x
- Build system: CMake + Make

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.17.1-1ubuntu0.18 \
    build-essential=12.4ubuntu1 \
    cmake \
    flex \
    zlib1g-dev \
    libedit-dev \
    libexporter-lite-perl \
    libfile-which-perl \
    libgetopt-tabular-perl \
    libregexp-common-perl \
    libterm-readkey-perl \
    python3 \
    wget \
    gnupg \
    software-properties-common

wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -
echo "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-9 main" >> /etc/apt/sources.list.d/llvm.list
apt-get update && apt-get install -y \
    llvm-9 llvm-9-dev clang-9 libclang-9-dev clang-format-9
```

## Build Steps

```bash
cd /app/project
export CC=clang-9 CXX=clang++-9

mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_PREFIX_PATH=/usr/lib/llvm-9 ..
make -j$(nproc)
```

## Test Steps

### clang_delta unit tests (LLVM lit)

```bash
cd /app/project/build
cmake --build . --target check-clang-delta
```

### End-to-end creduce tests (Perl driver)

```bash
cd /app/project/build
mkdir -p tests && cd tests
for f in run_tests test0.bat test0.sh test1.sh test2.sh test3.sh test4.sh test5.sh test6.sh test7.sh file1.c file2.c file3.c; do
  ln -sf /app/project/tests/$f .
done
perl run_tests
```

## Unexpected Issues

- The project requires LLVM 9.x specifically; newer LLVM versions may need the `llvm-svn-compatible` branch
- `clang_delta` tests use LLVM's `llvm-lit` test runner — the LLVM installation must include it
- End-to-end tests use a custom Perl driver (`tests/run_tests`), not CTest or GoogleTest
- `clang-format` must be on PATH for creduce to function (provided by `clang-format-9`)
- `make check` from the Autotools build does NOT run the full test suite — use the CMake targets above instead
