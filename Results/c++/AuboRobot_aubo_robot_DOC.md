# aubo_robot Deployment Document

## Platform

- **Base Image:** ubuntu:16.04
- **Build System:** catkin (ROS Kinetic)

## Prerequisites

```bash
# ROS Kinetic repository setup
sh -c 'echo "deb http://packages.ros.org/ros/ubuntu xenial main" > /etc/apt/sources.list.d/ros-latest.list'
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add -

apt-get update && apt-get install -y \
    lsb-release \
    gnupg2 \
    curl=8.5.0-2ubuntu10.8 \
    git=1:2.43.0-1ubuntu7 \
    ros-kinetic-desktop-full \
    python-rosdep \
    python-rosinstall \
    python-catkin-tools \
    ros-kinetic-moveit \
    ros-kinetic-industrial-core \
    ros-kinetic-moveit-visual-tools \
    libev-dev

rosdep init || true && rosdep update
```

## Build Steps

```bash
mkdir -p /root/catkin_ws/src
cd /root/catkin_ws/src
git clone --depth 1 https://github.com/AuboRobot/aubo_robot

cd /root/catkin_ws
source /opt/ros/kinetic/setup.bash
catkin_make

# Update MoveIt libraries
cd /root/catkin_ws/src/aubo_robot/UpdateMoveitLib/Kinetic
chmod +x Update.sh && ./Update.sh || true
```

## Test Steps

```bash
source /opt/ros/kinetic/setup.bash
source /root/catkin_ws/devel/setup.bash
catkin_make run_tests 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- **Must use Ubuntu 16.04** — ROS Kinetic is only officially supported on Ubuntu 16.04 (Xenial)
- `ros-kinetic-desktop-full` is a very large metapackage; most time is spent on package installation
- Tests are gtest-based in `industrial_core` (joint names, message serialization, robot client)
- The `Update.sh` script updates MoveIt libraries and may fail silently
