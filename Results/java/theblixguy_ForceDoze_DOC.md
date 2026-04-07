# ForceDoze Deployment Document

## Platform

- **Base Image:** `ubuntu:22.04`
- **JDK:** Temurin JDK 8 (for Gradle builds) + JDK 17 (for `sdkmanager` only)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.34.1-1ubuntu1 \
    wget=1.21.2-2ubuntu1 \
    curl=7.81.0-1ubuntu1 \
    unzip=6.0-26ubuntu3 \
    zip=3.0-12build2 \
    openjdk-17-jre-headless=17.0.13+11-2ubuntu1~22.04 \
    ca-certificates=20230311ubuntu0.22.04.1
```

## Build Steps

### Install Temurin JDK 8

```bash
mkdir -p /opt/jdk8
wget -O /tmp/jdk8.tar.gz https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u402-b06/OpenJDK8U-jdk_x64_linux_hotspot_8u402b06.tar.gz
tar -xzf /tmp/jdk8.tar.gz -C /opt/jdk8 --strip-components=1
```

### Install Android SDK

```bash
export ANDROID_SDK_ROOT=/opt/android-sdk
mkdir -p $ANDROID_SDK_ROOT/cmdline-tools
wget -O /tmp/cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip /tmp/cmdline-tools.zip -d $ANDROID_SDK_ROOT/cmdline-tools
mv $ANDROID_SDK_ROOT/cmdline-tools/cmdline-tools $ANDROID_SDK_ROOT/cmdline-tools/latest

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$PATH
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-27" "build-tools;27.0.3"
```


### 1. Exclude XposedModule.java from compilation

Add to `app/build.gradle` inside the `android {}` block:

```groovy
sourceSets {
    main {
        java {
            exclude '**/XposedModule.java'
        }
    }
}
```

### 2. Create stub for libsuperuser

The `libsuperuser` library uses dynamic versioning (`1.0.0.+`) which may fail to resolve. Add a local stub or pin the version in `app/build.gradle`:

```groovy
implementation 'eu.chainfire:libsuperuser:1.0.0.201704021214'
```

### 3. Update dependencies in app/build.gradle

Replace the Xposed dependency (unavailable from standard repos) with a local jar or exclude it:

```groovy
compileOnly files('libs/XposedBridgeApi.jar')
```

Download the Xposed API jar from the Xposed repository and place it in `app/libs/`.

## Test Steps

```bash
export JAVA_HOME=/opt/jdk8
export PATH=$JAVA_HOME/bin:$PATH
cd /app/project
./gradlew --no-daemon test
```

Test framework: JUnit 4 (default Android `ExampleUnitTest` template).

## Unexpected Issues

- Only has a default `ExampleUnitTest` (template test) — minimal test coverage.
- Xposed API is a `compileOnly` dependency not available from standard Maven repos.
- `libsuperuser` uses dynamic versioning (`1.0.0.+`) which may not resolve.
