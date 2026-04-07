# dddplus-demo Deployment Document

## Platform

- **Base Image:** `maven:3.9.9-eclipse-temurin-8-focal`
- **JDK:** JDK 8 (required — project uses `javax.annotation.Resource`, Lombok 1.18.8, source/target 1.8)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.25.1-1ubuntu3
```

The base image `maven:3.9.9-eclipse-temurin-8-focal` already includes Maven 3.9.9 and JDK 8.

## Build Steps

### Step 1: Build

```bash
cd /app/project
mvn -B clean install -DskipTests
```

## Test Steps

```bash
cd /app/project
mvn -B test
```

Test framework: JUnit 4 + Spring Test. Most tests are `@Ignore`d or require Spring context with `spring-test.xml`.

## Unexpected Issues

- Lombok 1.18.8 is incompatible with JDK 11+ — must use JDK 8.
- `javax.annotation.Resource` is not available in JDK 11+ without adding `javax.annotation-api` dependency.
- Most tests are `@Ignore`d or require Spring context with `spring-test.xml`. The test suite may report 0 tests run.
- The `dddplus-plugin:0.1.0` dependency resolves from Maven Central.
