# vscode-anycode Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Node.js: 20.x LTS

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 curl=8.5.0-2ubuntu10.8 build-essential=12.10ubuntu1 python3=3.12.3-0ubuntu2
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
```

## Build Steps

```bash
cd /app/vscode-anycode
node ./scripts/all-npm.js i
npx playwright install --with-deps chromium
```

## Test Steps

### Unit tests (always work)

```bash
cd anycode/server && npm test
```

### Browser tests (need Playwright system deps + timeout fix)

The test fixture at `anycode/server/src/common/test-fixture/test.js` has a 15-second timeout that is too short for Docker environments. Increase it:

```bash
sed -i 's/setTimeout(() => reject.*TIMEOUT.*15000/setTimeout(() => reject("TIMEOUT"), 60000/' \
  anycode/server/src/common/test-fixture/test.js
```

Then run each language extension test:

```bash
for dir in anycode-typescript anycode-python anycode-java anycode-cpp anycode-go anycode-rust anycode-php anycode-kotlin anycode-c-sharp; do
  cd /app/vscode-anycode/$dir && npm test
done
```

## Unexpected Issues

- Playwright system dependencies MUST be installed (`npx playwright install --with-deps chromium`) before running browser tests
- The default 15-second timeout in `test-fixture/test.js` is too short for Docker/CI - increase to 60 seconds
- WASM loading + tree-sitter initialization is slow in containers, contributing to timeouts
