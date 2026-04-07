# ItemSwapper Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: OpenJDK 21 (`openjdk-21-jdk`)
- The project uses `gradlecw` (not standard `gradlew`). This is a custom wrapper that first runs `gradle-compose.jar` to generate `settings.gradle`, `build.gradle`, `gradle.properties`, and Gradle wrapper files from `gradle-compose.yml` + `settings.json`, then invokes the standard Gradle wrapper.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    openjdk-21-jdk=21.0.10+7-1~24.04 curl=8.5.0-2ubuntu10.8 wget=1.21.4-1ubuntu4 unzip=6.0-28ubuntu4
```


## Build Steps

```bash
cd /app/project
chmod +x ./gradlecw
./gradlecw build --stacktrace
```


## Test Steps


```bash
cd /app/project
./gradlecw test 2>&1 | tee TEST_RESULTS.txt
```


## Unexpected Issues

- **Custom wrapper:** Project uses `gradlecw` (not `gradlew`). Must `chmod +x ./gradlecw` before use.
- **PMD violations:** 52 rule violations reported (non-fatal, build still succeeds).
- **Gradle deprecation warnings:** Some plugins use APIs incompatible with Gradle 10.
- **Remapping warnings:** Multiple "Cannot remap..." warnings during Fabric remapping (non-fatal).
- **Long first build:** First run downloads Gradle distribution + all Minecraft dependencies.
- **No source code modifications needed.**
