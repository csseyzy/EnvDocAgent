# WorkArena Deployment Document

## Platform

- Base image: `ubuntu:24.04` (or `ubuntu:22.04` to avoid libasound2 issue)
- Python: 3.12 (system Python on 24.04) or 3.10 (on 22.04, matches CI)
- Requires Playwright with Chromium for browser automation.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    python3=3.12.3-0ubuntu2 python3-pip=24.0+dfsg-1ubuntu1.1 python3-venv=3.12.3-0ubuntu2
```

## Build Steps

```bash
python3 -m venv /opt/venv
export PATH="/opt/venv/bin:$PATH"
pip install --upgrade pip setuptools wheel

cd /app/project/dev
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir huggingface_hub

playwright install chromium --with-deps
```

`dev/requirements.txt` includes: `pytest`, `pytest-xdist`, `pytest-playwright`, `browsergym-core`, `-e ..` (editable install of the project).
## Test Steps

```bash
pytest -n 2 --durations=10 -m 'not slow and not pricy' \
    -k 'not test_api and not test_utils and not test_validate' -v tests
```

9 pass, 2 skip. Tests requiring ServiceNow credentials are excluded.


## Unexpected Issues

- **External credentials required.** Most tests need a live ServiceNow instance. Required env vars: `SNOW_INSTANCE_URL`, `SNOW_INSTANCE_UNAME`, `SNOW_INSTANCE_PWD` -- or `HUGGING_FACE_HUB_TOKEN` with access to gated dataset `ServiceNow/WorkArena-Instances`.
- **Ubuntu 24.04 libasound2 issue.** Playwright's `--with-deps` tries to install `libasound2` which is a virtual package on 24.04. Fix: pre-install `libasound2t64` or use `ubuntu:22.04`.
- **PEP 668 on Ubuntu 24.04.** Direct `pip install` outside a venv is blocked. Must use a virtual environment.
- **Instance-dependent tests.** `test_api.py`, `test_utils.py`, `test_validate.py` all require a real ServiceNow instance.
- **No source code modifications needed.**
