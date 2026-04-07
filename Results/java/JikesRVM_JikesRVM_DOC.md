# JikesRVM Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 8 (`openjdk-8-jdk` = 8u422-b05-1~24.04)
- **JAVA_HOME:** `/usr/lib/jvm/java-8-openjdk-amd64`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-8-jdk=8u422-b05-1~24.04 \
    gcc=4:13.2.0-7ubuntu1 \
    g++=4:13.2.0-7ubuntu1 \
    make=4.3-4.1build2 \
    gcc-multilib=4:13.2.0-7ubuntu1 \
    g++-multilib=4:13.2.0-7ubuntu1 \
    bison=2:3.8.2+dfsg-1build2 \
    perl=5.38.2-3.2build2 \
    gawk=1:5.2.1-2build3 \
    libproc-processtable-perl=0.636-1build3 \
    wget=1.21.4-1ubuntu4 \
    unzip=6.0-28ubuntu4 \
    lib32z1=1:1.3.dfsg-3.1ubuntu2 \
    lib32stdc++6=14-20240412-0ubuntu1 \
    autoconf=2.71-3 \
    automake=1:1.16.5-1.3ubuntu1 \
    libtool=2.4.7-7build1 \
    libtool-bin=2.4.7-7build1 \
    gettext=0.21-14ubuntu2 \
    pkg-config=1.8.1-2build1 \
    ca-certificates=20240203
```


```bash
cd /opt
wget -q https://archive.apache.org/dist/ant/binaries/apache-ant-1.9.16-bin.zip
unzip -q apache-ant-1.9.16-bin.zip
rm apache-ant-1.9.16-bin.zip
export ANT_HOME=/opt/apache-ant-1.9.16
export PATH=$ANT_HOME/bin:$PATH
```

## Build Steps

### Step 1: Create `.ant.properties`

```bash
cd /app/project
cat > .ant.properties << 'EOF'
host.name=x86_64_m32-linux
config.name=BaseBaseSemiSpace
EOF
```

This selects the 32-bit x86_64 Linux host configuration and the BaseBaseSemiSpace garbage collector configuration.

### Step 2: Validate properties and build GNU Classpath

```bash
ant check-properties
```

Downloads `classpath-0.99.tar.gz`, patches it, and runs autoconf/configure/make. Requires network access.

### Step 3: Build and run unit tests

```bash
ant -Dconfig.name=BaseBaseSemiSpace rvm-unit-tests
```

This builds the bootimage, compiles JikesRVM, and runs JUnit tests. 49 test classes executed.

### Alternative: Run tests on existing image

```bash
ant -Dconfig.name=BaseBaseSemiSpace unit-tests-on-existing-image
```


## Test Steps

```bash
ant -Dconfig.name=BaseBaseSemiSpace bootstrap-unit-tests
```

## Unexpected Issues

- Must use Ant 1.9.x. Ant 1.10+ produces class files at version 52 (Java 8) which JikesRVM cannot load (only supports up to version 50/Java 6).
- JikesRVM only supports 32-bit mode on x86_64; requires `gcc-multilib`, `g++-multilib`, `lib32z1`, `lib32stdc++6`.
- First build requires internet access to download `classpath-0.99.tar.gz` from `ftp://ftp.gnu.org/gnu/classpath/`.
- The `.ant.properties` file must be created before any `ant` target can run. The `host.name` must match a file in `build/hosts/`.
- The `rvm-unit-tests` target does not produce XML test report files; test results are only available in console output.
- Many tests are conditionally skipped based on annotations like `@RequiresBuiltJikesRVM`, `@RequiresBootstrapVM`, `@RequiresIA32`.
