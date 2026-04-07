# clang-llvm-tutorial Deployment Document

## Platform

- **Base Image:** ubuntu:20.04
- **Build System:** Make (with llvm-config)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.25.1-1ubuntu3 \
    build-essential=12.8ubuntu1 \
    cmake=3.16.3-1ubuntu1 \
    python3=3.8.2-0ubuntu2 \
    llvm-10 \
    llvm-10-dev \
    llvm-10-tools \
    clang-10 \
    libclang-10-dev \
    libtinfo-dev \
    libxml2-dev \
    zlib1g-dev \
    libedit-dev

ln -sf /usr/bin/llvm-config-10 /usr/bin/llvm-config
ln -sf /usr/bin/clang-10 /usr/bin/clang
ln -sf /usr/bin/clang++-10 /usr/bin/clang++
```

## Build Steps

Fix LLVM API breaking change — `TerminatorInst` was removed in LLVM 10+:
```bash
cd /app/project/live-variable-analysis
sed -i 's/!(isa<TerminatorInst>(ii))/!ii->isTerminator()/g' LiveVariable.cpp
```


```bash
cd /app/project/live-variable-analysis
make clean && make
```

## Test Steps

```bash
cd /app/project/live-variable-analysis
./test.sh 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- `TerminatorInst` was removed in LLVM 10+ — must use `isTerminator()` method instead
- Must use LLVM 10 on Ubuntu 20.04 (newer LLVM versions may introduce additional API changes)
- Most of the 67 minutes was spent on agent exploring different LLVM versions and patching strategies
