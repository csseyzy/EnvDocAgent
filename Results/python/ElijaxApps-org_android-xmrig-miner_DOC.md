# android-xmrig-miner Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** N/A (this is a Java/Android/C project)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    curl=8.5.0-2ubuntu10.6 \
    unzip=6.0-28ubuntu4.1 \
    zip=3.0-13build1 \
    wget=1.21.4-1ubuntu4.1 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203 \
    openjdk-17-jdk=17.0.13+11-2ubuntu1 \
    build-essential=12.10ubuntu1 \
    cmake=3.28.3-1build7
```

## Build Steps

```bash
# Install Android SDK
export ANDROID_SDK_ROOT="/opt/android-sdk"
mkdir -p "$ANDROID_SDK_ROOT/cmdline-tools"
wget -O /tmp/cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q /tmp/cmdline-tools.zip -d "$ANDROID_SDK_ROOT/cmdline-tools"
mv "$ANDROID_SDK_ROOT/cmdline-tools/cmdline-tools" "$ANDROID_SDK_ROOT/cmdline-tools/latest"
yes | "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" --licenses
"$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" "platform-tools" "platforms;android-26" "build-tools;28.0.3" "cmake;3.10.2.4988404" "ndk;21.4.7075529"

cd /app/project
chmod +x ./gradlew
./gradlew assembleDebug
```

## Test Steps

```bash
# Option 1: Run Gradle test (will find 0 project tests)
cd /app/project
./gradlew test 2>&1 | tee /app/project/TEST_RESULTS.txt

# Option 2: Build and run vendored libuv C tests
cd /app/project/libuv/libuv-1.23.1
mkdir -p build && cd build
cmake .. && make
./uv_run_tests 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This is fundamentally an Android/Java/C project miscategorized as Python
- The `app/src/test/` directory is empty — no Java test sources exist
- The libuv C tests are for the vendored networking library, not the Android app itself
- The Gradle build requires Android SDK, NDK, and CMake
- Espresso instrumentation tests require an Android emulator
