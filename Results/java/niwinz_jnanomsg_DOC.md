# jnanomsg Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.18+8-1~24.04.1)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1 \
    leiningen=2.10.0-2 \
    libnanomsg5=1.1.5+dfsg-1.1 \
    libnanomsg-dev=1.1.5+dfsg-1.1 \
    build-essential=12.10ubuntu1 \
    ca-certificates=20240203
```

## Build Steps


### Set library paths

```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
export JNA_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
```



## Test Steps

### Step 1: Run Clojure tests

```bash
cd /app/project
lein test
```

Runs `nanomsg.core-tests` which tests request/reply, pipeline, pair, pub/sub, and bus socket patterns.

### Step 2: Run Java test (requires adding test path)

Add `"src/test"` to `:test-paths` in `project.clj`, then:

```bash
lein test
```

## Unexpected Issues

- JNA native library loading depends on `libnanomsg.so` being on `LD_LIBRARY_PATH` or `JNA_LIBRARY_PATH`.
- Clojure tests use real TCP/IPC/inproc sockets — timing-sensitive in CI.
- Java test at `src/test/` is not discovered by Leiningen's default test runner.
