# ProjectManager Deployment Document

## Platform

- **Base Image:** python:3.10-slim
- **Python Version:** 3.10

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.39.5-0+deb12u1
```

## Build Steps

```bash
pip install --upgrade pip==24.3.1
```

No Python package dependencies — this is a Sublime Text plugin.

## Test Steps

The tests **cannot be run** in a standard Docker container. They require:
- Sublime Text application (the `sublime` and `sublime_plugin` modules are provided by Sublime Text's embedded Python)
- The `unittesting` Sublime Text package (`from unittesting.helpers import TempDirectoryTestCase`)
- A running Sublime Text window

The CI uses `SublimeText/UnitTesting` GitHub Action which installs Sublime Text and runs tests inside it.

Minimal syntax validation only:
```bash
python3 -c "
import py_compile, sys
try:
    py_compile.compile('project_manager.py', doraise=True)
    py_compile.compile('json_file.py', doraise=True)
    print('Syntax OK')
except py_compile.PyCompileError as e:
    print(f'FAIL: {e}')
    sys.exit(1)
" 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- **This project is NOT testable in a standard Docker container.** It is a Sublime Text plugin that requires the Sublime Text runtime.
- The only Python files are `project_manager.py` and `json_file.py`, which import `sublime` and `sublime_plugin`
- Recommend marking as **untestable in Docker**
