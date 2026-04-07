# jcef Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.11+9-1)
- **JAVA_HOME:** `/usr/lib/jvm/java-17-openjdk-amd64`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    build-essential=12.10ubuntu1 \
    cmake=3.28.3-1build7 \
    ninja-build=1.11.1-2 \
    pkg-config=1.8.1-2build1 \
    ant=1.10.14-1 \
    python3=3.12.3-0ubuntu2 \
    python3-pip=24.0+dfsg-1ubuntu1 \
    flex=2.6.4-8.2build1 \
    bison=2:3.8.2+dfsg-1build2 \
    openjdk-17-jdk=17.0.11+9-1 \
    libgtk-3-dev=3.24.41-4ubuntu1 \
    libcairo2-dev=1.18.0-3build1 \
    libpango1.0-dev=1.52.1+ds-1build1 \
    libasound2-dev=1.2.11-1build2 \
    libcups2-dev=2.4.7-1.2ubuntu7 \
    libx11-dev=2:1.8.7-1build1 \
    libxcomposite-dev=1:0.4.6-1build3 \
    libxdamage-dev=1:1.1.6-1build1 \
    libxrandr-dev=2:1.5.4-1build1 \
    libdrm-dev=2.4.120-2build1 \
    libxkbcommon-dev=1.6.0-1build1 \
    libgbm-dev=24.0.5-1ubuntu1 \
    libnss3=2:3.98-1build1 \
    dbus=1.14.10-4ubuntu4 \
    xvfb=2:21.1.12-1ubuntu1 \
    curl=8.5.0-2ubuntu10.8 wget=1.21.4-1ubuntu4 unzip=6.0-28ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

```bash
cd /opt
wget -q https://services.gradle.org/distributions/gradle-8.6-bin.zip
unzip -q gradle-8.6-bin.zip
rm gradle-8.6-bin.zip
export PATH=/opt/gradle-8.6/bin:$PATH
```

### Step 1: Build native JCEF artifacts

```bash
cd /app/project
JCEF_CLEANUP_VCPKG=1 jb/tools/linux/build.sh all x86_64
```

This downloads CEF binaries and builds vcpkg dependencies. Takes significant time and disk space.

### Step 2: Extract and stage JCEF into JDK

```bash
cd /app/project
mkdir -p jcef_bundle
tar xfz jcef_linux_x64.tar.gz -C jcef_bundle
tar xfz cef_server_linux_x64.tar.gz -C jcef_bundle

JDK_LIB=/usr/lib/jvm/java-17-openjdk-amd64/lib
mkdir -p "$JDK_LIB/locales"
cp -a jcef_bundle/libcef.so jcef_bundle/libEGL.so jcef_bundle/libGLESv2.so \
    jcef_bundle/libvk_swiftshader.so jcef_bundle/libvulkan.so.1 \
    jcef_bundle/libshared_mem_helper.so jcef_bundle/resources.pak \
    jcef_bundle/chrome_100_percent.pak jcef_bundle/chrome_200_percent.pak \
    jcef_bundle/icudtl.dat jcef_bundle/v8_context_snapshot.bin \
    jcef_bundle/vk_swiftshader_icd.json jcef_bundle/cef_server \
    jcef_bundle/chrome-sandbox "$JDK_LIB/"
cp -a jcef_bundle/locales/* "$JDK_LIB/locales/"
chmod +x "$JDK_LIB/cef_server" "$JDK_LIB/chrome-sandbox"
```



## Test Steps

```bash
mkdir -p /tmp/runtime
cd /app/project/jb/project/java-gradle
ulimit -n 4096
XDG_RUNTIME_DIR=/tmp/runtime xvfb-run -a \
    /opt/gradle-8.6/bin/gradle --no-daemon test \
    -Pjbr_linux=/usr/lib/jvm/java-17-openjdk-amd64
```

## Unexpected Issues

- JCEF native artifacts must be built first via `jb/tools/linux/build.sh`, then staged into the JDK's `lib/` directory before tests can pass.
- Xvfb is required for headless GUI testing (CEF uses windowless rendering).
- `XDG_RUNTIME_DIR` must be set to avoid DBus socket warnings.
- File descriptor limit (`ulimit -n 4096`) should be raised for CEF stability.
- `KeyboardOSRTest.initializationError` fails in headless container environment.
- SwingComponentsTest and SelfSignedSSLTest are intentionally skipped.
