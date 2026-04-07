# wiselib Deployment Document

## Platform

- Base image: `ubuntu:22.04`
- Compiler: g++ 11

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.9ubuntu3 \
    g++=4:11.2.0-1ubuntu1 \
    make=4.3-4.1build1 \
    libboost-dev=1.74.0.3ubuntu7 \
    libboost-system-dev=1.74.0.3ubuntu7 \
    libpthread-stubs0-dev=0.4-1build2 \
    doxygen=1.9.1-2ubuntu2 \
    git=1:2.34.1-1ubuntu1
```

## Build Steps


### 1. Create config.h for timer_test

```bash
cd /app/wiselib
cat > apps/pc_apps/timer_test/config.h << 'EOF'
#ifndef __CONFIG_H
#define __CONFIG_H
#define RADIO_BASE_MAX_RECEIVERS 10
#define UART_BASE_MAX_RECEIVERS 10
#define STATE_CALLBACK_BASE_MAX_RECEIVERS 10
#define SENSOR_CALLBACK_BASE_MAX_RECEIVERS 10
#endif
EOF
```

### 2. Fix Makefile.base include path

```bash
sed -i 's|CXXFLAGS+=-I$(WISELIB_STABLE) -I$(WISELIB_TESTING)|CXXFLAGS+=-I. -I$(WISELIB_STABLE) -I$(WISELIB_TESTING)|' \
    apps/pc_apps/Makefile.base
```

### 3. Create Boost endian compatibility shim (for Boost >= 1.72)

```bash
mkdir -p wiselib.testing/boost/detail/
cat > wiselib.testing/boost/detail/endian.hpp << 'EOF'
#ifndef BOOST_DETAIL_ENDIAN_HPP
#define BOOST_DETAIL_ENDIAN_HPP
#include <boost/predef/other/endian.h>
#if BOOST_ENDIAN_BIG_BYTE
#define BOOST_BIG_ENDIAN
#elif BOOST_ENDIAN_LITTLE_BYTE
#define BOOST_LITTLE_ENDIAN
#endif
#endif
EOF
```


```bash
cd /app/wiselib/apps/pc_apps/timer_test
make -j1
```

## Test Steps

```bash
cd /app/wiselib/apps/pc_apps/timer_test
timeout 10 ./timer_test
echo "Exit code: $?"
```

## Unexpected Issues

- **timer_test runs forever** -- it enters a POSIX event loop; must always use `timeout`
- **Header-only library** -- there's nothing to "build" for the library itself; only example apps compile
- `boost/detail/endian.hpp` was removed in modern Boost -- needs a compatibility shim
- Each app is expected to provide its own `config.h` but the Makefile doesn't document this
- `Makefile.base` doesn't add `-I.` so the app's local `config.h` is invisible to headers in `wiselib.stable/`
- Most apps target embedded platforms (iSense, Contiki); only `apps/pc_apps/` works on x86 Linux
