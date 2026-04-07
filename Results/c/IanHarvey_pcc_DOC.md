# pcc Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    build-essential=12.10ubuntu1 \
    bison=2:3.8.2+dfsg-1build2 \
    flex=2.6.4-8.2build1 \
    m4=1.4.19-4build1 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Configure

```bash
cd /app/project
./configure
```

### Step 2: Build with -fcommon flag

```bash
make -j$(nproc) CFLAGS='-fcommon'
```


### Step 3: Run tests

```bash
make -C cc/cpp test
```

## Test Steps


```bash
make -C cc/cpp test
```

## Unexpected Issues

- Must build with `CFLAGS='-fcommon'` on GCC 13+ to avoid "multiple definition" linker errors.
- No top-level `make check` target exists. Tests are only available via `make -C cc/cpp test` for the C preprocessor component.
- Test files are in `cc/cpp/tests/` containing `test1`-`test18` (input) and `res1`-`res18` + `res15C`/`res16C` (expected output).
