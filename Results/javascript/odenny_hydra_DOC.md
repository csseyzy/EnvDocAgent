# hydra Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: OpenJDK 8
- Build tool: Maven
- Database: MySQL

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 openjdk-8-jdk=8u402-ga-8build1 maven=3.8.7-2 curl=8.5.0-2ubuntu10.8 mysql-server mysql-client
```

## Build Steps

```bash
service mysql start
mysql -e "CREATE DATABASE hydra DEFAULT CHARACTER SET utf8;"
mysql -e "CREATE USER 'hydra'@'localhost' IDENTIFIED BY 'hydra';"
mysql -e "GRANT ALL ON hydra.* TO 'hydra'@'localhost';"
```

Initialize the database schema from SQL scripts in the project (check `modules/hydra-manager-db/src/main/resources/`).

```bash
cd /app/hydra
mvn clean install -DskipTests
```

## Test Steps

```bash
service mysql start
mvn test -pl modules/hydra-manager-db,modules/hydra-store/hydra-mysql \
    -Dmaven.test.failure.ignore=true
```

## Unexpected Issues

- ALL tests are Spring integration tests requiring a running MySQL instance - zero unit tests exist
- Without MySQL, every test times out during Spring context initialization (Druid connection pool)
- The `hydra-client` module depends on `com.alibaba:dubbo:2.4.8-SNAPSHOT` which is unavailable from public Maven repos
- The Maven `http://0.0.0.0/` blocker prevents downloading SNAPSHOT dependencies from Sonatype
- Database connection properties (`mysql.properties`) in test resources need to match the provisioned MySQL credentials
- Consider using an embedded H2 database for tests as an alternative
