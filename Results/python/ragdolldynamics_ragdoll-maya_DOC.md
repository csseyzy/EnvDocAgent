# ragdoll-maya Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** 3.12

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    python3=3.12.3-0ubuntu2 \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
    build-essential=12.10ubuntu1 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /app/project
python3 -m pip install --break-system-packages pip
```

## Test Steps

```bash
cd /app/project
python3 -c "import ragdoll; print('Import OK')" 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This project genuinely has zero test files
- The `ragdoll` package imports Maya-specific modules (`from maya import cmds`) at various points, so anything beyond `import ragdoll` will fail outside Maya
- The package requires Autodesk Maya's Python runtime (cmds, OpenMaya API) which is proprietary and cannot be installed in Docker
- The `upgrade_assets.py` script is the only standalone-runnable Python file
- The repository is primarily for the Python package + documentation website source (mkdocs)
