# Classic-Generative-Model Deployment Document

## Platform

- OS: Ubuntu 24.04
- Language: Python 3.12 (system)
- Runtime: PyTorch 2.10.0+cpu
- Build System: pip (venv)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    build-essential=12.10ubuntu1 \
    python3=3.12.3-0ubuntu2 \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
    python3-venv=3.12.3-0ubuntu2 \
    libgl1 \
    libglib2.0-0=2.80.0-6ubuntu3.8 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg
```

## Build Steps

```bash
git clone --depth 1 https://github.com/liujf69/Classic-Generative-Model.git /app/project
cd /app/project

python3 -m venv /opt/venv
export PATH="/opt/venv/bin:$PATH"

pip install --upgrade pip setuptools wheel

pip install --index-url https://download.pytorch.org/whl/cpu \
    torch torchvision torchaudio

pip install \
    numpy scipy matplotlib pillow tqdm einops \
    scikit-image imageio opencv-python

pip install \
    diffusers transformers accelerate peft \
    safetensors huggingface-hub

pip install omegaconf==2.3.0
```

`PYTHONPATH` fix for submodules with local imports:

```bash
export PYTHONPATH="/app/project/SD_UNet:/app/project/PixelCNN_VQVAE:$PYTHONPATH"
```

## Test Steps

```bash
cd /app/project
export PATH="/opt/venv/bin:$PATH"
export PYTHONPATH="/app/project/SD_UNet:/app/project/PixelCNN_VQVAE:$PYTHONPATH"

python3 -c "
import importlib, json, sys
modules = [
    'DDPM.DDPM','DDPM.UNet',
    'VAE.VAE_1','VAE.CVAE_1',
    'VQVAE.VQ_VAE',
    'SD_UNet.UNet','SD_UNet.attention','SD_UNet.util',
    'GAN.gan_demo',
    'PixelCNN_VQVAE.main',
    'Cond_AR_Transformer.Demo',
]
passed = 0
for m in modules:
    try:
        importlib.import_module(m)
        passed += 1
    except Exception as e:
        print(f'FAIL {m}: {e}')
print(f'{passed}/{len(modules)} modules imported successfully')
"
```

SD_UNet CPU forward pass test:

```bash
python3 -c "
from SD_UNet.UNet import UNetModel
import torch
model = UNetModel(
    in_channels=4, out_channels=4, model_channels=320,
    attention_resolutions=[4,2,1], num_res_blocks=2,
    channel_mult=[1,2,4,4], num_heads=8,
    use_spatial_transformer=True, transformer_depth=1,
    context_dim=768, use_checkpoint=False, legacy=False,
    image_size=32,
)
x = torch.randn(1,4,32,32)
t = torch.tensor([981])
c = torch.ones(1,77,768)
y = model(x, t, context=c)
print('SD_UNet forward OK', tuple(y.shape))
"
```

## Unexpected Issues

- `SD_UNet.UNet` and `SD_UNet.attention` use `import util` (relative to their own directory), requiring `/app/project/SD_UNet` on `PYTHONPATH`.
- `PixelCNN_VQVAE.main` uses `import utils` (relative), requiring `/app/project/PixelCNN_VQVAE` on `PYTHONPATH`.
- `omegaconf` is not listed in any `requirements.txt` but is required by `Cond_AR_Transformer.Demo` (via diffusers). Must be installed separately.
- `UNetModel.__init__()` requires `image_size` parameter not shown in some tutorials; omitting it causes `TypeError`.
- Many demo scripts (e.g., `SD_UNet/demo.py`, `Simple_DIT/demo.py`) call `.cuda()` directly and will fail on CPU-only environments. The import tests and forward pass tests use CPU tensors to avoid this.
- PEP 668 on Ubuntu 24.04 blocks direct `pip install` outside venv; a virtual environment (`python3 -m venv`) is required.
