# richdocuments Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- PHP: 8.3
- Node.js: 20.x (for frontend assets)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    php8.3 php8.3-cli php8.3-xml php8.3-mbstring php8.3-curl \
    php8.3-zip php8.3-gd php8.3-mysql php8.3-intl php8.3-sqlite3 \
    composer wget=1.21.4-1ubuntu4 curl=8.5.0-2ubuntu10.8 unzip=6.0-28ubuntu4
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
npm install -g pnpm
```

## Build Steps


```bash
git clone --depth 1 --branch stable10 https://github.com/owncloud/core.git /app/owncloud
cd /app/owncloud && composer install --no-dev
git clone --depth 1 https://github.com/owncloud/richdocuments /app/owncloud/apps/richdocuments
cd /app/owncloud/apps/richdocuments
composer install
composer bin all install
pnpm install
```

## Test Steps

```bash
cd /app/owncloud/apps/richdocuments
vendor-bin/behat/vendor/bin/phpunit --configuration phpunit.xml --testsuite unit
```

## Unexpected Issues

- The app cannot be tested standalone - it requires the full ownCloud core framework for the test bootstrap
- Without ownCloud core, tests fail with missing OCP interfaces and OC classes (27 errors)
- Correct approach: clone ownCloud core and place the app in `apps/richdocuments/`
