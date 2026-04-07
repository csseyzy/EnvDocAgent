# cwhy Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** 3.12

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    python3=3.12.3-0ubuntu2 \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
    python3-venv=3.12.3-0ubuntu2 \
    build-essential=12.10ubuntu1 \
    clang=1:18.0-59~exp2 \
    clangd=1:18.0-59~exp2 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

Key dependencies from `pyproject.toml`:
- openai>=1.84.0
- rich>=13.7.1
- llm-utils>=0.2.8
- hatchling (build system)

## Test Steps

```bash
cd /app/project
. .venv/bin/activate
python -m unittest discover -s test -p 'test_*.py' -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- The test file has a typo in its name (`test_cland_integration.py` instead of `test_clangd_integration.py`)
- The tests require `clangd` to be installed and available on PATH
- The tests check clangd symbol resolution against specific C++ files, so expected output is sensitive to clangd version
- The tests do NOT require an OpenAI API key — they only test the clangd LSP integration
- The `openjdk-17-jdk` package in the original Dockerfile is unnecessary for running tests
