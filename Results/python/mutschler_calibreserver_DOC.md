# calibreserver Deployment Document

## Platform

- **Base Image:** ubuntu:20.04
- **Python Version:** 2.7

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.25.1-1ubuntu3 \
    python2=2.7.17-2ubuntu4 \
    curl=7.68.0-1ubuntu2 \
    tzdata=2024a-0ubuntu0.20.04 \
    bash=5.0-6ubuntu1 \
    ca-certificates=20230311ubuntu0.20.04.1
```

## Build Steps

```bash
cd /app/project
mkdir -p "Calibre Library"
```

No pip install needed — all dependencies are vendored in `lib/`.

## Test Steps

```bash
cd /app/project
python2 cps.py &
sleep 3
{
  echo "=== calibreserver HTTP Endpoint Tests ==="
  echo "Test 1: Main page"
  curl -sSf http://127.0.0.1:8083/ > /dev/null 2>&1 && echo "PASS" || echo "FAIL"
  echo "Test 2: Setup page"
  curl -sS -o /dev/null -w "%{http_code}" http://127.0.0.1:8083/setup | grep -q "200\|302" && echo "PASS" || echo "FAIL"
} 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- Python 2 only project (requires `python2`, not `python3`)
- All dependencies are vendored in `lib/` (no pip install needed)
- `config.ini` is auto-generated on first run
- Requires `Calibre Library` directory to exist (even if empty)
- No formal test suite exists for the application code — only vendored library tests
