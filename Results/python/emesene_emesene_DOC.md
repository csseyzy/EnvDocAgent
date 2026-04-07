# emesene Deployment Document

## Platform

- **Base Image:** python:2.7-slim-buster
- **Python Version:** 2.7 (explicitly "NO python3" per DEPENDS file)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    python-gobject=3.30.4-1 \
    python-dbus=1.2.8-3 \
    python-crypto=2.6.1-9+b1 \
    python-openssl=19.0.0-1 \
    python-dnspython=1.16.0-1+b1
```

## Build Steps

```bash
cd /app/project
python setup.py install
```

All dependencies are bundled in source tree (papyon, SleekXMPP, pyfb).

## Test Steps

```bash
cd /app/project/emesene
python -m pytest test/test_ring_buffer.py test/test_cache_manager.py test/test_avatar_cache.py test/test_emoticon_cache.py -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- This is an **abandoned Python 2 project** (last commit ~2013). Python 2.7 reached EOL in 2020.
- `python:2.7-slim-buster` is the last available Python 2 Docker image
- GTK-dependent tests cannot run headlessly without `xvfb`
- `test/test_logger.py` has complex dependencies on the `e3` module and may fail
- `test/__main__.py` uses Python 2-style relative imports
- Only `test_ring_buffer.py`, `test_cache_manager.py`, `test_avatar_cache.py`, and `test_emoticon_cache.py` are likely to pass in a headless Docker environment
