# secs4java8 Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: OpenJDK 17 (`openjdk-17-jdk`). Target bytecode is Java 8 (`--release 8` in compile.sh).
- Zero external dependencies.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 unzip=6.0-28ubuntu4 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1
```


## Build Steps

```bash
export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF-8"

cd /app/project
chmod +x compile.sh
./compile.sh
```


## Test Steps

```bash
cd /app/project
mkdir -p out_examples
javac -d out_examples --release 8 -encoding UTF-8 -cp bin \
    src/examples/example3/ExampleBuildSecs2.java
java -cp out_examples:bin example3.ExampleBuildSecs2
```


## Unexpected Issues

- **UTF-8 encoding required.** Must set `JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF-8"` before running `compile.sh`, otherwise `javac` may fail on source files with non-ASCII characters.
- **No dependency management file.** No `pom.xml`, `build.gradle`, `build.xml`, `.project`, or `.classpath`.
- **No source code modifications needed.**
