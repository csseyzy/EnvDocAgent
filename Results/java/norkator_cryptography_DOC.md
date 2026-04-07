# cryptography Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 11 (`openjdk-11-jdk` = 11.0.25+9-1ubuntu1~24.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-11-jdk=11.0.25+9-1ubuntu1~24.04 \
    ant=1.10.14-1 \
    ant-optional=1.10.14-1 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Fix Eclipse classpath in build.xml


Change the `JUnit 4.libraryclasspath` path to:
```xml
<path id="JUnit 4.libraryclasspath">
    <pathelement location="jar/org.junit_4.13.0.v20200204-1500.jar"/>
    <pathelement location="jar/core-1.3.0.jar"/>
</path>
```

### Step 2: Build

```bash
cd /app/project
ant build
```

## Test Steps


```bash
ant Cryptography
```

Or run the test suite:

```bash
ant JunitTestSuite
```

Or run the default target which includes tests + HTML report:

```bash
ant junitreport
```

## Unexpected Issues

- Eclipse-generated `build.xml` has hardcoded Eclipse `.p2` plugin paths that don't exist outside Eclipse.
- The `Cryptography` target lists test classes individually (not a batchtest), so new tests must be manually added.
- Some crypto tests may need `crypto.policy=unlimited` — the code uses `Security.setProperty("crypto.policy", "unlimited")` to work around this.
