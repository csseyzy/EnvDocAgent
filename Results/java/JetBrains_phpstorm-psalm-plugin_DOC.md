# phpstorm-psalm-plugin Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.18+8-1~24.04.1)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1 \
    curl=8.5.0-2ubuntu10 \
    unzip=6.0-28ubuntu4 \
    zip=3.0-13build1 \
    ca-certificates=20240203 \
    libxext6=2:1.3.4-1build2 \
    libxrender1=1:0.9.10-1.1build1 \
    libxtst6=2:1.2.3-1.1build1 \
    libxi6=2:1.8.1-1build1 \
    libnss3=2:3.98-1build1 \
    fontconfig=2.15.0-1.1ubuntu2
```

### Install Bazelisk

```bash
curl -L https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 -o /usr/local/bin/bazelisk
chmod +x /usr/local/bin/bazelisk
ln -sf /usr/local/bin/bazelisk /usr/local/bin/bazel
```

## Build Steps


### Theoretical steps (will fail without proprietary PhpStorm modules):

```bash
git clone --depth 1 https://github.com/JetBrains/intellij-community /app/intellij-community
mkdir -p /app/intellij-community/phpstorm/psalm
cp -a /app/project/* /app/intellij-community/phpstorm/psalm/
cd /app/intellij-community
```


## Test Steps
```
bazel test //phpstorm/psalm:psalm_test
```

## Unexpected Issues

- Monorepo sub-module — cannot build or test standalone.
- Requires proprietary PhpStorm SDK modules not available publicly.
- No CI workflow files found in the repo — tests are run via JetBrains internal CI.
- This is arguably a legitimate "untestable in Docker" case.
