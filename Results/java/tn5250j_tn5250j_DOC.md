# tn5250j Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.13+11-2ubuntu1~24.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-17-jdk=17.0.13+11-2ubuntu1~24.04 \
    ant=1.10.14-1 \
    ant-optional=1.10.14-1 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Compile and run tests

```bash
cd /app/project
export JAVA_TOOL_OPTIONS="-Djava.awt.headless=true"
ant compile compile-tests run-tests
```

## Test Steps
```
ant compile compile-tests run-tests
```

## Unexpected Issues

- tn5250j is a GUI application — `JAVA_TOOL_OPTIONS="-Djava.awt.headless=true"` is needed since tests may touch AWT classes.
- Tests use bundled `junit-4.5.jar` from `lib/development/`, not the system `junit4` package.
- Test files are in a non-standard `tests/` directory.
