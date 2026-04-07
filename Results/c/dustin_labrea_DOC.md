# labrea Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Despite being in a C workspace, the project uses `.cc` files and compiles with `g++`.
- Bundled Lua 5.1.4 is statically linked into `labrea.so`. No system Lua package needed.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.10ubuntu1 sed \
    python3=3.12.3-0ubuntu2 python-is-python3
```


## Build Steps


```bash
cd /app/project
python3 -c 'from pathlib import Path; files=["mkwrapfuns.py","mkgeninvoker.py","mkcallfuns.py"]; [Path(f).write_text(Path(f).read_text().replace("file(","open(")) for f in files]'
```


```bash
cd /app/project
chmod +x ./configure
./configure
make -j1
make install PREFIX=/app/install
```


## Test Steps


```bash
/app/install/bin/labrea /app/install/share/labrea/examples/trace.lua /bin/echo SmokeTest
```



## Unexpected Issues

- **Python 2 dependency:** The code generators (`mk*.py`) use Python 2's `file()` builtin. On modern systems without Python 2, must patch `file(` -> `open(` before building.
- **No formal test suite:** Validation is done via smoke-testing the installed wrapper with an example Lua script.
- **`configure` is not autoconf:** It's a simple 32-line shell script that detects OS and substitutes LDFLAGS into `Makefile.in`.
- **Linux-only runtime mechanism:** The wrapper sets `LD_PRELOAD=labrea.so`. Other OSes use different mechanisms.
