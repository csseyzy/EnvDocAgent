# NER Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 8 (`openjdk-8-jdk` = 8u402-ga-8build1)
- **JAVA_HOME:** `/usr/lib/jvm/java-8-openjdk-amd64`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-8-jdk=8u402-ga-8build1 \
    ant=1.10.14-1 \
    ant-optional=1.10.14-1 \
    perl=5.38.2-3.2build2 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Set JDK 8 as active JDK

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
update-alternatives --set javac /usr/lib/jvm/java-8-openjdk-amd64/bin/javac
```

### Step 2: Initialize project directories

```bash
cd /app/project
ant -f nerbuild.xml init
```

Creates `build/`, `dist/`, `etc/`, and `reports/` directories and copies template files from `templates/` to `etc/`.

### Step 3: Compile

```bash
ant -f nerbuild.xml clean compile
```

## Test Steps

```bash
ant -f nerbuild.xml test
```

## Unexpected Issues

- Project REQUIRES Java 8 (JDK 1.8). Compilation fails with Java 11+ due to internal API access restrictions (module system blocks `sun.*` packages).
- Only 1 test class (`CoresetsTest`) is auto-discovered by the `**/*Test.class` pattern. Other test classes (`AutoTests`, `ManualTests`, etc.) do not match the pattern.
- The `testauto` Ant target runs `test.AutoTests` separately but is not part of the standard `test` target.
- Some functionality requires a MySQL database with Wikipedia data (not needed for basic tests).
- All library dependencies are vendored in `lib/` directory.
