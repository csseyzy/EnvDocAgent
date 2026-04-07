# EntityCulling Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: OpenJDK 21 (`openjdk-21-jdk`)
- The project uses `gradlecw` (not standard `gradlew`). This is a custom wrapper that runs `gradle-compose.jar` to generate Gradle build files from `gradle-compose.yml` + `settings.json`, then invokes Gradle.
- No `build.gradle` or `settings.gradle` in repo root; they are generated at build time.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    openjdk-21-jdk=21.0.10+7-1~24.04
```


## Build Steps

```bash
cd /app/project
chmod +x ./gradlecw
./gradlecw build --stacktrace
```

Builds 33 version variants across Fabric/Forge/NeoForge (defined in `settings.json`).


## Test Steps

This project has no test source files. The `src/test/` directories are empty across all submodules. Running `./gradlecw test` completes with 0 tests executed.

```bash
cd /app/project
./gradlecw test 2>&1 | tee TEST_RESULTS.txt
```

Verification is limited to a successful build (`./gradlecw build`).

## Unexpected Issues

- **Custom wrapper:** Project uses `gradlecw` (not `gradlew`). Must `chmod +x ./gradlecw` before use.
- **No build files in repo root:** `build.gradle` and `settings.gradle` are generated at build time by gradle-compose/Stonecutter.
- **Long first build:** Downloads Minecraft mappings, mod loaders, and all dependencies.
- **No source code modifications needed.**
