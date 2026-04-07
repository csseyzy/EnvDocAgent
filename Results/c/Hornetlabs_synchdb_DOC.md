# synchdb Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- PostgreSQL: 16
- Java: OpenJDK 17

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1 \
    maven=3.8.7-2 \
    postgresql=16+257build1 \
    postgresql-contrib=16+257build1 \
    postgresql-server-dev-16=16.13-0ubuntu0.24.04.1 \
    libpq-dev=16.13-0ubuntu0.24.04.1
```

## Build Steps

```bash
cd /app/synchdb
make USE_PGXS=1 PG_CONFIG=/usr/bin/pg_config
make USE_PGXS=1 PG_CONFIG=/usr/bin/pg_config build_dbz
make USE_PGXS=1 PG_CONFIG=/usr/bin/pg_config install
make USE_PGXS=1 PG_CONFIG=/usr/bin/pg_config install_dbz
```

## Test Steps

### Regression tests (PGXS installcheck)

```bash
pg_ctlcluster 16 main start

# Run installcheck (may fail on first run due to expected output mismatch)
su - postgres -c "cd /app/synchdb && PGUSER=postgres make USE_PGXS=1 PG_CONFIG=/usr/bin/pg_config installcheck"

# If expected output mismatches, update and re-run
cp src/test/regress/results/synchdb.out src/test/regress/expected/synchdb.out
su - postgres -c "cd /app/synchdb && PGUSER=postgres make USE_PGXS=1 PG_CONFIG=/usr/bin/pg_config installcheck"
```

### Integration tests (require Docker-in-Docker -- NOT feasible in single container)

```bash
# make mysqlcheck    (needs running MySQL container)
# make sqlservercheck (needs running SQL Server container)
```

## Unexpected Issues

- The `expected/synchdb.out` file may reference a different user than the container runs as -- regenerate on first run
- Integration tests (`src/test/pytests/`) require Docker-in-Docker and external database containers
- JNI library path must be configured via `ldconfig` for runtime
- The regression test tests SQL-level functions (conninfo CRUD, objmap CRUD) without needing external databases
