# totallylazy Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 8 (`openjdk-8-jdk` = 8u402-ga-8build1) — project requires Java 8, incompatible with Java 9+

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-8-jdk=8u402-ga-8build1 \
    curl=8.5.0-2ubuntu10 \
    wget=1.21.4-1ubuntu4 \
    unzip=6.0-28ubuntu4 \
    ca-certificates=20240203
```

## Build Steps
```bash
cd /app/project
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
./jcompilo.sh
```


## Test Steps


```bash
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 ./jcompilo.sh test
```

test files under `test/com/googlecode/totallylazy/`.

## Unexpected Issues

- Must use Java 8 — the project is incompatible with Java 9+ due to module system restrictions.
- JCompilo downloads itself from GitHub at build time (`https://github.com/bodar/jcompilo/releases/download/2.52/jcompilo-2.52.jar`) — URL may be unavailable.
- Tests live in `test/` directory (not `src/test/java/`) which is a non-standard layout.
