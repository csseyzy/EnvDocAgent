# pycam Deployment Document

## Platform

- **Base Image:** debian:bullseye
- **Python Version:** 3.9

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    python3=3.9.2-3 \
    python3-setuptools=52.0.0-4 \
    python3-pytest=6.0.2-2 \
    python3-numpy=1:1.19.5-1 \
    python3-yaml=5.3.1-5 \
    python3-svg.path=4.1-1 \
    python3-opengl=3.1.5+dfsg-1 \
    python3-gi=3.38.0-2 \
    gir1.2-gtk-3.0=3.24.24-4+deb11u1 \
    codespell=2.0.0-1 \
    help2man=1.47.16-1 \
    make=4.3-4.1 \
    git=1:2.30.2-1+deb11u2
```

## Build Steps

```bash
cd /app/project
python3 setup.py install
```

Key dependencies from `requirements.txt`:
- PyOpenGL==3.1.5
- PyYAML==5.3.1
- svg.path==4.1

## Test Steps

```bash
cd /app/project
python3 -m pytest -v pycam/Test/ 2>&1 | tee /app/project/TEST_RESULTS.txt
```

Test files:
- `pycam/Test/test_polygon.py`
- `pycam/Test/test_intersection.py`
- `pycam/Test/test_pointutils.py`
- `pycam/Test/test_stl_loader.py`
- `pycam/Test/test_dxf_importer.py`
- `pycam/Test/test_svg_loader.py`
- `pycam/Test/test_cxf_fonts.py`
- `pycam/Test/test_motion_grid.py`
- `pycam/Test/test_tools.py`

## Unexpected Issues

- GUI-related tests may fail without a display server; use `xvfb-run python3 -m pytest -v pycam/Test/` if needed
- The `pycam/__init__.py` generates VERSION from git tags; in Docker without a proper git repo, it falls back to `"0.0-unknown"` (fine for testing)
- The existing `Dockerfile` uses `debian:9` (stretch, EOL) which is outdated; use `debian:bullseye` instead
