# MicroModem Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Cross-compiler: gcc-avr (for firmware build)
- Native compiler: gcc (for hosted unit tests)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    make=4.3-4.1build2 \
    gcc-avr=1:7.3.0+Atmel3.7.0-1 \
    binutils-avr=2.26.20160125+Atmel3.7.0-2 \
    avr-libc=1:2.0.0+Atmel3.7.0-1
```

## Build Steps

```bash
cd /app/micromodem
make
avr-size images/Modem.elf
```

## Test Steps

Tests use the BeRTOS `TEST_MAIN(module)` macro which activates when compiled with `-DARCH=16`. Tests are designed as hosted (x86) executables:

```bash
cd /app/micromodem

# Compile and run the byteorder test (simplest, fewest dependencies)
gcc -std=gnu99 -DARCH=16 -Ibertos -I. \
    -o byteorder_test bertos/cpu/byteorder_test.c \
    && ./byteorder_test && echo "PASS: byteorder_test"

# Compile and run bitarray test
gcc -std=gnu99 -DARCH=16 -Ibertos -I. \
    -o bitarray_test bertos/struct/bitarray_test.c -lm \
    && ./bitarray_test && echo "PASS: bitarray_test"
```

## Unexpected Issues

- This is an **embedded firmware project** -- the main build cross-compiles for AVR microcontrollers
- The `test/run_tests.sh` script referenced by `make check` is **missing** from the repo
- Tests must be compiled with `-DARCH=16` to enable `UNIT_TEST` mode and the `TEST_MAIN()` macro
- Many test files have deep dependencies on BeRTOS internals that may need stubs for hosted compilation
- Tests like `timer_test.c` depend on hardware abstractions (IRQ, watchdog) that cannot run on x86
- `byteorder_test.c` is the simplest and most reliably runnable test
