# R2CNN_FPN_Tensorflow Deployment Document

## Platform

- **Base Image:** python:2.7.18-buster (CPU-only)
- **Python Version:** 2.7 (README says "python2 + tensorflow1.2")

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.10ubuntu1 \
    git=1:2.43.0-1ubuntu7 \
    libopencv-dev
```

## Build Steps

- `libs/configs/cfgs.py` line 130: Change `ROOT_PATH` from Windows path to the container path (e.g., `/app/project`)
- Set `ROTATE_NMS_USE_GPU = False` in `cfgs.py` for CPU-only environments


```bash
cd /app/project
pip install tensorflow==1.2.0
pip install opencv-python==3.4.2.17
pip install matplotlib==2.2.5
pip install numpy==1.16.6
pip install Cython==0.29.37
pip install Pillow==6.2.2
```

## Test Steps

```bash
cd /app/project/libs/networks/slim_nets
PYTHONPATH=. python -m pytest resnet_v1_test.py resnet_v2_test.py vgg_test.py alexnet_test.py -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This is a very old TF 1.2 project. The `tf.contrib.slim` API was removed in TF 2.x
- Cython extensions require CUDA 8.0 + nvcc for full compilation; CPU-only mode is limited
- The slim_nets tests are from TF-Slim and are self-contained unit tests that work without trained weights
- Python 2 is EOL; `tensorflow==1.2.0` only works with Python 2.7 or Python 3.5
- GPU extensions (`rbbox_overlaps`, `rotate_polygon_nms`) require CUDA toolkit 8.0
