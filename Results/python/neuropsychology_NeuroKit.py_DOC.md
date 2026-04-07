# NeuroKit.py Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Python: 3.12 (system Python). Legacy project originally targeting Python 2.7/3.5/3.6.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 pkg-config=1.8.1-2build1 \
    python3=3.12.3-0ubuntu2 python3-pip=24.0+dfsg-1ubuntu1.1 python3-venv=3.12.3-0ubuntu2 python3-dev=3.12.3-0ubuntu2 \
    build-essential=12.10ubuntu1 gfortran \
    libopenblas-dev liblapack-dev \
    libjpeg-turbo8-dev zlib1g-dev=1:1.3.dfsg-3.1ubuntu2 libpng-dev libfreetype6-dev=2.13.2+dfsg-1build3 \
    libffi-dev
```





## Build Steps

```bash
python3 -m pip install -U pip setuptools wheel

cd /app/project
pip install -e .
pip install peakutils
pip install coverage nose pytest
```

## Test Steps

```bash
export MPLBACKEND=Agg
python -m coverage run tests/tests.py
```


## Unexpected Issues

- **Legacy project designed for Python 2.7/3.5/3.6.** Running on 3.12 requires extensive compatibility shims.
- **Needs `gfortran`, `libopenblas-dev`, `liblapack-dev`** for scipy/numpy native builds.
- **Needs image libraries** (`libjpeg-turbo8-dev`, `zlib1g-dev`, `libpng-dev`, `libfreetype6-dev`) for Pillow/matplotlib.
- **`peakutils` is an undeclared dependency** needed by tests.
- **Remaining failures:** Shannon entropy and MSE_AUC value drift (algorithm/dependency version changes), and `z_score` returning ndarray instead of pandas Series.
- **`MPLBACKEND=Agg`** required for headless environments.
