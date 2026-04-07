# OpenDKIM Deployment Document

## Platform

- Base image: `ubuntu:20.04`
- OpenSSL 1.1.1 is available on Ubuntu 20.04. The configure script has a known issue detecting `SSL_library_init` (deprecated in OpenSSL 1.1+), requiring cache variable overrides.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.25.1-1ubuntu3

apt-get update && apt-get install -y --no-install-recommends \
    tzdata bash ca-certificates=20230311ubuntu0.20.04.1 \
    build-essential=12.8ubuntu1 autoconf=2.69-11.1 automake=1:1.16.1-4ubuntu6 libtool pkg-config=0.29.1-0ubuntu4 \
    libssl-dev libmilter-dev libbsd-dev \
    libdb-dev libldap2-dev liblua5.3-dev
```


## Build Steps

```bash
cd /app/project
autoreconf -fi
ac_cv_search_SSL_library_init=-lssl ac_cv_lib_ssl_SSL_library_init=yes ./configure --disable-shared
make -j$(nproc)
```


## Test Steps

```bash
cd /app/project
make check
```


## Unexpected Issues

- **OpenSSL `SSL_library_init` detection failure (critical):** On Ubuntu 20.04 with OpenSSL 1.1.1, the configure script checks for `SSL_library_init` which is deprecated and replaced by a macro. `AC_SEARCH_LIBS` fails because the symbol isn't exported as a linkable function. Must pass `ac_cv_search_SSL_library_init=-lssl` and `ac_cv_lib_ssl_SSL_library_init=yes` at configure time.
- **`--disable-shared` required:** Without this flag, shared/static library mismatch issues occur during linking.
- **No source code modifications needed.** The only workaround is passing autoconf cache variables at configure time.
- **`rrdtool` not found** but is optional (only needed for RRD-based statistics features).
