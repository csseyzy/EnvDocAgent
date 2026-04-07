# mtmct Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Python: **3.7.7** (via Miniconda conda environment)
- Uses FairMOT, mmdetection, and py-motmetrics on the MTA dataset.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 wget=1.21.4-1ubuntu4 build-essential=12.10ubuntu1 \
    ffmpeg \
    libglib2.0-0 libsm6 libxrender-dev libxext6 \
    libgtk2.0-0 libcanberra-gtk-module
```


```bash
wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
bash /tmp/miniconda.sh -b -p /opt/conda
export PATH=/opt/conda/bin:$PATH

conda create -y -n mtmct python=3.7.7
source activate mtmct
```




## Build Steps

```bash
conda install -y -c pytorch pytorch==1.7.0 torchvision==0.8.0 cpuonly

cd /app/project
sed -i '/^torch==/d' requirements.txt
sed -i '/^torchvision==/d' requirements.txt
pip install --no-cache-dir -r requirements.txt

pip install --no-cache-dir cython
pip install --no-cache-dir -r trackers/fair/requirements.txt

cd trackers/fair/DCNv2 && ./make.sh || true

pip install -q pytest dataclasses future
pip install -q -e evaluation/py_motmetrics
```


## Test Steps

```bash
source activate mtmct
pytest -q evaluation/py_motmetrics/motmetrics/tests
```


## Unexpected Issues

- **DCNv2 build fails without CUDA.** `trackers/fair/DCNv2/make.sh` requires CUDA toolkit; build is skipped for CPU-only environments.
- **torch/torchvision version conflict.** Root `requirements.txt` pins `torch==1.4.0`/`torchvision==0.5.0` but FairMOT needs `pytorch==1.7.0`/`torchvision==0.8.0`. Must strip root pins and install via conda.
- **lapsolver unavailable.** `lapsolver==1.1.0` can fail to build; motmetrics must be patched to use SciPy's `linear_sum_assignment` instead.
- **No unit tests at root level.** Only `evaluation/py_motmetrics/motmetrics/tests/` has a test suite.
- **Full pipeline requires GPU + dataset.** `sh start.sh fair_high_30e` needs CUDA, DCNv2, and the MTA dataset.
