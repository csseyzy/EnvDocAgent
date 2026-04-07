# ros2_java Deployment Document

## Platform

- **Base Image:** `ros:humble-ros-base-jammy` (recommended since Galactic is EOL)
- **JDK:** JDK 11 (default-jdk on Ubuntu 22.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    default-jdk=2:1.11-72build2 \
    gradle=4.4.1-13 \
    python3-colcon-common-extensions=0.3.0-1 \
    python3-vcstool=0.3.0-1 \
    python3-pip=22.0.2+dfsg-1ubuntu0.4 \
    python3-rosdep=0.22.2-1 \
    python3-dev=3.10.6-1~22.04 \
    curl=7.81.0-1ubuntu1 \
    build-essential=12.9ubuntu3 \
    cmake=3.22.1-1ubuntu1.22.04.2 \
    ca-certificates=20240203
```

### Install colcon Gradle extensions

```bash
pip3 install git+https://github.com/colcon/colcon-gradle.git
pip3 install --no-deps git+https://github.com/colcon/colcon-ros-gradle.git
```

## Build Steps

### Step 1: Source ROS and create workspace

```bash
source /opt/ros/humble/setup.bash
mkdir -p /ros2_java_ws/src
cd /ros2_java_ws
```

### Step 2: Import repos (update branch references for Humble)

```bash
curl -skL https://raw.githubusercontent.com/ros2-java/ros2_java/main/ros2_java_desktop.repos \
    | sed 's/version: galactic/version: humble/g' \
    | vcs import src
```

### Step 3: Install ROS dependencies

```bash
rosdep update
rosdep install --from-paths src -y -i --skip-keys "ament_tools"
```

### Step 4: Build

```bash
colcon build --symlink-install
```

## Test Steps

```bash
source install/setup.bash
colcon test --packages-select rosidl_generator_java rcljava_common rcljava
colcon test-result --verbose
```

## Unexpected Issues

- **ROS Galactic is EOL** — binary packages removed from ROS apt repository. Use ROS Humble instead.
- On plain Ubuntu (without ROS apt sources), `python3-colcon-common-extensions`, `python3-vcstool` are **not available** via apt.
- The `ros2_java_desktop.repos` file pins ROS interface repos to `galactic` branch — must change to `humble` when using ROS Humble.
- `colcon build` is very long (30-60 minutes) — generates Java bindings for all ROS message types.
- The `--no-deps` flag is used for `colcon-ros-gradle` pip install to avoid pulling incompatible colcon versions.
- Build involves JNI compilation requiring both JDK and C++ toolchain.
