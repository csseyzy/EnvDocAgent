# allocation-instrumenter Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: OpenJDK 17 (`openjdk-17-jdk`)
- Bazel must run as non-root user (hermetic Python rules disallow root).

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 unzip=6.0-28ubuntu4 zip=3.0-13build1 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1 build-essential=12.10ubuntu1 sudo
```


```bash
curl -L -o /usr/local/bin/bazel \
    https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64
chmod +x /usr/local/bin/bazel
```


## Build Steps

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:/usr/local/bin:$PATH
```

Create non-root user (Bazel refuses to run hermetic Python as root):

```bash
useradd -m -s /bin/bash builder
chown -R builder:builder /app/project
```

## Test Steps

```bash
sudo -u builder -H env \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    HOME=/home/builder \
    PATH=/usr/lib/jvm/java-17-openjdk-amd64/bin:/usr/local/bin:/usr/bin \
    bazel --nosystem_rc --nohome_rc --output_user_root=/home/builder/.cache/bazel \
    test //... --test_output=all
```


## Unexpected Issues

- **Must run Bazel as non-root user.** Bazel's hermetic Python rules (`rules_python`) disallow running as root. Must create a `builder` user.
- **Stale Bazel symlinks.** If Bazel was previously run as root, symlinks (`bazel-bin`, `bazel-out`, etc.) point to `/root/.cache` and cause permission errors. Fix: `rm -f bazel-bin bazel-out bazel-testlogs bazel-project`.
- **Bazel mirror 404s.** Multiple artifacts return 404 from `bazel-mirror.storage.googleapis.com`. Bazel falls back to Maven Central automatically; no action needed.
- **No source code modifications needed.**
