# ScatterWebExtension Deployment Document

## Platform

- Base image: `node:10-buster`
- Node.js: 10.x (for compatibility with webpack 3, babel 6, node-sass 4.9)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 python2.7 build-essential=12.10ubuntu1
ln -sf /usr/bin/python2.7 /usr/bin/python
```

## Build Steps


Patch `tests/setup.js` to add the missing Web Crypto API polyfill:

```javascript
const nodeCrypto = require('crypto');
global.crypto = { getRandomValues: (buf) => nodeCrypto.randomFillSync(buf) };
```

This fixes 6 of the 14 failures (IdGenerator, StorageService, Ethereum key generation tests).


```bash
cd /app/ScatterWebExtension
echo "SCATTER_ENV=testing" > .env
npm install --legacy-peer-deps
```

Do NOT use `--ignore-scripts` - native modules (`node-sass`, `secp256k1`, `sha3`) must be compiled.

## Test Steps

```bash
SCATTER_ENV=testing npx mocha-webpack --timeout 1000000 \
  --webpack-config webpack.config.js \
  --require tests/setup.js "tests/**/*.spec.js"
```

## Unexpected Issues

- The project is a browser extension relying on Web Crypto API - `crypto.getRandomValues` is not available in Node.js by default
- Using `--ignore-scripts` during `npm install` breaks native crypto bindings (`secp256k1`, `sha3`)
- `ContractHelpers` tests (3 failures) reference `messageChecksum` and `validChecksum` methods that are not implemented - genuine code bugs
- Node.js 12+ may break compatibility with webpack 3 and babel 6
- Achievable pass rate with crypto polyfill fix: ~76-81% (15-17/21)
