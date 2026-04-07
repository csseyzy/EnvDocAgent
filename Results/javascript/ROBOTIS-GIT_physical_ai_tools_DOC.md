# physical_ai_tools Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- ROS 2: Jazzy
- Node.js: 20.x (for React web UI)
- Python: 3.12

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 software-properties-common=0.99.48 curl=8.5.0-2ubuntu10.8 locales gnupg2 lsb-release
locale-gen en_US.UTF-8
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2.list
apt-get update && apt-get install -y ros-jazzy-ros-base python3-rosdep python3-colcon-common-extensions python3-pip=24.0+dfsg-1ubuntu1.1 build-essential=12.10ubuntu1
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
rosdep init || true && rosdep update
```

## Build Steps

### ROS 2 Packages

```bash
cd /app/physical_ai_tools
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths . --ignore-src -y -r --rosdistro jazzy
colcon build --packages-select physical_ai_server physical_ai_interfaces rosbag_recorder physical_ai_bt
```

### React Web UI (the testable component)

```bash
cd /app/physical_ai_tools/physical_ai_manager
npm install
```

## Test Steps

### ROS 2 packages (no test cases defined)

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
colcon test --packages-select physical_ai_server physical_ai_interfaces rosbag_recorder physical_ai_bt
colcon test-result --verbose
```

### React Web UI (has actual tests)

```bash
cd /app/physical_ai_tools/physical_ai_manager
CI=true npm test -- --watchAll=false
```

## Unexpected Issues

- The ROS 2 packages have zero test cases (only `tests_require=['pytest']` declared but no test files)
- `CI=true` and `--watchAll=false` are needed because `react-scripts test` runs in watch mode by default
