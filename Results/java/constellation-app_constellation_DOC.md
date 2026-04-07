# constellation Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** Azul Zulu JDK 21.0.2 with JavaFX (`zulu21.32.17-ca-fx-jdk21.0.2-linux_x64.tar.gz`) — standard OpenJDK lacks JavaFX

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    unzip=6.0-28ubuntu4 \
    wget=1.21.4-1ubuntu4 \
    python3=3.12.3-0ubuntu2 \
    libx11-dev=2:1.8.7-1build1 \
    fontconfig=2.15.0-1.1ubuntu2 \
    fonts-dejavu=2.37-8 \
    libpangoft2-1.0-0=1.52.1+ds-1build1 \
    ca-certificates=20240203
```

### Install Azul Zulu JDK 21 with JavaFX

```bash
wget -q https://cdn.azul.com/zulu/bin/zulu21.32.17-ca-fx-jdk21.0.2-linux_x64.tar.gz -O /tmp/zulu.tar.gz
tar xzf /tmp/zulu.tar.gz -C /opt/
export JAVA_HOME=/opt/zulu21.32.17-ca-fx-jdk21.0.2-linux_x64
export PATH=$JAVA_HOME/bin:$PATH
```

### Install Apache NetBeans 21

```bash
wget -q https://archive.apache.org/dist/netbeans/netbeans/21/netbeans-21-bin.zip -O /tmp/netbeans.zip
unzip -q /tmp/netbeans.zip -d /opt/
export NETBEANS_HOME=/opt/netbeans
```

### Install JaCoCo 0.8.11

```bash
wget -q https://github.com/jacoco/jacoco/releases/download/v0.8.11/jacoco-0.8.11.zip -O /tmp/jacoco.zip
unzip -q /tmp/jacoco.zip -d /opt/jacoco
export JACOCO_HOME=/opt/jacoco
```

## Build Steps



```bash
cd /app/project
ant \
    -Dnbplatform.active.dir="${NETBEANS_HOME}" \
    -Dnbplatform.default.netbeans.dest.dir="${NETBEANS_HOME}" \
    -Dnbplatform.default.harness.dir="${NETBEANS_HOME}"/harness \
    -Dupdate.dependencies=true \
    -Dbuild.compiler.debug=true update-dependencies-clean-build
```

## Test Steps


The project provides its own test script:

```bash
./.githubutilities/run-tests.sh -v -verbose
```

Or run the test phase directly:

```bash
ant \
    -verbose \
    -Dnbplatform.active.dir="${NETBEANS_HOME}" \
    -Dnbplatform.default.netbeans.dest.dir="${NETBEANS_HOME}" \
    -Dnbplatform.default.harness.dir="${NETBEANS_HOME}"/harness \
    -Dtest.run.args="-javaagent:${JACOCO_HOME}/lib/jacocoagent.jar \
        --add-opens=java.base/java.net=ALL-UNNAMED \
        --add-opens=javafx.graphics/com.sun.glass.ui=ALL-UNNAMED \
        --add-exports=javafx.graphics/com.sun.javafx.util=ALL-UNNAMED \
        --add-exports=javafx.base/com.sun.javafx.event=ALL-UNNAMED \
        -Djava.awt.headless=true -Dtestfx.robot=glass -Dtestfx.headless=true \
        -Dprism.order=sw -Dprism.text=t2k" test
```


## Unexpected Issues

- Extremely long build+test cycle (45 NetBeans modules, 830+ TestNG test files).
- Requires Azul Zulu JDK with bundled JavaFX (standard OpenJDK lacks JavaFX).
- Requires NetBeans harness for module suite build and test discovery.
- Some tests use TestFX for JavaFX UI testing, requiring headless glass robot configuration.
- Ivy dependency download during first build can take 20+ minutes.
