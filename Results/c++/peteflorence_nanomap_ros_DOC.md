# nanomap_ros Deployment Document

## Platform

- **Base Image:** ubuntu:20.04
- **Build System:** catkin (ROS Noetic)

## Prerequisites

```bash
# ROS Noetic repository setup
sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list'
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add -

apt-get update && apt-get install -y \
    build-essential=12.8ubuntu1 \
    cmake=3.16.3-1ubuntu1 \
    curl=7.68.0-1ubuntu2 \
    gnupg2=2.2.19-3ubuntu2 \
    lsb-release=11.1.0ubuntu2 \
    ros-noetic-desktop-full=1.5.0-1focal \
    python3-rosdep=0.22.2-1 \
    python3-rosinstall=0.7.8-4 \
    python3-wstool=0.1.18-2 \
    libeigen3-dev=3.3.7-2 \
    libopencv-dev=4.2.0+dfsg-5 \
    libpcl-dev=1.10.0+dfsg-5ubuntu1 \
    ros-noetic-pcl-ros=1.7.4-1focal \
    ros-noetic-cv-bridge=1.16.2-1focal \
    ros-noetic-image-transport=1.12.0-1focal

rosdep init || true && rosdep update
```

## Build Steps

```bash
mkdir -p /catkin_ws/src
cd /catkin_ws/src
git clone --depth 1 https://github.com/peteflorence/nanomap_ros

cd /catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make
```

## Test Steps

```bash
source /opt/ros/noetic/setup.bash
source /catkin_ws/devel/setup.bash
catkin_make run_tests_nanomap_ros 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- **Must use Ubuntu 20.04** — ROS Noetic is only officially supported on Ubuntu 20.04 (Focal)
- `ros-noetic-desktop-full` is a very large metapackage (~2GB+); could use `ros-noetic-ros-base` + specific packages to speed up Docker build
- Tests use Google Test (gtest) via catkin's `catkin_add_gtest`
- Almost all time was spent installing ROS packages, not building/testing
