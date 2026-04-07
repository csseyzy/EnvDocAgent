# OJ Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Python Version:** 3.12

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1ubuntu7.2 \
    python3=3.12.3-0ubuntu2 \
    python3-pip=24.0+dfsg-1ubuntu1.1 \
    python3-dev=3.12.3-0ubuntu2 \
    python3-venv=3.12.3-0ubuntu2 \
    build-essential=12.10ubuntu1 \
    pkg-config=1.8.1-2build1 \
    gettext=0.21-14ubuntu2 \
    libxml2-dev=2.9.14+dfsg-1.3ubuntu3 \
    libxslt1-dev=1.1.39-0exp1ubuntu1 \
    zlib1g-dev=1:1.3.dfsg-3.1ubuntu2 \
    libjpeg-dev=8c-2ubuntu11 \
    libfreetype6-dev=2.13.2+dfsg-1build3 \
    default-libmysqlclient-dev=1.1.0-1ubuntu1 \
    mysql-server=8.0.37-0ubuntu0.24.04.1 \
    tzdata=2024a-3ubuntu1.1 \
    bash=5.2.21-2ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

Create `dmoj/local_settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dmoj',
        'USER': 'dmoj',
        'PASSWORD': 'dmoj',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
DMOJ_PROBLEM_DATA_ROOT = '/tmp/problems'
STATIC_ROOT = '/tmp/static'
```


```bash
cd /app/project
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt
pip install coverage==7.4.0
```

## Test Steps

```bash
mkdir -p /var/run/mysqld && chown -R mysql:mysql /var/run/mysqld
mysqld --daemonize --bind-address=127.0.0.1
sleep 3
mysql -uroot -e "CREATE DATABASE IF NOT EXISTS dmoj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -uroot -e "CREATE USER IF NOT EXISTS 'dmoj'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'dmoj';"
mysql -uroot -e "GRANT ALL PRIVILEGES ON *.* TO 'dmoj'@'127.0.0.1'; FLUSH PRIVILEGES;"

. .venv/bin/activate
mkdir -p /tmp/problems /tmp/static
python manage.py compilejsi18n
python manage.py test -v 2 judge urlshortener 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- MySQL must be running before tests
- The project has git-based dependencies that may fail to install if GitHub is unreachable
- The `compilejsi18n` step requires `gettext`
- Some tests may require specific database state
- The default sqlite3 config in settings.py won't work because the project uses MySQL-specific features
