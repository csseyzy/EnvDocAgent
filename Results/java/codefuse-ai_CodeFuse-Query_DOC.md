# CodeFuse-Query Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: default-jdk (OpenJDK 21 on Ubuntu 24.04)
- Also requires: Python 3, Node.js/npm, Clang 18, CMake, Bazel

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 locales curl=8.5.0-2ubuntu10.8 jq tar \
    build-essential=12.10ubuntu1 cmake=3.28.3-1build7 python3=3.12.3-0ubuntu2 python3-pip=24.0+dfsg-1ubuntu1.1 nodejs npm clang=1:18.0-59~exp2 libclang-dev \
    sqlite3 libsqlite3-dev=3.45.1-1ubuntu2 default-jdk unzip=6.0-28ubuntu4 pkg-config=1.8.1-2build1 \
    m4=1.4.19-4build1 flex=2.6.4-8.2build1 bison=2:3.8.2+dfsg-1build2 zlib1g-dev=1:1.3.dfsg-3.1ubuntu2 file=1:5.45-3build1 libffi-dev
```


## Build Steps

```bash
locale-gen zh_CN.UTF-8
export LANG=zh_CN.UTF-8
export LANGUAGE=zh_CN:zh:en_US:en
export LC_ALL=zh_CN.UTF-8

ln -sf /usr/bin/python3 /usr/bin/python
ln -sf /usr/bin/clang-18 /usr/bin/clang
ln -sf /usr/bin/clang++-18 /usr/bin/clang++

python3 -m pip install --upgrade pip==24.0
```

Install Bazelisk:

```bash
curl -fL https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    -o /usr/local/bin/bazel
chmod +x /usr/local/bin/bazel
```


```bash
git clone --recurse-submodules https://github.com/codefuse-ai/CodeFuse-Query project
cd project
```


```bash
git config --global user.name "CI"
git config --global user.email "ci@example.com"

cd /app/project/godel-script/godel-backend/souffle
git am ../0001-init-self-used-souffle-from-public-souffle.patch
cd ../..

mkdir -p build && cd build
cmake ..
make -j$(nproc)
```


```bash
cd /app/project
bazel build //...
```


After Bazel build, fix libstdc++ mismatch for godel binary:

```bash
cd /root/.cache/bazel/_bazel_root/*/execroot/__main__/bazel-out/k8-opt/bin/godel-script/usr/lib64
rm -f libstdc++.so.6
ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 libstdc++.so.6
```


## Test Steps

```bash
cd /app/project/godel-script
export LD_LIBRARY_PATH=/app/project/godel-script/build/godel-backend/souffle/src:$LD_LIBRARY_PATH
./build/godel
./build/godel --version
./build/godel -h --color-off
```


## Unexpected Issues

- **Full `bazel build //...` may fail** at LLVM compilation step. This is an external dependency issue, not a project code bug. The godel-script component builds successfully via CMake.
- **Souffle patch required.** Must apply `0001-init-self-used-souffle-from-public-souffle.patch` in the souffle submodule before CMake build.
- **Clang symlinks required.** Ubuntu 24.04 installs `clang-18` but the build expects `clang`. Must create symlinks.
- **libstdc++ mismatch.** Bazel-packaged `libstdc++.so.6` may have GLIBCXX version mismatch. Must symlink to system version.
- **Bazel rule naming conflict.** Warning in `language/javascript/extractor/BUILD:128`.
- **zh_CN.UTF-8 locale required.** Some components expect Chinese locale.
- **Git config required for `git am`.** Must set `user.name` and `user.email` before applying the souffle patch.
