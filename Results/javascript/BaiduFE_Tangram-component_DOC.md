# Tangram-component Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- PHP: 8.x (for test server)
- Node.js: 18+ (for Puppeteer)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 php-cli nodejs npm \
    libglib2.0-0 libnss3=2:3.98-1build1 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
    libgbm1 libasound2t64 libxcomposite1 libxdamage1 libxrandr2 \
    libpango-1.0-0 libcairo2 libcups2 libxshmfence1 libatspi2.0-0 libgtk-3-0
```

## Build Steps

```bash
cd /app/Tangram-component
npm init -y
npm install puppeteer
```

## Test Steps

Tests are QUnit tests that run in a browser, served by PHP via `test/tools/br/run.php`.

```bash
# Start PHP server
php -S localhost:8080 -t . > /dev/null 2>&1 &
sleep 2

# Get test case list
curl -s http://localhost:8080/test/tools/br/list.php | grep -oP 'case=[^"&]+' | cut -d= -f2 > test_cases.txt
```

Create a Puppeteer script (`run_tests.js`) that:
1. Launches headless Chrome with `--no-sandbox`
2. For each test case, navigates to `http://localhost:8080/test/tools/br/run.php?case=<name>`
3. Waits for QUnit `#qunit-testresult` element
4. Extracts pass/fail counts from the DOM

```bash
node run_tests.js
```

## Unexpected Issues

- No `package.json` in the repo - tests are entirely browser-based via PHP + QUnit
- The `config.php` references Windows paths for STAF-based remote browser execution (Baidu internal infra) - irrelevant for local testing
- ~132 test cases running sequentially through Puppeteer is slow (~30-60s each) - use parallel browser tabs or reduce timeout to stay under 2 hours
- Chrome system dependencies (libglib, libnss, etc.) must all be installed for Puppeteer to work
