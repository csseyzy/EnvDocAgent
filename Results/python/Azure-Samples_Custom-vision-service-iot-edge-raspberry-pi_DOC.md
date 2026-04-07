# Custom-vision-service-iot-edge-raspberry-pi Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** 3.12

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    python3=3.12.3-0ubuntu2 \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
    python3-venv=3.12.3-0ubuntu2 \
    python3-dev=3.12.3-0ubuntu2 \
    build-essential=12.10ubuntu1 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
python3 -m pip install --no-cache-dir --upgrade pip
```

## Test Steps

```bash
cd /app/project/modules/CameraCapture/test
python3 -m unittest UnitTests -v 2>&1 | tee /app/project/TEST_RESULTS_camera.txt

cd /app/project/modules/SenseHatDisplay/test
python3 -m unittest UnitTests -v 2>&1 | tee /app/project/TEST_RESULTS_sensehat.txt

cat /app/project/TEST_RESULTS_camera.txt /app/project/TEST_RESULTS_sensehat.txt > /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- Only 2 of the 4 test files are runnable (unit tests); the integration tests require physical hardware (USB camera, SenseHat display)
- Test files use non-standard naming (`UnitTests.py`, `IntegrationTests.py`) instead of `test_*.py`
- The `sys.path.insert(0, '../')` in the test files handles the import path
- The CameraCapture integration test also requires OpenCV and a video file
