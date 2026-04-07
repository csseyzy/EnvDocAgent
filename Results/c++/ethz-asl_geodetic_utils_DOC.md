# geodetic_utils Deployment Document

## Platform

- OS: Ubuntu 20.04 (focal), glibc 2.31
- ROS: ROS Noetic
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    lsb-release gnupg2 curl=8.5.0-2ubuntu10.8 ca-certificates=20240203

sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" \
    > /etc/apt/sources.list.d/ros-latest.list'
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add -

apt-get update && apt-get install -y --no-install-recommends \
    ros-noetic-ros-base \
    ros-noetic-catkin \
    python3-catkin-tools \
    python3-rosdep \
    python3-rosinstall python3-rosinstall-generator python3-wstool \
    build-essential=12.10ubuntu1 cmake=3.28.3-1build7 \
    libgdal-dev pkg-config=1.8.1-2build1 libeigen3-dev \
    ros-noetic-tf=1.13.4-1focal* \
    ros-noetic-tf-conversions=1.13.4-1focal* \
    ros-noetic-tf2=0.7.10-1focal* \
    ros-noetic-tf2-ros=0.7.10-1focal*

rosdep init || true && rosdep update
```

## Build Steps

```bash
mkdir -p /app/catkin_ws/src && cd /app/catkin_ws/src
git clone --depth 1 https://github.com/catkin/catkin_simple.git
git clone --depth 1 https://github.com/ethz-asl/geodetic_utils.git
cd /app/catkin_ws
source /opt/ros/noetic/setup.bash
catkin build
```

## Test Steps

```bash
cd /app/catkin_ws
source devel/setup.bash
catkin run_tests
```
## Unexpected Issues

- Missing `tf` packages: `ros-noetic-ros-base` does not include `tf`. Install `ros-noetic-tf` (1.13.4), `ros-noetic-tf-conversions` (1.13.4), `ros-noetic-tf2` (0.7.10), `ros-noetic-tf2-ros` (0.7.10) explicitly.
- `catkin_simple` not in ROS repos: must clone from `https://github.com/catkin/catkin_simple.git`.
- `rosdep` cannot resolve `tf` keys; install packages via apt directly.
