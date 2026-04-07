# bach Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: **JDK 25 Early Access** (Eclipse Temurin). The project targets `--release 25` and will NOT compile on JDK 21 or 22.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 tar
```


```bash
mkdir -p /opt/jdk-25
curl -L -o /tmp/jdk.tar.gz \
    https://api.adoptium.net/v3/binary/latest/25/ea/linux/x64/jdk/hotspot/normal/eclipse
tar -xzf /tmp/jdk.tar.gz -C /opt/jdk-25 --strip-components=1
rm -f /tmp/jdk.tar.gz

export JAVA_HOME=/opt/jdk-25
export PATH="$JAVA_HOME/bin:$PATH"
```


## Build Steps

```bash
git clone --depth 1 --recurse-submodules https://github.com/sormuras/bach project
cd project
git submodule update --init --recursive || true
```


```bash
cd /app/project
java @build
```


## Test Steps

The project uses its own self-hosted build system. Tests are run via the same `java @build` mechanism:

```bash
cd /app/project
java @build test
```

If the `test` argument is not supported, the `java @build` command already compiles and validates the modules. Alternatively, run JUnit tests directly:

```bash
cd /app/project
java --module-path .bach/out/modules -m org.junit.platform.console --scan-modules --disable-ansi-colors
```

## Unexpected Issues

- **Requires JDK 25 EA specifically.** The project targets `--release 25`. JDK 21 or 22 will fail.
- **No traditional build tool.** No `pom.xml`, `build.gradle`, or `Makefile`. The `build` file in repo root is a text argfile read by `java @build`.
- **Self-hosted build system.** Bach builds itself using its own SourceLauncher mechanism.
- **Submodules.** Must use `--recurse-submodules` when cloning or run `git submodule update --init --recursive`.
- **No source code modifications needed.**
