# realtime_tools Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Build System:** colcon (ROS 2 Jazzy)

## Prerequisites

```bash
# ROS 2 repository setup
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

apt-get update && apt-get install -y --no-install-recommends \
    locales software-properties-common=0.99.48 curl=8.5.0-2ubuntu10.8 gnupg2 lsb-release \
    ros-jazzy-ros-base \
    ros-jazzy-ament-cmake \
    ros-jazzy-ament-cmake-gtest \
    ros-jazzy-realtime-tools \
    ros-jazzy-test-msgs \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-control-cmake \
    ros-jazzy-ros2-control-test-assets \
    python3-colcon-common-extensions \
    python3-pytest \
    build-essential=12.10ubuntu1 \
    cmake=3.28.3-1build7 \
    pkg-config=1.8.1-2build1 \
    libcap-dev=1:2.66-5ubuntu2.2

locale-gen en_US en_US.UTF-8
update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
```

## Build Steps

```bash
mkdir -p /app/ws/src
cd /app/ws/src
git clone --depth 1 https://github.com/ros-controls/realtime_tools

cd /app/ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select realtime_tools --cmake-args -DBUILD_TESTING=ON
```

## Test Steps

```bash
source /opt/ros/jazzy/setup.bash
source /app/ws/install/setup.bash
colcon test --packages-select realtime_tools
colcon test-result --verbose 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- ROS 2 ecosystem has massive dependency chains — installing `ros-jazzy-ros2-control` is critical but was missed initially
- Most of the 76 minutes was spent on failed Docker image builds, not actual compilation
