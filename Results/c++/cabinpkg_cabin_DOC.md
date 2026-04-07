# cabin Deployment Document

## Platform

- Ubuntu 24.04

## Prerequisites

- Ubuntu 24.04
- GCC 13
- Ninja 1.11

## Build Steps

```bash
# 1. Clone project
git clone https://github.com/cabinpkg/cabin.git
cd cabin

# 2. Install build dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
  build-essential=12.10ubuntu1 ca-certificates=20240203 git=1:2.43.0-1ubuntu7 pkg-config=1.8.1-2build1 \
  clang=1:18.0-59~exp2 ninja-build=1.11.1-2 \
  libfmt-dev libspdlog-dev libgit2-dev libcurl4-openssl-dev nlohmann-json3-dev libtbb-dev

# 3. Build (release)
make BUILD=release -j4
# Built binary path (for reference):
ls -l build/cabin

# 4. Confirm install target exists
grep -E '^install:' Makefile && echo "INSTALL_TARGET_OK"

# 5. Install to user bin directory and update PATH
make install PREFIX="$HOME/.local"
export PATH="$HOME/.local/bin:$PATH"
# Persist PATH for future shells
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
. ~/.bashrc

# 6. Verify installation
[ -x "$HOME/.local/bin/cabin" ] && echo "CABIN_OK"
```

```bash
sudo apt-get install -y libgit2-dev

```

```bash
sudo apt-get install -y build-essential=12.10ubuntu1

```

```bash
# Use GCC 13 (Ubuntu 24.04 provides GCC 13)
sudo apt-get install -y build-essential=12.10ubuntu1

```
## Test Steps

```
cabin new hello_cabin
cd hello_cabin
cabin run | grep 'Hello, world!'
```
## Unexpected Issues

- `fatal error: fmt/core.h: No such file or directory` — fmt development headers not installed. Install with `sudo apt-get install -y libfmt-dev`.
- `fatal error: curl/curl.h: No such file or directory` — libcurl development headers not installed. Install with `sudo apt-get install -y libcurl4-openssl-dev`.
- Ninja not installed or too old — Ninja missing or version < 1.11. Install with `sudo apt-get install -y ninja-build=1.11.1-2`.
- `make: *** No rule to make target 'install'. Stop.` — Makefile lacks an install target.
- `fatal error: git2.h: No such file or directory` — libgit2 development headers not installed. Install with `sudo apt-get install -y libgit2-dev`.
- `g++: command not found` — C++ compiler not installed. Install with `sudo apt-get install -y build-essential`.
- Compiler does not support C++23 — compiler version too old. Use GCC 13+ on Ubuntu 24.04.
