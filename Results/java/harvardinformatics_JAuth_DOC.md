# JAuth Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 21 (`default-jdk` = 2:1.21-0ubuntu2, resolves to openjdk-21)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    default-jdk=2:1.21-0ubuntu2 \
    dos2unix=7.5.1-1 \
    junit4=4.13.2-4 \
    libhamcrest-java=1.3-10 \
    xvfb=2:21.1.12-1ubuntu1 \
    ca-certificates=20240203
```

## Build Steps

### Build the jar

```bash
cd /app/project
chmod +x ./makejar ./setpath
./makejar
```

## Test Steps


```bash
cd /app/project
. ./setpath
export CLASSPATH="$CLASSPATH:/usr/share/java/junit4.jar:/usr/share/java/junit.jar:/usr/share/java/hamcrest-core.jar"
javac -cp "$CLASSPATH" JAuth/AuthenticatorGUITests.java
xvfb-run -a java -cp "$CLASSPATH" org.junit.runner.JUnitCore JAuth.AuthenticatorGUITests
```

## Unexpected Issues

- Tests are GUI-heavy — they create `AuthenticatorGUI` instances with `Image` and `Font` objects. Requires `xvfb-run` for headless execution.
- The `makejar` script only compiles `AuthenticatorGUI.java`, not the test file.
- JUnit 4 is not in the project's classpath (`setpath` only includes forms-1.1.0.jar and i4jruntime.jar).
- The test `editPasswordCheck` opens a visible frame and may hang without headless mode.
