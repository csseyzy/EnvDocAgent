# Wallet (Bitcoin.com) Deployment Document

## Platform

- Base image: `node:6.17.1`
- Node.js: 6.x, npm 3.x (specified in `package.json` engines)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 build-essential=12.10ubuntu1 python2.7 ruby ruby-sass \
    chromium xvfb=2:21.1.12-1ubuntu1
ln -sf /usr/bin/python2.7 /usr/bin/python
```

## Build Steps

```bash
cd /app/Wallet
npm install fs-extra@0.30
cd app-template && node apply.js bitcoincom && cd ..
npm install --unsafe-perm
./fix-asn1.sh
npx bower install --allow-root --config.interactive=false
grunt default
```

## Test Steps

```bash
export CHROME_BIN=$(which chromium)
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
karma start test/karma.conf.js --single-run
```

## Unexpected Issues

- Must use **Node.js 6.x** and **npm 3.x** - specified in `package.json` engines field
- `node-sass 3.13.1` requires Python 2 + Node 6-era node-gyp for native compilation
- **`grunt default` must run before tests** - without it, `bwcModule` AngularJS module is not available, causing injection failures
- Bower components must be installed (`bower install`) - Karma tests reference `bower_components/` files
- `karma.conf.js` may need `browsers: ['ChromeHeadless']` instead of `browsers: ['Chrome']` for headless mode with `--no-sandbox`
