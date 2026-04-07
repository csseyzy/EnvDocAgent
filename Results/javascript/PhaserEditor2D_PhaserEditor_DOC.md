# PhaserEditor Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: OpenJDK 11
- Build tool: Maven with Eclipse Tycho 1.6.0

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 openjdk-11-jdk maven=3.8.7-2 build-essential=12.10ubuntu1 \
    libgtk-3-0 libxss1 libasound2 libgbm1 xvfb=2:21.1.12-1ubuntu1
```

## Build Steps


- Comment out or remove the `chromium-swt` and `chromium-cef` `<repository>` blocks (lines 56-66) in `releng/configuration/pom.xml`
- Exclude chromium-dependent modules from `phasereditor/pom.xml` module list


```bash
cd /app/PhaserEditor
mvn clean install -pl phasereditor/phasereditor.inspect.core,phasereditor/phasereditor.assetpack.core,phasereditor/phasereditor.inspect.core.tests -am
```

## Test Steps

The test module `phasereditor.inspect.core.tests` contains a JUnit test (`IPhaserFullnames_Test`):

```bash
mvn test -pl phasereditor/phasereditor.inspect.core.tests
```

## Unexpected Issues

- **Build is fundamentally broken for CI/CD**: The project was designed to build on the developer's machine with local mirrors at `http://localhost/repo-mirror/chromium-*`
- The alternative domain `dl.maketechnology.io` is permanently offline (`UnknownHostException`)
- Eclipse Tycho validates ALL P2 repositories before compiling any module - the entire build is blocked by dead repos
- The test module doesn't depend on chromium but can't compile because the reactor build fails atomically
- This is v2 (archived) - the active version is `PhaserEditor2D/PhaserEditor2D-v3`
- Even with chromium repos removed, Tycho may still require a full Eclipse target platform
