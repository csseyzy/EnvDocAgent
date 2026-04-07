# Makeblock-Libraries Deployment Document

## Project Info
- **Repository:** https://github.com/Makeblock-official/Makeblock-Libraries
- **Description:** Arduino C++ library for Makeblock robot modules (motors, sensors, displays, etc.)
- **Language:** C++ (Arduino)


## Environment
- **Base Image:** ubuntu:24.04
- **Build System:** arduino-cli (cross-compilation)

## System Packages
```bash
apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    build-essential \
    ca-certificates
```

## Install
```bash
# Install arduino-cli
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
mv bin/arduino-cli /usr/local/bin/

# Initialize and install AVR core
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr

# Link library
mkdir -p /root/Arduino/libraries
ln -s /app/project /root/Arduino/libraries/Makeblock-Libraries
```

## Source Modifications
```bash
# Copy Wire.h to src/ for compilation compatibility
cp src/utility/Wire.h src/ 2>/dev/null || true
```

## Test
```bash
# No unit tests exist — verify by compiling example sketches:
arduino-cli compile --fqbn arduino:avr:uno examples/Me_UltrasonicSensor/UltrasonicSensorTest/UltrasonicSensorTest.ino
arduino-cli compile --fqbn arduino:avr:uno examples/Me_Servo/ServoTest/ServoTest.ino
arduino-cli compile --fqbn arduino:avr:uno examples/Me_LineFollower/LineFollowerTest/LineFollowerTest.ino
arduino-cli compile --fqbn arduino:avr:uno examples/Me_Temperature/MeTemperatureTest/MeTemperatureTest.ino
arduino-cli compile --fqbn arduino:avr:uno examples/Me_DCMotor/DCMotorDriverTest/DCMotorDriverTest.ino
```

## Unexpected Issues
- This project genuinely has **no automated tests** — it is a hardware-only Arduino library
- All 107 examples require physical Makeblock modules to run
- Verification is limited to successful compilation for `arduino:avr:uno` target
- Some examples may fail to compile due to missing Wire.h — the `cp src/utility/Wire.h src/` workaround is needed
