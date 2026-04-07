# Tangram-base Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- PHP: 8.x (for test server)
- Node.js: 18+ (for Puppeteer)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 php-cli php-xml nodejs npm \
    libglib2.0-0 libnss3=2:3.98-1build1 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
    libgbm1 libasound2t64 libxcomposite1 libxdamage1 libxrandr2 \
    libpango-1.0-0 libcairo2 libcups2 libxshmfence1 libatspi2.0-0 libgtk-3-0
```

## Build Steps

```bash
cd /app/Tangram-base
npm init -y
npm install puppeteer
```

## Test Steps

Tests are QUnit tests run in browser, served by PHP via `test/tools/br/run.php`.

```bash
# Start PHP server
php -S 0.0.0.0:8080 -t . > /dev/null 2>&1 &
sleep 2

# Verify PHP serves test pages
curl -s http://localhost:8080/test/tools/br/run.php?case=baidu/dom/addClass | head -5
```

Create a Puppeteer script (`run_tests.js`) that:
1. Discovers test cases by scanning `test/baidu/` for `.js` files
2. Converts file paths to case names (e.g., `test/baidu/dom/addClass.js` -> `baidu/dom/addClass`)
3. For each case, navigates to `http://localhost:8080/test/tools/br/run.php?case=<name>`
4. Waits for QUnit `#qunit-testresult` element
5. Extracts pass/fail counts from the DOM

```bash
node run_tests.js
```

## Unexpected Issues

- No `package.json` in the repo - tests are entirely browser-based via PHP + QUnit
- The PHP `import.php` resolves `///import` directives in source files and concatenates JS dynamically
- The `runall.php` uses STAF (Software Testing Automation Framework) for remote browser execution - irrelevant for local testing
- ~200+ QUnit test files exist under `test/baidu/` - sequential execution is slow
- Structure is identical to Tangram-component - same PHP + QUnit + Puppeteer approach needed
