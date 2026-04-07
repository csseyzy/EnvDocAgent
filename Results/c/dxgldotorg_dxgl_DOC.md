# dxgl Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    build-essential=12.10ubuntu1 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
git checkout 0.5.x
```

## Test Steps

```bash
cd /app/project/cfgmgr/inih/tests
chmod +x ./unittest.sh
./unittest.sh
```

See verification commands in Build Steps.

## Unexpected Issues

- The main DXGL project cannot be built on Linux — it requires Microsoft Visual Studio (2022 Update 8 for standard build, 2010 SP1 for legacy).
- Only the vendored `cfgmgr/inih` subcomponent has a Linux-compatible test suite.
- The master branch is explicitly non-functional; must use `0.5.x` branch.
