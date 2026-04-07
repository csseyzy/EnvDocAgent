# vision_msgs Deployment Document

## Platform

- OS: Ubuntu 24.04 (noble)
- ROS: ROS 2 Jazzy
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    software-properties-common=0.99.48 curl=8.5.0-2ubuntu10.8 gnupg2 lsb-release \
    build-essential=12.10ubuntu1

curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
    http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/ros2.list

apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-ros-base \
    ros-jazzy-ament-cmake \
    ros-jazzy-ament-cmake-gtest \
    ros-jazzy-sensor-msgs \
    ros-jazzy-geometry-msgs \
    ros-jazzy-std-msgs \
    python3-colcon-common-extensions \
    python3-rosdep

rosdep init || true && rosdep update
```

## Build Steps

```bash
git clone --depth 1 -b ros2 https://github.com/ros-perception/vision_msgs.git /app/project
cd /app/project
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths . --ignore-src -r -y
colcon build --packages-select vision_msgs
```

## Test Steps

```bash
source /opt/ros/jazzy/setup.bash
colcon test --packages-select vision_msgs
colcon test-result --all --verbose
```

## Unexpected Issues

- `build-essential` not in ROS base image: CMake fails without compilers. Must install separately.
- `vision_msgs_rviz_plugins` fails on Jazzy due to API mismatch. Only build `vision_msgs`.
