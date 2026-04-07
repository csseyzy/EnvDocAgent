# awips2 Deployment Document

## Platform

- **Base Image:** `eclipse-temurin:11-jdk-jammy`
- **JDK:** JDK 11

## Prerequisites

```bash
apt-get update && apt-get install -y \
    ant=1.10.12-1 \
    python3=3.10.6-1~22.04 \
    python3-pip=22.0.2+dfsg-1ubuntu0.4 \
    postgresql-14=14.13-0ubuntu0.22.04.1 \
    libhdf5-dev=1.10.7+repack-4ubuntu2 \
    curl=7.81.0-1ubuntu1 \
    unzip=6.0-26ubuntu3 \
    ca-certificates=20240203
```

## Build Steps

**WARNING: AWIPS2 is NOT buildable in a simple Docker container.** The build system is Eclipse PDE-based and requires:
- A full Eclipse PDE installation at `/awips2/eclipse` (normally installed via Unidata RPMs)
- Hundreds of pre-compiled OSGi bundles and COTS libraries
- The `edexOsgi/build.edex/build.xml` explicitly calls `org.eclipse.equinox.launcher_*.jar`

###  build steps:

```bash
cd /app/project/edexOsgi/build.edex
ant -f build.xml \
    -Duframe.eclipse=/awips2/eclipse \
    -Duframe.target=/awips2/eclipse
```


## Test Steps

```bash
export AWIPS2_BASELINE=/path/to/fully/built/awips2
cd /app/project/tests
ant -f build.xml -DAWIPS2_BASELINE=${AWIPS2_BASELINE} run-tests
```

## Unexpected Issues

- **This project is effectively unbuildable in a standalone Docker container.**
- Requires Eclipse PDE installation, hundreds of pre-compiled OSGi bundles, and COTS libraries.
- Test classpath requires all `com.raytheon.*` modules pre-compiled plus COTS jars.
- Deploy tests additionally require a running EDEX server with PostgreSQL.
- **Recommended approach:** Use pre-built RPM packages from https://www.unidata.ucar.edu/software/awips/ instead of building from source.
- The repository contains 200+ OSGi plugins — the full build takes hours even with proper infrastructure.
