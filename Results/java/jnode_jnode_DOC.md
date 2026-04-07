# jnode Deployment Document

## Platform

- **Base Image:** `ubuntu:22.04`
- **JDK:** OpenJDK 8 (`openjdk-8-jdk` = 8u422-b05-1~22.04)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.34.1-1ubuntu1 \
    openjdk-8-jdk=8u422-b05-1~22.04 \
    ant=1.10.12-1 \
    ant-optional=1.10.12-1 \
    wget=1.21.2-2ubuntu1 \
    curl=7.81.0-1ubuntu1 \
    bzip2=1.0.8-5build1 \
    ca-certificates=20230311ubuntu0.22.04.1
```

## Build Steps

### Step 1: Download required classlib artifacts

```bash
cd /app/project
wget -O all/lib/classlib.pack.gz "http://jnode.ro/classlib/20160111104759/classlib.pack.gz"
wget -O all/lib/classlib-src.jar.bz2 "http://jnode.ro/classlib/20160111104759/classlib-src.jar.bz2"
unpack200 all/lib/classlib.pack.gz all/lib/classlib.jar
bunzip2 all/lib/classlib-src.jar.bz2
```

### Step 2: Set up ant-contrib

```bash
cp core/lib/ant-contrib-1.0b3.jar /usr/share/ant/lib/
```

### Step 3: Build

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
cd /app/project/all
ant -f build.xml cd-x86-lite
```

## Test Steps


```bash
cd /app/project/all
ant -f build.xml tests
```

## Unexpected Issues

- **CRITICAL:** The project depends on external classlib artifacts from `jnode.ro` which is currently unreachable. Without these, the project **cannot be built**.
- This is an OS project — many tests require a JNode VM runtime and cannot run on a standard JVM.
- The `ant-contrib` JAR must be on Ant's classpath.
- Build requires significant memory (`-Xmx1512m` on amd64).
- **Recommendation:** Mark this project as potentially unbuildable in Docker due to unreachable external dependency.
