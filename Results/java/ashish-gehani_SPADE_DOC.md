# SPADE Deployment Document

## Platform

- **Base Image:** `ubuntu:22.04`
- **JDK:** OpenJDK 11 (`openjdk-11-jdk` = 11.0.21+9-0ubuntu1~22.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.34.1-1ubuntu1 \
    openjdk-11-jdk=11.0.21+9-0ubuntu1~22.04 \
    gcc=4:11.2.0-1ubuntu1 \
    make=4.3-4.1build1 \
    autoconf=2.71-2 \
    libaudit-dev=1:3.0.7-1build1 \
    auditd=1:3.0.7-1build1 \
    libfuse-dev=2.9.9-5ubuntu3 \
    pkg-config=0.29.2-1ubuntu3 \
    wget=1.21.2-2ubuntu1 \
    unzip=6.0-26ubuntu3 \
    postgresql=14+238 \
    postgresql-client=14+238 \
    curl=7.81.0-1ubuntu1 \
    ca-certificates=20230311ubuntu0.22.04.1
```

## Build Steps

### Step 1: Configure and build

```bash
cd /app/project
./configure
```

If Neo4j download fails, build without Neo4j/Quickstep modules:

```bash
mkdir -p build
find src -type f -name '*.java' \
    ! -path 'src/spade/storage/Neo4j.java' \
    ! -path 'src/spade/storage/Quickstep.java' \
    ! -path 'src/spade/storage/neo4j/*' \
    ! -path 'src/spade/storage/quickstep/*' \
    -print0 | xargs -0 javac -Xlint:none -proc:none -cp 'lib/*' -d build
jar cvf lib/spade.jar -C build .
```



## Test Steps

### Step 1: Set up PostgreSQL for tests

```bash
service postgresql start
su - postgres -c "psql -c \"CREATE ROLE spade WITH LOGIN SUPERUSER PASSWORD 'spade';\""
su - postgres -c "psql -c \"CREATE DATABASE spade_db OWNER spade;\""
```

### Step 2: Download JUnit 5 and run tests

```bash
wget -O lib/junit-platform-console-standalone-1.10.2.jar \
    https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.10.2/junit-platform-console-standalone-1.10.2.jar

mkdir -p test_build
javac -cp 'build:lib/*' -d test_build test/storage/SQLTest.java

java -jar lib/junit-platform-console-standalone-1.10.2.jar \
    --class-path 'test_build:build:lib/*' \
    --scan-class-path test_build
```

## Unexpected Issues

- Neo4j embedded JARs are not bundled in `lib/`; `bin/downloadNeo4j` script must fetch them.
- `SQLTest` requires a running PostgreSQL instance with specific credentials.
- The `configure` script generates `Makefile` from `Makefile.in`.
- `commons-lang3` is missing from `lib/` — needed for Quickstep module.
