# rhinomcp Deployment Document

## Platform

- **Base Image:** python:3.12-slim
- **Python Version:** 3.10+ (CI tests 3.10, 3.11, 3.12)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    curl=7.88.1-10+deb12u8 \
    git=1:2.39.5-0+deb12u1
```

## Build Steps

```bash
pip install uv==0.6.6
cd /app/project/rhino_mcp_server
uv venv
uv pip install -e ".[dev]"
```

Key dependencies from `pyproject.toml`:
- fastmcp==2.14.5
- mcp[cli]==1.16.0
- jsonschema==4.23.0 (dev)
- pytest==8.3.4 (dev)
- pytest-cov==6.0.0 (dev)
- pytest-asyncio==0.24.0 (dev)

## Test Steps

```bash
cd /app/project/rhino_mcp_server
uv run pytest tests/ -v --tb=short 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- The Rhino plugin component is C# (.NET) and cannot be tested in this Docker environment
- Integration tests use a mock Rhino server, so they should work headlessly
- Schema validation tests also exist: `python contracts/test_schemas.py` (requires `jsonschema`)
