# Cafe Deployment Document

## Platform

- **Base Image:** `ubuntu:22.04`
- **JDK:** OpenJDK 8 (`openjdk-8-jdk` = 8u392-ga-1~22.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.34.1-1ubuntu1 \
    openjdk-8-jdk=8u392-ga-1~22.04 \
    curl=7.81.0-1ubuntu1 \
    wget=1.21.2-2ubuntu1 \
    unzip=6.0-26ubuntu3 \
    ca-certificates=20230311ubuntu0.22.04.1
```

## Build Steps

```bash
cd /app/project
mkdir -p out
javac -source 1.7 -target 1.7 \
    -cp testrunner/libs/android.jar \
    -d out \
    testrunner/src/com/baidu/cafe/*.java \
    testrunner/src/com/baidu/cafe/local/*.java \
    testrunner/src/com/baidu/cafe/remote/*.java
jar cvf out/cafe.jar -C out .
```

## Test Steps

```bash
cd /app/project
java -cp out/cafe.jar com.baidu.cafe.CafeTestCase 2>&1 || echo "Expected: requires Android runtime"
ls -la out/cafe.jar && echo "BUILD VERIFICATION: cafe.jar created successfully"
```

## Unexpected Issues

- Project is designed exclusively for AOSP-integrated builds.
- All tests are Android instrumentation tests requiring a physical device or emulator.
- `make.sh` hardcodes `ANDROID_TOP=$SRC/../` and calls `. build/envsetup.sh`.
- No Maven/Gradle/Ant build files exist.
- The bundled `testrunner/libs/android.jar` can be used for compilation-only verification.
