# calendar Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Node.js: 16.x (for Gulp 3.x compatibility)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    curl=8.5.0-2ubuntu10.8 bzip2=1.0.8-5.1build0.1 xvfb=2:21.1.12-1ubuntu1 firefox-esr \
    libgtk-3-0 libdbus-glib-1-2 libxt6 libx11-xcb1 libasound2t64
curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
apt-get install -y nodejs
npm install -g yarn
```

## Build Steps


```bash
mkdir -p /app/core/vendor/jquery/dist
mkdir -p /app/core/vendor/moment/min
mkdir -p /app/core/vendor/davclient.js/lib

curl -sL https://code.jquery.com/jquery-2.2.4.js -o /app/core/vendor/jquery/dist/jquery.js
cp /app/core/vendor/jquery/dist/jquery.js /app/core/vendor/jquery/jquery.js
curl -sL https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment-with-locales.js -o /app/core/vendor/moment/min/moment-with-locales.js
cp /app/core/vendor/moment/min/moment-with-locales.js /app/core/vendor/moment/min/moment-with-locales.min.js
curl -sL https://raw.githubusercontent.com/nickvergessen/davclient.js/master/lib/client.js -o /app/core/vendor/davclient.js/lib/client.js

git clone --depth 1 https://github.com/owncloud/calendar /app/apps/calendar
cd /app/apps/calendar
yarn install
yarn run build
```

## Test Steps

```bash
cd /app/apps/calendar
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99
sleep 2
yarn test
```

## Unexpected Issues

- The `karma.js` basePath is `../../../`, so the app must be at `apps/calendar/` with `core/vendor/` two levels up
- Without the vendor JS files (jQuery, Moment, davclient), 168/378 tests fail due to undefined globals
- The `gulpfile.js` hardcodes `browsers: ['Firefox']` in the Karma task - Firefox + Xvfb + `libasound2t64` are required
- Alternative: modify `karma.js` to use `node_modules/` paths and install `jquery`, `moment` as npm dependencies
