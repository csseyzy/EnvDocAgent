# pwa-kit Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Node.js: 24.x
- Build tool: npm + Lerna (monorepo)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 wget=1.21.4-1ubuntu4 python3-pip=24.0+dfsg-1ubuntu1.1 time
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt-get install -y nodejs
```


```bash
pip install --break-system-packages -U pip setuptools
pip install --break-system-packages awscli==1.18.85 datadog==0.40.1 || true
```

## Build Steps

```bash
cd /app/pwa_kit
npm ci
```

## Test Steps

```bash
npm test
```

`npm test` executes:
1. `npm run lint` (pretest)
2. `lerna run --stream --concurrency=1 test` (tests for all sub-packages)

Test framework: Jest

## Unexpected Issues

- Monorepo structure managed by Lerna with multiple sub-packages; `npm ci` installs dependencies for all sub-packages
- During testing, MSW (Mock Service Worker) may produce unhandled Commerce API request warnings and 403 errors — these do not affect test results
- `npm ci` requires significant time and memory
- The `python2` package may not be available on Ubuntu 24.04; use `python3-pip` instead
