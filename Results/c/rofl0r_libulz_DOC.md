# libulz Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    binutils=2.42-4ubuntu2
```

## Build Steps

```bash
cd /app/libulz
make -j$(nproc)
```

## Test Steps

```bash
cd /app/libulz

# Compile and run each test
gcc -std=c99 -Iinclude -o tests/md5_test tests/md5_test.c -Llib -lulz && tests/md5_test
gcc -std=c99 -Iinclude -o tests/base64_test tests/base64_test.c -Llib -lulz && tests/base64_test
gcc -std=c99 -Iinclude -o tests/crc32_test tests/crc32_test.c -Llib -lulz && tests/crc32_test
gcc -std=c99 -Iinclude -o tests/hashlist_test tests/hashlist_test.c -Llib -lulz && tests/hashlist_test
gcc -std=c99 -Iinclude -o tests/ipv4fromstring_test tests/ipv4fromstring_test.c -Llib -lulz && tests/ipv4fromstring_test

# List tests with numeric argument requirement
gcc -std=c99 -Iinclude -DDATASIZE=256 -o tests/sblist_test tests/sblist_test.c -Llib -lulz && tests/sblist_test 100
gcc -std=c99 -Iinclude -DDATASIZE=256 -o tests/tglist_test tests/tglist_test.c -Llib -lulz && tests/tglist_test 100

# iniparser test (must run from tests/ directory)
cd tests && gcc -std=c99 -I../include -o iniparser_test_nextsection iniparser_test_nextsection.c -L../lib -lulz && ./iniparser_test_nextsection && cd ..
```

## Unexpected Issues

- `sblist_test`, `tglist_test`, etc. require a numeric command-line argument
- `DATASIZE` macro must be defined externally for list tests: `-DDATASIZE=256`
- `iniparser_test_nextsection` reads `test.ini` from CWD -- must run from `tests/` directory
