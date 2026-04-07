# CFGgrind Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    autoconf=2.71-3 \
    automake=1:1.16.5-1.3ubuntu1 \
    libtool=2.4.7-7build1 \
    pkg-config=1.8.1-2build1 \
    patch=2.7.6-7build3 \
    wget=1.21.4-1ubuntu4.1 \
    bzip2=1.0.8-5.1build0.1 \
    binutils=2.42-4ubuntu2 \
    graphviz=2.42.2-9ubuntu0.1 \
    python3=3.12.3-0ubuntu2 \
    gawk=1:5.2.1-2build3 \
    bc=1.07.1-3ubuntu4
```

## Build Steps

```bash
cd /app/cfggrind
wget -qO - https://sourceware.org/pub/valgrind/valgrind-3.26.0.tar.bz2 | tar jx
cd valgrind-3.26.0
patch -p1 < /app/cfggrind/cfggrind.patch
./autogen.sh
./configure
make -j$(nproc)
make install
install -m 0755 /app/cfggrind/cfggrind_asmmap /usr/local/bin/cfggrind_asmmap
install -m 0755 /app/cfggrind/cfggrind_info /usr/local/bin/cfggrind_info
```

## Test Steps


```bash
cd /app/cfggrind/tests

# Compile test program
gcc -g -ggdb -O0 -Wall -fno-stack-protector -no-pie -o test test.c

# Generate assembly map
cfggrind_asmmap ./test > test.map

# Run under CFGgrind
valgrind -q --tool=cfggrind --cfg-outfile=test.cfg --instrs-map=test.map --cfg-dump=bubble ./test 4 8 15 16 23 42

# Verify DOT files were generated
ls -1 *.dot

# Run cfggrind_info
cfggrind_info -s program -i test.map -m json test.cfg
```

## Unexpected Issues

- No automated test runner (`make test` or similar) -- tests are manual/example-based
- The `prototype/test/test.desc` is a trace description file for the prototype simulator, not a runnable test
- Valgrind source must be downloaded and patched -- the plugin builds as part of Valgrind
