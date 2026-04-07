# py2app Deployment Document

## Platform

- **Base Image:** python:3.12.8-bookworm
- **Python Version:** 3.10+ (pyproject.toml: `requires-python = ">=3.10,<4"`)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9
```

## Build Steps

```bash
cd /app/project
pip install flit_core==3.9.0
pip install setuptools==75.8.2
pip install packaging==24.2
pip install rich==13.9.4
pip install altgraph==0.17.4
pip install modulegraph==0.19.6
pip install modulegraph2==4.2
pip install macholib==1.16.3
pip install coverage==7.6.10
pip install flit==3.10.1
pip install -e .
```

## Test Steps

```bash
cd /app/project
# Only pure-Python unit tests work on Linux:
python -m unittest \
    py2app_tests.test_config \
    py2app_tests.test_filters \
    py2app_tests.test_utils \
    py2app_tests.test_setuptools_stub \
    py2app_tests.test_recipe_imports \
    py2app_tests.test_py2applet \
    -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- **py2app is fundamentally macOS-only.** The `pyproject.toml` classifiers say `Operating System :: MacOS :: MacOS X`. Most tests create actual `.app` bundles using macOS-specific APIs.
- On Linux/Docker, only the pure-Python unit tests (config parsing, filters, utils, recipe imports) will pass
- The `tox.ini` lists `pyobjc` as a test dependency, which is macOS-only
- Tests that actually build `.app` bundles (test_basic_app, test_app_with_scripts, etc.) will fail on Linux
