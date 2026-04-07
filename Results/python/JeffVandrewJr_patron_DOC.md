# patron (LibrePatron) Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** 3.7.2 (via pyenv)

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    curl=8.5.0-2ubuntu10.6 \
    build-essential=12.10ubuntu1 \
    libffi-dev=3.4.6-1build1 \
    libssl-dev=3.0.13-0ubuntu3 \
    zlib1g-dev=1:1.3.dfsg-3.1ubuntu2 \
    libbz2-dev=1.0.8-5.1build0.1 \
    libreadline-dev=8.2-4build1 \
    libsqlite3-dev=3.45.1-1ubuntu2 \
    libncursesw5-dev=6.4+20240113-1ubuntu2 \
    liblzma-dev=5.6.1+really5.4.5-1build0.1 \
    xz-utils=5.6.1+really5.4.5-1build0.1 \
    tk-dev=8.6.14-1build1 \
    pkg-config=1.8.1-2build1 \
    make=4.3-4.1build2 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
# Install pyenv and Python 3.7.2
git clone https://github.com/pyenv/pyenv.git /root/.pyenv
export PYENV_ROOT="/root/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
pyenv install 3.7.2
pyenv global 3.7.2

cd /app/project
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Key dependencies from `requirements.txt`:
- Flask==1.0.2
- Flask-SQLAlchemy==2.3.2
- Flask-Migrate==2.3.1
- Flask-Login==0.4.1
- Flask-WTF==0.14.2
- SQLAlchemy==1.3.0
- APScheduler==3.5.3
- pytest==4.0.2
- attrs==18.2.0

## Test Steps

```bash
cd /app/project
. .venv/bin/activate
export FLASK_APP=patron.py
export DATABASE_URL=sqlite:////tmp/app.db
flask db upgrade
python -m pytest tests/ -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- Requires Python 3.7.x specifically (uses `shelve` module behavior and older Flask APIs)
- `config.py` uses `shelve.open()` at import time, which creates files in the project directory
- `tests/tconfig.py` provides a test-specific Config class that avoids production config issues
- `test_scheduler.py` has a `sleep(65)` making it slow (tests APScheduler timing)
- The `attrs==18.2.0` pinning is needed to fix a dependency conflict
