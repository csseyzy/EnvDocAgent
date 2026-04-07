# eclairjs-node Deployment Document

## Platform

- Base image: `node:6-slim`
- Node.js: 6.x (critical - must match the project era)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
```

## Build Steps

```bash
cd /app/eclairjs-node
npm install
```

## Test Steps

```bash
npm test
```

Test framework: Mocha (`mocha --harmony test/*.js`)

## Unexpected Issues

- **Node.js version is critical**: All 11 test failures are caused by `Function.prototype.toString()` format changes between Node.js versions
   - Node.js 6.x: `function (arg)` (with space after `function`) - matches test expectations
   - Node.js 10+: `function(arg)` (no space) - breaks strict string comparisons
- If you must use a modern Node.js, patch `lib/utils.js` around line 363 to normalize function serialization:
   ```javascript
   var funcStr = func.toString().replace(/^function\(/, 'function (');
   ```
- The project's `engines` field says `node >= 0.12` - it was designed for the Node.js 0.12-6.x era
