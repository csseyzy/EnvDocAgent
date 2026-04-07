# qwadmin Deployment Document

## Platform

- OS: Ubuntu 24.04
- Database: MariaDB (bundled in Ubuntu 24.04 repos)
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 \
    php php-cli php-mysql php-mbstring php-xml php-curl php-gd php-zip \
    mariadb-server mariadb-client
```

## Build Steps

```bash
git clone --depth 1 https://github.com/qiaweicom/qwadmin.git /app/project
cd /app/project

service mariadb start
mysql -e "CREATE DATABASE IF NOT EXISTS qwadmin;"
mysql qwadmin < sql.sql
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;"

mkdir -p App/Runtime && chmod -R 755 App/Runtime
```

## Test Steps

```bash
cd /app/project
service mariadb start
php -S 0.0.0.0:8000 -t . &
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/index.php/Qwadmin/
```

## Unexpected Issues

- MariaDB service must be manually started inside Docker container (`service mariadb start`) before database operations.
- `App/Runtime/` directory does not exist after clone; must be created manually with write permissions for ThinkPHP cache and compiled templates.
- Database schema import (`sql.sql`) must be done after creating the `qwadmin` database; it creates 11 tables with `qw_` prefix.
- The `root` MariaDB user has no password by default; set password to `root` to match `App/Common/Conf/db.php` configuration.
