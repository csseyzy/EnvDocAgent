# ldapsdk Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.13+11-2ubuntu1~24.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-17-jdk=17.0.13+11-2ubuntu1~24.04 \
    ant=1.10.14-1 \
    zip=3.0-13build1 \
    unzip=6.0-28ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
ant -Dcheckstyle.enabled=false -Dcoverage.enabled=false build
```

## Test Steps

```bash
cd /app/project
ant -Dcheckstyle.enabled=false -Dcoverage.enabled=false test
```

Test framework: TestNG (bundled `testng-5.8-jdk15.jar`). The full suite contains 1,228 tests.

## Unexpected Issues

- Checkstyle (bundled version 6.19) is incompatible with Java 9+ — must disable with `-Dcheckstyle.enabled=false`.
- JaCoCo coverage can cause issues — disable with `-Dcoverage.enabled=false`.
- The full test suite (1,228 tests) takes a very long time to run.
- Tests use TestNG (not JUnit) — the bundled version is `testng-5.8-jdk15.jar`.
