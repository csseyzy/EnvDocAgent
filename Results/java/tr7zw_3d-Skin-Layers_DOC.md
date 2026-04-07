# 3d-Skin-Layers Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 21 (`openjdk-21-jdk` = 21.0.10+7-1~24.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-21-jdk=21.0.10+7-1~24.04 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
./gradlecw build --stacktrace
```

## Test Steps

```bash
find . -path '*/build/test-results/test/*.xml' -type f
```

## Unexpected Issues

- The Gradle wrapper is named `gradlecw` (not `gradlew`), which is non-standard.
- Only Fabric modules produce test results; Forge/NeoForge modules may not include tests.
- Publishing tasks (e.g., `publishMods`) require Modrinth/CurseForge credentials and should be skipped.
