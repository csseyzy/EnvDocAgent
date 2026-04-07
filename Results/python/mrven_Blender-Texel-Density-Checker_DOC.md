# Blender-Texel-Density-Checker Deployment Document

## Platform

- **Base Image:** ubuntu:22.04
- **Python Version:** 3.11 (bundled with Blender 4.2+)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9ubuntu3 \
    g++=4:11.2.0-1ubuntu1 \
    libgl1-mesa-glx \
    libxi6 \
    libxrender1 \
    xvfb \
    wget=1.21.2-2ubuntu1.1 \
    xz-utils
```

## Build Steps

```bash
# Install Blender 4.2 (from official tarball)
wget -q https://download.blender.org/release/Blender4.2/blender-4.2.0-linux-x64.tar.xz
tar -xf blender-4.2.0-linux-x64.tar.xz -C /opt/
ln -s /opt/blender-4.2.0-linux-x64/blender /usr/local/bin/blender

# Compile C++ backend
cd /app/project/tdcore/
g++ -c -fPIC tdcore.cpp -o tdcore.o
g++ -shared -o libtdcore.so tdcore.o
cp libtdcore.so ../texel_density_2025_1_2/libs/

# Install addon into Blender
mkdir -p ~/.config/blender/4.2/scripts/addons/texel_density_2025_1_2
cp -r /app/project/texel_density_2025_1_2/* ~/.config/blender/4.2/scripts/addons/texel_density_2025_1_2/
```

## Test Steps

```bash
xvfb-run blender --background --python-expr "
import bpy
bpy.ops.preferences.addon_enable(module='texel_density_2025_1_2')
bpy.ops.object.texel_density_run_tests()
" 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- **Tests require a running Blender instance** with `bpy` context. Standard `pytest`/`unittest` cannot run these tests.
- Blender needs a display server; `xvfb-run` provides a virtual framebuffer for headless operation
- The C++ backend falls back to Python if `libtdcore.so` is not found, so tests can still pass without it
- The `libs/` directory ships with Windows DLLs only; the `libtdcore.so` must be compiled from `tdcore/tdcore.cpp`
- Tests use `bpy.context.area` which may be `None` in background mode
