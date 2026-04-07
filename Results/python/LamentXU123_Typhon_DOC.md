# Typhon Deployment Document

## Platform

- **Base Image:** python:3.12-slim
- **Python Version:** 3.9+ (CI tests 3.9, 3.10, 3.11, 3.12, 3.13)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7
```

## Build Steps

```bash
cd /app/project
pip install coverage==7.6.9
```

No external dependencies — Typhon uses only the Python standard library.

## Test Steps

```bash
cd /app/project
python -m unittest discover -s test -p "test_*.py" -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

Or with coverage:
```bash
cd /app/project
coverage run --source Typhon -m unittest discover -s test -p "test_*.py"
coverage report
```

## Unexpected Issues

- Tests use `unittest.mock.patch` to mock `builtins.quit` and `builtins.exit`, which may cause `SystemExit` or `RuntimeError` as expected test behavior
- The WebUI test (`test_webui.py`) tests the built-in HTTP server and should work headlessly
- Tests may take ~1 minute due to the recursive bypass strategy
- This is the **easiest project to deploy** — zero external dependencies, pure Python
