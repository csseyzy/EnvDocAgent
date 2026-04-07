# engine (Open Integration Engine) Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.13+11-2ubuntu1~24.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-17-jdk=17.0.13+11-2ubuntu1~24.04 \
    openjfx=17.0.11+3-1 \
    ant=1.10.14-1 \
    ant-optional=1.10.14-1 \
    unzip=6.0-28ubuntu4 \
    zip=3.0-13build1 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Build

```bash
cd /app/project/server
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF-8"
ant -f mirth-build.xml -DdisableSigning=true build
```



## Test Steps


```bash
cd /app/project/server
ant -f mirth-build.xml -DdisableSigning=true -Dcoverage=true test-run
```

## Unexpected Issues

- Complex multi-module build with interdependencies (donkey -> server -> client -> command).
- The build requires `disableSigning=true` to skip JAR signing.
- Some tests may require database setup (Derby embedded DB).
- Encoding issues require `LC_ALL=C.UTF-8` and `JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF-8`.
