# npms-analyzer Deployment Document

## Platform

- Base image: `node:8-slim`
- Node.js: 8.x or 10.x (matching `engines: >=8.6`)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 bsdtar
```

## Build Steps

```bash
cd /app/npms-analyzer
npm install
```

## Test Steps

```bash
# Download test fixtures first
npm run download-test-fixtures

# Run tests with HTTP playback mode (uses pre-recorded fixtures)
VCR_MODE=playback npm run test-travis
```

Or manually:

```bash
VCR_MODE=playback npx mocha --timeout 60000 test/test.js
```

## Unexpected Issues

- **Node.js version is critical**: The `got@9.3.0` library uses internal Node.js stream APIs that changed in Node.js 18
   - Error: `RequestError: The first argument must be of type string or an instance of Buffer, ArrayBuffer, or Array`
   - This affects ALL tests that make HTTP requests (GitHub collection, NPM collection, source analysis, downloads)
- `test/mocha.opts` contains `--bail` which stops at the first failure - remove it to see all failures
- `VCR_MODE=playback` is essential - it uses pre-recorded HTTP fixtures instead of making real API calls
- `bsdtar` is needed for some archive extraction tests
