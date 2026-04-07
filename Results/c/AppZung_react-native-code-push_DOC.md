# react-native-code-push Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Node.js: 20.x

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    python3=3.12.3-0ubuntu2 \
    ca-certificates=20240203 \
    curl=8.5.0-2ubuntu10.8 \
    gnupg=2.4.4-2ubuntu17

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs=20.*

# Enable Corepack for Yarn 4
corepack enable
```

## Build Steps

```bash
cd /app/react_native_code_push
yarn install
yarn prepare
```

## Test Steps

```bash
cd /app/react_native_code_push
yarn test
```

This runs `yarn test:lint && yarn test:format && yarn test:types`:
1. `eslint "**/*.{js,ts,tsx}"` -- lint check
2. `prettier --check "docs/**/*.md" README.md` -- format check
3. `tsc --noEmit` -- TypeScript type check

## Unexpected Issues

- The `test/test.ts` file contains integration tests requiring Android/iOS emulators and a CodePush server -- not runnable in Docker
- `yarn test` runs only static analysis (lint, format, types)
- Yarn 4 requires Corepack to be enabled
