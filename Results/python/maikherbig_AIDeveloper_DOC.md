# AIDeveloper Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** 3.9.10 (via conda)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    wget=1.21.4-1ubuntu4.1 \
    bzip2=1.0.8-5.1build0.1 \
    build-essential=12.10ubuntu1 \
    ffmpeg=7:6.1.1-3ubuntu5 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
bash /tmp/miniconda.sh -b -p /opt/conda && rm -f /tmp/miniconda.sh
export PATH=/opt/conda/bin:$PATH
conda create -y -n aid3_spyder -c conda-forge --override-channels python==3.9.10 spyder==5.2.1 typing-extensions==3.7.4.3
conda run -n aid3_spyder pip install --upgrade setuptools tensorflow==2.7.1
conda run -n aid3_spyder pip install numpy==1.21.6 "protobuf<=3.20.3" scikit-learn==1.0.2 \
    hdf5plugin==3.3.1 Pillow==9.0.0 pandas==1.1.5 psutil==5.9.0 mkl==2022.0.2 \
    pyqtgraph==0.12.3 imageio==2.13.5 opencv-contrib-python-headless==4.5.5.62 \
    openpyxl==3.0.9 xlrd==2.0.1 keras2onnx==1.7.0 tf2onnx==1.9.3 Keras-Applications==1.0.8
```

## Test Steps

```bash
conda run -n aid3_spyder python -c "
import os; os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf, sklearn, imageio, cv2, pandas, pyqtgraph, psutil
print('All imports OK')
print('tf', tf.__version__)
print('sklearn', sklearn.__version__)
" 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This project genuinely has no standard automated tests
- The `aid_cv2_dnn_tests.py` file uses `plt.show()` which requires a display
- The `dclab` dependency is not in the standard requirements
- This is a GUI application — true automated testing would require mocking the Qt/PyQtGraph UI
- The conda TOS acceptance step may block in non-interactive environments
