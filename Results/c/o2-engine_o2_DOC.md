# o2 Deployment Document

## Platform

- Base image: `ubuntu:22.04`
- Compiler: g++ 11 (C++20 support)
- CMake: 3.22+

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.9ubuntu3 \
    cmake=3.22.1-1ubuntu1 \
    git=1:2.34.1-1ubuntu1 \
    g++=4:11.2.0-1ubuntu1 \
    libx11-dev=2:1.7.5-1ubuntu0.3 \
    libgl-dev=1.4.0-1 \
    libglx-dev=1.4.0-1 \
    libglu1-mesa-dev=9.0.2-1 \
    libxrandr-dev=2:1.5.2-1build1 \
    libxinerama-dev=2:1.1.4-3 \
    libxcursor-dev=1:1.2.0-2build4 \
    libxi-dev=2:1.8-1build1 \
    libfreetype-dev=2.11.1+dfsg-1ubuntu0.2 \
    libpng-dev=1.6.37-3build5 \
    zlib1g-dev=1:1.2.11.dfsg-2ubuntu9 \
    python3=3.10.6-1~22.04
```

## Build Steps


### 1. Create missing Linux platform headers

The Linux rendering backend is incomplete. `ShaderBase.h` and `MaterialBase.h` don't exist for Linux:

```bash
cd /app/o2

cat > Framework/Sources/o2/Render/Linux/ShaderBase.h << 'EOF'
#pragma once
#if defined(PLATFORM_LINUX) && !defined(O2_RENDER_GLES2)
#include "o2/Render/Linux/OpenGL.h"
namespace o2 {
    class ShaderBase {
    protected:
        GLuint mHandle = 0;
    };
}
#endif
EOF

cat > Framework/Sources/o2/Render/Linux/MaterialBase.h << 'EOF'
#pragma once
#if defined(PLATFORM_LINUX) && !defined(O2_RENDER_GLES2)
#include "o2/Render/Linux/OpenGL.h"
namespace o2 {
    class MaterialBase {
    protected:
        GLuint mShaderProgram = 0;
    };
}
#endif
EOF
```

### 2. Uncomment Linux includes

```bash
sed -i 's|// #include "o2/Render/Linux/ShaderBase.h"|#include "o2/Render/Linux/ShaderBase.h"|' \
    Framework/Sources/o2/Render/Shader.h

sed -i 's|// #include "o2/Render/Linux/MaterialBase.h"|#include "o2/Render/Linux/MaterialBase.h"|' \
    Framework/Sources/o2/Render/Material.h
```

### 3. Disable JerryScript LTO and -Werror

```bash
sed -i 's|set(ENABLE_LTO                ON  CACHE BOOL "" FORCE)|set(ENABLE_LTO                OFF CACHE BOOL "" FORCE)|' \
    Framework/3rdPartyLibs/CMakeLists.txt
```


```bash
cd /app/o2

git submodule update --init --recursive

cmake -S . -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DO2_TESTS=ON \
    -DO2_EDITOR=OFF \
    -DO2_TRACY=OFF \
    -DCMAKE_CXX_FLAGS="-Wno-error" \
    -DCMAKE_C_FLAGS="-Wno-error"

cmake --build build -j$(nproc)
```

## Test Steps

```bash
cd /app/o2/build
ctest --output-on-failure
```

Or directly:

```bash
./build/Tests/o2Tests
```

## Unexpected Issues

- **Linux rendering support is explicitly WIP** -- `ShaderBase.h` and `MaterialBase.h` must be created as stubs
- The stubs allow compilation but actual shader compilation/material pipeline methods need real implementations for rendering
- JerryScript hardcodes `-Werror` and `ENABLE_LTO ON` which fails with GCC 12+/13+ due to `-Werror=maybe-uninitialized`
- The GLES2 render path references a directory with a space (`Linux GLES2`) that doesn't exist
- Tracy profiler should be disabled (`-DO2_TRACY=OFF`) in headless environments
- Google Test v1.14.0 is fetched at configure time via FetchContent (requires internet access)
- The tests exercise the scripting/math layer and should pass without a working render backend
