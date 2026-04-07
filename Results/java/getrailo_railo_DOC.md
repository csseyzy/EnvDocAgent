# railo Deployment Document

## Platform

- **Base Image:** `eclipse-temurin:8-jdk-jammy`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    ant=1.10.12-1 \
    curl=7.81.0-1ubuntu1 \
    unzip=6.0-26ubuntu3 \
    wget=1.21.2-2ubuntu1 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Download and extract Lucee Express

```bash
curl -fsSL -o /tmp/lucee-express.zip https://cdn.lucee.org/lucee-express-5.4.4.38.zip
mkdir -p /opt/lucee
unzip -o /tmp/lucee-express.zip -d /opt/lucee
```

The `-o` flag is **critical** to avoid interactive overwrite prompts in non-TTY environments.

### Step 2: Map webroot and start server

```bash
rm -rf /opt/lucee/webapps/ROOT
ln -s /app/project/railo-cfml /opt/lucee/webapps/ROOT
chmod +x /opt/lucee/bin/*.sh /opt/lucee/startup.sh
export JAVA_HOME=/opt/java/openjdk
/opt/lucee/startup.sh
sleep 15
```

### Step 3: Configure build properties

```bash
cd /app/project/railo-java/railo-core
sed -i 's|railo.url=http://compile/compileAdmin.cfm|railo.url=http://localhost:8888/compileAdmin.cfm|' build.properties
```

### Step 4: Run the master Ant build

```bash
cd /app/project/railo-java/railo-master
ant -Drailo.password=admin master
```

The `-Drailo.password=admin` is required to avoid interactive password prompt.


## Test Steps

```bash
ls /app/project/railo-java/railo-core/dist/*.rc
```

## Unexpected Issues

- Build **requires** a running CFML server (Lucee or Railo Express) — cannot build offline.
- The `createadmin` Ant target uses `<input>` to prompt for admin password — must supply `-Drailo.password=<value>`.
- `unzip` **must** use `-o` flag to force overwrite, otherwise it blocks on interactive prompt.
- Lucee server needs 10-15 seconds to fully start before `compileAdmin.cfm` is accessible.
- Version 4.1.2.005 is very old (2013); Railo was superseded by Lucee in 2015.
- No JUnit test suite exists — the "test" is successful build producing a `.rc` patch file.
