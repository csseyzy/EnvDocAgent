# node-oracle Deployment Document

## Platform

- OS: Ubuntu 24.04 (Linux 6.8.0)
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    curl=8.5.0-2ubuntu10.8 build-essential=12.10ubuntu1 python3=3.12.3 libaio1t64

curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
```


```bash
export OCI_HOME=/opt/instantclient_11_2
export OCI_LIB_DIR=/opt/instantclient_11_2
export OCI_INCLUDE_DIR=/opt/instantclient_11_2/sdk/include
export OCI_VERSION=11
export NLS_LANG=AMERICAN_AMERICA.UTF8
export LD_LIBRARY_PATH=/opt/instantclient_11_2:$LD_LIBRARY_PATH
```

## Build Steps

```bash
git clone --depth 1 https://github.com/joeferner/node-oracle.git /app/node_oracle
cd /app/node_oracle
npm install
```

Produces `build/Release/oracle_bindings.node` (14,928 bytes) via node-gyp 10.3.1.

## Test Steps

```bash
npm test
```

## Unexpected Issues

- Oracle Instant Client not in apt: must be manually downloaded (license acceptance required). Without SDK, v0.3.9 fails (`occi.h` not found).
- `libaio1` vs `libaio1t64`: Ubuntu 24.04 uses `libaio1t64`.
- All tests require a running Oracle DB instance with credentials and schema.
