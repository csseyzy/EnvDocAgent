# meteor-promise Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Meteor: 1.6.1 (minimum supported version where spacejam + PhantomJS still works)

## Prerequisites

```bash
apt-get update && apt-get install -y curl=8.5.0-2ubuntu10.8 bzip2=1.0.8-5.1build0.1 git=1:2.43.0-1ubuntu7 python3=3.12.3-0ubuntu2 build-essential=12.10ubuntu1
```

## Build Steps

```bash
curl https://install.meteor.com/ | sh
export PATH="/root/.meteor:$PATH"
export METEOR_ALLOW_SUPERUSER=1
```

```bash
cd /app/meteor-promise
meteor npm install
```

## Test Steps

### Option A: Using spacejam (original method)

```bash
npm test
```

This runs `spacejam test-packages ./` which uses PhantomJS for headless browser testing.

### Option B: Modern approach (if spacejam fails)

```bash
meteor npm install --save-dev puppeteer
TEST_BROWSER_DRIVER=puppeteer meteor test-packages ./ --once --driver-package meteortesting:mocha
```

Note: Tests use TinyTest API (`Tinytest.add`), not Mocha. The `test-in-console` driver may be more appropriate:

```bash
meteor test-packages ./ --once --driver-package test-in-console
```

## Unexpected Issues

- This is a **Meteor package** (not a Meteor app) - can only be tested via `meteor test-packages`
- `spacejam` is deprecated and broken on modern Meteor (v2.3+); PhantomJS is abandoned
- Tests are client-only TinyTest tests that need a browser to execute
- If using `meteortesting:mocha`, TinyTest tests would need rewriting to Mocha syntax
- The most reliable approach: use Meteor 1.6.1 where spacejam + PhantomJS still works
- `package.js` declares `api.versionsFrom(['1.6.1', '2.3', '3.0-beta.0'])`
