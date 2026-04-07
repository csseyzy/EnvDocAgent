# rules_jvm_external Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: OpenJDK 17 (`openjdk-17-jdk`)
- Android SDK required for Android-related test targets.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 unzip=6.0-28ubuntu4 zip=3.0-13build1 python3=3.12.3-0ubuntu2 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1 libc6 libstdc++6 build-essential=12.10ubuntu1
```


```bash
curl -fsSL https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 \
    -o /usr/local/bin/bazel && chmod +x /usr/local/bin/bazel
```


```bash
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk

mkdir -p ${ANDROID_HOME}/cmdline-tools
curl -fsSL -o /tmp/cmdtools.zip \
    https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q /tmp/cmdtools.zip -d ${ANDROID_HOME}/cmdline-tools
mv ${ANDROID_HOME}/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest

export PATH="${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/cmdline-tools/latest/bin:${PATH}"

yes | sdkmanager --sdk_root=$ANDROID_HOME \
    "platform-tools" "build-tools;33.0.1" "build-tools;35.0.0" \
    "platforms;android-33" "platforms;android-35" \
    "ndk;21.4.7075529" "cmdline-tools;latest"
yes | sdkmanager --licenses --sdk_root=$ANDROID_HOME

export ANDROID_NDK_HOME=/opt/android-sdk/ndk/21.4.7075529
```


## Build Steps

```bash
cd /app/project
bazel build //...
```

Bazel automatically fetches all Maven dependencies declared in `MODULE.bazel` / `WORKSPACE` during the first build. This may take several minutes due to the large number of artifacts.

## Test Steps

```bash
cd /app/project
bazel test //tests/... --test_output=errors
```


## Unexpected Issues

- **Android SDK version mismatch.** The project requires `build-tools;35.0.0` and `platforms;android-35` in addition to the older versions. Must install both.
- **Missing C/C++ toolchain.** Bazel's `cc_configure` fails without `gcc`. Must install `build-essential`.
- **`PublishShapeTest` timeout.** The single failing test times out during `Process.waitFor()`. Not a real logic failure; can potentially be fixed with `--test_timeout=900`.
- **Maven 404 warnings.** Many artifact downloads from `maven.google.com` and `packages.confluent.io` return 404. Non-fatal; Bazel falls back to other repositories.
- **No source code modifications needed.**
