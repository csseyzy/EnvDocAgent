# SlamBook Deployment Document

## Platform

- **Base Image:** ubuntu:20.04
- **Build System:** CMake

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.25.1-1ubuntu3 \
    build-essential=12.8ubuntu1 \
    cmake=3.16.3-1ubuntu1 \
    pkg-config=0.29.1-0ubuntu4 \
    libeigen3-dev \
    libopencv-dev \
    libpcl-dev \
    liboctomap-dev \
    libboost-all-dev \
    libgflags-dev \
    libgoogle-glog-dev \
    libatlas-base-dev \
    libsuitesparse-dev \
    wget=1.20.3-1ubuntu2
```

```bash
# Sophus (pinned commit)
git clone https://github.com/strasdat/Sophus.git && cd Sophus
git checkout 13fb3288311485e74b6d8f7b95d5d1e030c08b73
mkdir build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j$(nproc) && make install
```

## Build Steps

```bash
sed -i 's|/usr/local/Cellar/eigen/3.3.4/include/eigen3|/usr/include/eigen3|g' ch13/CMakeLists.txt
```


```bash
cd /app/project
mkdir build && cd build
cmake .. && make -j$(nproc)
```

## Test Steps

```bash
cd /app/project/build
ctest --output-on-failure 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This project genuinely has no automated tests — `ch9/test/test_slam.cpp` is a visual odometry demo requiring TUM RGB-D datasets
- The `ctest` command may find zero tests
- Most chapters are independent executables that require input data (images, point clouds)
- The Eigen3 path in `ch13/CMakeLists.txt` is hardcoded to macOS Homebrew path — must be patched
