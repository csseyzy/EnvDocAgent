# igbinary Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- This repo version targets PHP 5.2-5.6. Ubuntu 24.04 ships PHP 8.x by default, which causes build failures (API incompatibilities). Must install PHP 5.6 from the ondrej/php PPA.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.10ubuntu1 autoconf=2.71-3 automake=1:1.16.5-1.3ubuntu1 libtool=2.4.7-7build1 pkg-config=1.8.1-2build1 \
    php-cli php-dev \
    software-properties-common=0.99.48

add-apt-repository -y ppa:ondrej/php
apt-get update
apt-get install -y php5.6-cli php5.6-dev
```


## Build Steps


```bash
cd /app/project
mv configure.ac configure.ac.disabled
mv configure.in configure.in.disabled
```


```bash
cd /app/project
phpize5.6 --clean && phpize5.6
./configure CFLAGS="-O2 -g" --enable-igbinary --with-php-config=/usr/bin/php-config5.6
make -j1
```


## Test Steps

```bash
cd /app/project
NO_INTERACTION=1 TEST_PHP_EXECUTABLE=/usr/bin/php5.6 make test
```


## Unexpected Issues

- **PHP version mismatch is the critical issue.** This repo version is compatible with PHP 5.2-5.6 only. PHP 8.x causes build failures (`zend_dynamic_array.h` not found, API incompatibilities). Must install PHP 5.6 from the ondrej/php PPA and use `phpize5.6`/`php-config5.6` throughout.
- **`configure.ac`/`configure.in` conflict:** These files conflict with the phpize-generated build system. Must be renamed before running `phpize5.6`, otherwise autoconf errors on missing macros.
- **2 skipped tests** are due to APC/APCu extensions not being loaded. These are optional serializer-handler integration tests and do not indicate a problem.
- **Do NOT use default `phpize`/`php-config`** on Ubuntu 24.04 -- they point to PHP 8.x which is incompatible.
