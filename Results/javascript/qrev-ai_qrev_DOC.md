# qrev Deployment Document

## Platform

- Base image: `python:3.11-slim`
- Python: 3.11
- Build tool: Poetry

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 build-essential=12.10ubuntu1 coreutils vim tmux
pip install --no-cache-dir --upgrade pip setuptools wheel poetry
```

## Build Steps

```bash
export PYTHONUNBUFFERED=1
export PIP_DISABLE_PIP_VERSION_CHECK=on
export PIP_DEFAULT_TIMEOUT=100
export POETRY_NO_INTERACTION=1
export POETRY_VIRTUALENVS_CREATE=false
export PYTHONPATH=/app/qrev
```

```bash
cd /app/qrev/ai
poetry install --no-root
pip install toml
pip install 'packaging>=24.2'
cd /app/qrev/ai/projects/agent && poetry install
pip install -e .
cd /app/qrev/ai && poetry install --no-root
```

Download NLTK data:

```bash
python3 -c "import nltk; nltk.download('averaged_perceptron_tagger_eng')"
```

## Test Steps

```bash
cd /app/qrev/ai
pytest -v
```

Tests can also be run per module:

```bash
pytest -v projects/ai/tests/test_mock_openai.py projects/ai/tests/test_nltk.py
pytest -v projects/core/tests/
pytest -v projects/schema/tests/
```

## Unexpected Issues

- The deployed component is the Python AI portion; the JS server/client parts are not covered in this test run
- `packaging` version must be >=24.2; older versions cause Poetry installation failures
- Some postal-related tests require the `libpostal` library and will be skipped if it is not installed
- Pydantic produces deprecated API warnings
- The JS server component requires Node.js >= 18.18 and uses `npm ci` for installation
