# E-Stega Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.18+8-1~24.04.1)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1 \
    maven=3.8.7-2 \
    mysql-server=8.0.41-0ubuntu0.24.04.1 \
    redis-server=5:7.0.15-1ubuntu0.24.04 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Start MySQL and create database

```bash
service mysql start
mysql -e "CREATE DATABASE IF NOT EXISTS test;"
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456'; FLUSH PRIVILEGES;"
```

### Step 2: Build (skip tests initially)

```bash
cd /app/project/backend
mvn -q -DskipTests=true clean install
```




## Test Steps



```bash
cd /app/project/backend
mvn test
```

See verification commands in Build Steps.

## Unexpected Issues

- Tests require MySQL running at `localhost:3306` with root password `123456`.
- `checkSpecificBeanPresence` test is a placeholder that will always fail.
- `verifyEnvironmentProperty` test has a compilation error (undefined variables).
- `pom.xml` has `maven-compiler-plugin` duplicated 8 times.
- Consider adding H2 in-memory database for testing as an alternative to MySQL.
