# ruboto-irb Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 11 (`openjdk-11-jdk` = 11.0.30+7-1ubuntu1~24.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-11-jdk=11.0.30+7-1ubuntu1~24.04 \
    ant=1.10.14-1 \
    wget=1.21.4-1ubuntu4 \
    unzip=6.0-28ubuntu4 \
    libstdc++6=14.2.0-4ubuntu2~24.04 \
    ca-certificates=20240203
```

### Install Android SDK

```bash
export ANDROID_SDK_ROOT=/opt/android-sdk
mkdir -p /opt/android-sdk/cmdline-tools
wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O /tmp/cmdline-tools.zip
unzip -q /tmp/cmdline-tools.zip -d /opt/android-sdk/cmdline-tools
mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest
yes | /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
/opt/android-sdk/cmdline-tools/latest/bin/sdkmanager "platforms;android-17" "build-tools;19.1.0" "platform-tools"
```

## Build Steps

### Build the APK

```bash
cd /app/project
android update project -n ruboto-irb --path . --subprojects --target 1
ant debug
```

## Test Steps

```bash
/opt/android-sdk/cmdline-tools/latest/bin/sdkmanager "system-images;android-17;default;x86"
echo "no" | avdmanager create avd -n test -k "system-images;android-17;default;x86" --force
emulator -avd test -no-window -no-audio -no-boot-anim &
adb wait-for-device

cd test
android update test-project -m .. -p .
ant debug install
adb shell am instrument -w org.jruby.ruboto.tests/org.ruboto.test.InstrumentationTestRunner
```

## Unexpected Issues

- Android instrumentation tests are fundamentally unrunnable in a headless Docker container without KVM support for the Android emulator.
- The project targets Android API 17 (Android 4.2, released 2012) — extremely old.
- The `android` CLI tool used for project setup is deprecated since 2016.
- This is a legitimate "no runnable tests" case for a Docker environment without KVM.
