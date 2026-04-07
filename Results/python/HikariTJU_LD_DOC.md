# LD Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Python: **3.8** (via Miniconda). PyTorch 1.8 does not support Python 3.9+.
- Built on MMDetection framework. Requires `mmcv-full==1.2.7` compiled with CPU ops.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 wget=1.21.4-1ubuntu4 \
    build-essential=12.10ubuntu1 ninja-build=1.11.1-2 \
    ffmpeg libsm6 libxext6 libxrender1=1:0.9.10-1.1build1 libglib2.0-0 libgl1 \
    pkg-config=1.8.1-2build1 python3=3.12.3-0ubuntu2
```


```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p /opt/miniconda && rm miniconda.sh
export PATH=/opt/miniconda/bin:$PATH

conda create -y -n ldenv python=3.8
export PATH=/opt/miniconda/envs/ldenv/bin:$PATH
```




## Build Steps


```bash
pip install --upgrade pip setuptools wheel

pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio==0.8.0 \
    -f https://download.pytorch.org/whl/torch_stable.html

pip install mmcv==1.2.7
pip uninstall -y mmcv
MMCV_WITH_OPS=1 FORCE_CUDA=0 pip install --no-cache-dir mmcv-full==1.2.7

cd /app/project
pip install -r requirements/build.txt
pip install -r requirements/runtime.txt
pip install -r requirements/optional.txt
pip install -r requirements/tests.txt
pip install --no-cache-dir -e .

pip uninstall -y pycocotools mmpycocotools
pip install --no-cache-dir pycocotools==2.0.7
```

## Test Steps

```bash
MPLBACKEND=Agg pytest -q
```


## Unexpected Issues

- **mmcv vs mmcv-full:** Must install `mmcv-full==1.2.7` (not plain `mmcv`) to get `mmcv.ops` required by MMDetection. Build with `MMCV_WITH_OPS=1 FORCE_CUDA=0`.
- **mmpycocotools build failure:** Use `pycocotools==2.0.7` instead + inject `pycocotools.__version__` via sitecustomize.
- **NumPy compatibility:** Code uses deprecated aliases (`np.int`, `np.bool`, etc.) removed in NumPy 1.24+. Fixed via sitecustomize shim.
- **Test images missing:** `tests/data/color.jpg` and `tests/data/gray.jpg` are not in the repo.
- **Remaining failures** are mostly doctest signature mismatches, NMS config key differences, and missing `mmengine` module -- pre-existing repo issues.
- **MPLBACKEND=Agg** required for headless environments.
- **Requires Python 3.8 specifically.**
