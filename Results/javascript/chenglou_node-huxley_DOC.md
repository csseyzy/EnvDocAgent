# node-huxley Deployment Document

## Platform

- Base image: `node:6-stretch`
- Node.js: 6.x (project uses old APIs and old dependencies)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
```

## Build Steps

```bash
cd /app/node-huxley
npm install
```

## Test Steps

### Unit tests only (no Selenium needed, recommended)

```bash
node_modules/.bin/mocha source/__tests__/getDefaultOpts-test.js source/__tests__/runTasks-test.js --reporter spec
```

### Full test suite (requires Selenium + browser)

The `npm test` script runs: `chromedriver & ./node_modules/.bin/selenium & mocha 'source/**/*-test.js'`

This requires:
- Java JRE (for Selenium standalone)
- ChromeDriver + Chrome (or Firefox)
- Xvfb for headless display

```bash
apt-get install -y default-jre chromium chromium-driver xvfb=2:21.1.12-1ubuntu1
Xvfb :99 &
export DISPLAY=:99
npm test
```

## Unexpected Issues

- `selenium-webdriver` ^2.43.5 is ancient and incompatible with modern Chrome/ChromeDriver
- `npm install` fails on modern Node.js due to native module compilation issues - use Node.js 6.x
- Only 1 of 3 test files (`getDefaultOpts-test.js`) is a pure unit test; `runRunnableTasks-test.js` requires a live Selenium+browser stack
- Updating `selenium-webdriver` to v4.x would require significant test refactoring
- Use `node:6-stretch` base image for best compatibility
