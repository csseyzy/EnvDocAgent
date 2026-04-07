# anvil-level-design Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** Blender's embedded Python 3.11

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    git-lfs=3.4.1-1 \
    xvfb=2:21.1.12-1ubuntu1 \
    wget=1.21.4-1ubuntu4.1 \
    xz-utils=5.6.1+really5.4.5-1build0.1 \
    libxi6=2:1.8.1-1build1 \
    libxxf86vm1=1:1.1.5-1build1 \
    libxfixes3=1:6.0.1-2build1 \
    libxrender1=1:0.9.10-1.1build1 \
    libgl1=1.7.0-1build1 \
    libsm6=2:1.2.4-1 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
git lfs install && git lfs pull

# Download Blender 5.0
cd /opt
wget -q https://download.blender.org/release/Blender5.0/blender-5.0.0-linux-x64.tar.xz
tar -xJf blender-5.0.0-linux-x64.tar.xz
rm blender-5.0.0-linux-x64.tar.xz
export BL5=/opt/blender-5.0.0-linux-x64

# Install addon by symlinking into Blender's addon directory
ADDON_DIR="/root/.config/blender/5.0/scripts/addons"
mkdir -p "$ADDON_DIR"
ln -sf /app/project "$ADDON_DIR/anvil_level_design"
```

## Test Steps

```bash
xvfb-run -a /opt/blender-5.0.0-linux-x64/blender --enable-event-simulate --python /app/project/tests/run_tests.py 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- Blender 5.0 must be downloaded separately (not in Ubuntu repos)
- Git LFS must be installed and `git lfs pull` must succeed to get `workspaces.blend`
- The tests use `--enable-event-simulate` which is a Blender 5.0 feature
- `xvfb` is required for headless rendering
- The Blender 5.0 download URL may change over time
- The addon has 6 test files: `test_smoke.py`, `test_box_builder.py`, `test_cube_cut.py`, `test_uv_extend.py`, `test_texture_apply.py`, and `run_tests.py`
