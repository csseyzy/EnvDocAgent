# ilastik Deployment Document

## Platform

- **Base Image:** continuumio/miniconda3:24.7.1-0
- **Python Version:** 3.11 (via conda)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    mesa-utils \
    libgl1-mesa-dev \
    xvfb=2:21.1.12-1ubuntu1 \
    curl=8.5.0-2ubuntu10.8 \
    git=1:2.43.0-1ubuntu7 \
    build-essential=12.10ubuntu1
```

## Build Steps

```bash
conda install -n base -c conda-forge conda-build setuptools_scm -y
conda create -n ilastik-dev --override-channels \
    -c ilastik-forge/label/patched-2 \
    -c conda-forge \
    -c ilastik-forge \
    python=3.11 \
    numpy=1.26.4 \
    cachetools=5.3.3 \
    dpct=0.3.0 \
    fastfilters=0.3.0 \
    future=1.0.0 \
    greenlet=3.0.3 \
    grpcio=1.62.1 \
    h5py=3.11.0 \
    hytra=1.1.5 \
    ilastik-feature-selection=0.1.0 \
    ilastikrag=0.1.4 \
    ilastiktools=0.3.0 \
    jsonschema=4.21.1 \
    mamutexport=0.2.0 \
    marching_cubes=0.2.0 \
    ndstructs=0.0.14 \
    nifty=1.2.1 \
    "pandas=2.*" \
    platformdirs=4.2.0 \
    psutil=5.9.8 \
    "pydantic>=2.10,<3" \
    pyopengl=3.1.7 \
    "pyqt=5.15.*" \
    "pyqtgraph<0.14" \
    "python-elf>=0.4.8" \
    qimage2ndarray=1.10.0 \
    qtpy=2.4.1 \
    scikit-image=0.22.0 \
    "scikit-learn<=1.6.1" \
    "tifffile>=2022" \
    "vigra=1.12.1" \
    "xarray!=2023.8.0,!=2023.9.0,!=2023.10.0" \
    z5py=2.0.17 \
    "zarr=2.*" \
    aiohttp=3.9.3 \
    fsspec=2024.2.0 \
    "s3fs>=2022.8.2" \
    "pytest>4" \
    pytest-qt=4.4.0 \
    setuptools_scm=8.0.4 \
    -y

conda activate ilastik-dev
pip install -e . --no-deps
```

## Test Steps

```bash
conda activate ilastik-dev
xvfb-run --server-args="-screen 0 1024x768x24" pytest -v \
    --ignore=tests/test_ilastik/data \
    --ignore=tests/test_ilastik/helpers \
    2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This is a conda-only project with many specialized scientific dependencies (vigra, nifty, fastfilters, etc.) that are NOT available on PyPI — must use conda
- Requires X11/Xvfb for PyQt5-based GUI tests
- `scikit-learn>1.6.1` breaks `testContourMWTExport`
- The `lazyflow` subpackage is included in the same repo (not a separate dependency)
