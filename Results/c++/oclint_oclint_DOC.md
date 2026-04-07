# oclint Deployment Document

## Platform

- Tech: C++11 + CMake 3.20 + LLVM/Clang Tooling

## Prerequisites

- CMake 3.20
- C++ compiler with C++11 support
- LLVM/Clang tooling (libclang, llvm-config)
- Git

## Build Steps

```bash
# 1. Clone project
git clone https://github.com/oclint/oclint.git
cd oclint

# 2. Install build prerequisites (Debian/Ubuntu)
sudo apt-get update
sudo apt-get install -y build-essential=12.10ubuntu1 cmake=3.28.3-1build7 g++=4:13.2.0-7ubuntu1 clang=1:18.0-59~exp2 llvm-dev libclang-dev git=1:2.43.0-1ubuntu7

# 3. Verify toolchain availability (fail-fast)
cmake --version | head -n 1  # Expected to contain: cmake version
g++ --version | head -n 1    # Expected to contain: g++ (GCC)
clang --version | head -n 1  # Expected to contain: clang version
llvm-config --version        # Expected to print an LLVM version

git --version               # Expected to contain: git version

# 4. Configure environment variables
# No environment variables required; create an empty .env for consistency
cat > .env << 'EOF'
EOF

# 5. Build the project with CMake
mkdir -p build
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel

# 6. Locate the built binary and verify help output
BIN="$(find build -type f -name oclint -executable -print -quit)"
if [ -z "$BIN" ]; then echo "oclint binary not found in build directory"; exit 1; fi
echo "Found: $BIN"
"$BIN" -help | head -n 1
"$BIN" -help | grep -i '^Usage:'


```

## Test Steps


See verification commands in Build Steps.

## Unexpected Issues

- `CMake Error: The current CMake version is lower than required` — CMake version below 3.20 (project requires minimum 3.20). Install CMake 3.20 or newer.
- `fatal error: 'clang/Tooling/CommonOptionsParser.h' file not found` — missing LLVM/Clang tooling headers. Install LLVM/Clang development packages.
- `make: g++: Command not found` — build-essential tools not installed. Install with `sudo apt-get install -y build-essential`.
- oclint binary not found in build directory during verification — target name or build directory structure differs by configuration.
