# jaamsim Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 21 (`openjdk-21-jdk` = 21.0.10+7-1~24.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-21-jdk=21.0.10+7-1~24.04 \
    ant=1.10.14-1 \
    junit4=4.13.2-4 \
    libhamcrest-java=1.3-10 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Build main classes

```bash
cd /app/project
ant clean && ant
```

### Step 2: Compile tests manually

The `build.xml` only compiles `src/main` — tests must be compiled separately.

```bash
cd /app/project
mkdir -p build/test-classes
find src/test/java -name "*.java" > build/test-sources.txt
javac -cp build/classes:jar/*:/usr/share/java/junit4.jar:/usr/share/java/junit.jar:/usr/share/java/hamcrest.jar:/usr/share/java/hamcrest-core.jar \
    -d build/test-classes @build/test-sources.txt
```

## Test Steps


```bash
java -Djava.awt.headless=true \
    -cp build/test-classes:build/classes:jar/*:/usr/share/java/junit4.jar:/usr/share/java/junit.jar:/usr/share/java/hamcrest.jar:/usr/share/java/hamcrest-core.jar \
    org.junit.runner.JUnitCore com.jaamsim.AllTests
```

## Unexpected Issues

- The `build.xml` only has `clean`, `compile`, `jar`, and `exe` targets — no test target.
- Some tests (e.g., `TestSimulation`, `TestEntityDefinitions`) require headless mode (`-Djava.awt.headless=true`) because they reference GUI components.
- JUnit 4 and Hamcrest must be installed via apt since they are not bundled.
