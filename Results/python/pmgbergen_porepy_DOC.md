# porepy Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Python: 3.12 (system Python)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    python3=3.12.3-0ubuntu2 python3-pip=24.0+dfsg-1ubuntu1.1 python3-venv=3.12.3-0ubuntu2 python3-dev=3.12.3-0ubuntu2 \
    build-essential=12.10ubuntu1 cmake=3.28.3-1build7 \
    libglu1-mesa libgeos-dev libffi-dev \
    libgl1 libsm6 libxext6 libxrender1=1:0.9.10-1.1build1 libxcursor1 libxft2 libxinerama1 \
    ffmpeg libglx-mesa0 python3-tk
```





## Build Steps

```bash
python3 -m pip install --upgrade pip

cd /app/project
pip install --no-cache-dir .[testing]
pip install --no-cache-dir pypardiso
```

## Test Steps

```bash
cd /app/project
pytest tests -m "not tutorials"
```


## Unexpected Issues

- **Tutorial tests excluded** via `-m "not tutorials"` -- they require jupyter and additional tooling.
- **OpenGL/X11 libraries needed** for mesh visualization components (`libglu1-mesa`, `libgl1`, etc.).
- **`cmake` required** for building gmsh and other native dependencies.
- **`pypardiso`** installed as optional performance solver.
- **No source code modifications needed.**
