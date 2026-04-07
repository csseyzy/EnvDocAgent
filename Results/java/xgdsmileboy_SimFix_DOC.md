# SimFix Deployment Document

## Platform

- **Base Image:** `openjdk:7-jdk` (JDK 7 is **required** per README)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.20.1-2+deb10u9 \
    wget=1.20.1-1.1 \
    unzip=6.0-23+deb10u3 \
    subversion=1.10.4-1+deb10u4 \
    perl=5.28.1-6+deb10u1 \
    cpanminus=1.7044-1 \
    curl=7.64.0-4+deb10u8 \
    build-essential=12.6
```

## Build Steps

### Step 1: Install Defects4J

```bash
cd /app
git clone https://github.com/rjust/defects4j.git
cd defects4j
git checkout fee5ddf020d0ce9c793655b74f0ab068153c03ef
cpanm --installdeps .
./init.sh
export DEFECTS4J_HOME=/app/defects4j
export PATH=$DEFECTS4J_HOME/framework/bin:$PATH
```

### Step 2: Unzip fault localization data

```bash
cd /app/project
unzip -o sbfl/data.zip -d sbfl/
```

### Step 3: Compile SimFix

```bash
cd /app/project
mkdir -p bin
find src -name "*.java" > /tmp/src_files.txt
find test -name "*.java" >> /tmp/src_files.txt
javac -source 1.7 -target 1.7 -encoding UTF-8 \
    -cp "lib/com.gzoltar-0.1.1-jar-with-dependencies.jar:lib/commons-io-2.5.jar:lib/dom4j-2.0.0-RC1.jar:lib/json-simple-1.1.1.jar:lib/log4j-1.2.17.jar:lib/org.eclipse.core.contenttype_3.5.0.v20150421-2214.jar:lib/org.eclipse.core.jobs_3.7.0.v20150330-2103.jar:lib/org.eclipse.core.resources_3.10.1.v20150725-1910.jar:lib/org.eclipse.core.runtime_3.11.1.v20150903-1804.jar:lib/org.eclipse.equinox.common_3.7.0.v20150402-1709.jar:lib/org.eclipse.equinox.preferences_3.5.300.v20150408-1437.jar:lib/org.eclipse.jdt.core_3.11.2.v20160128-0629.jar:lib/org.eclipse.osgi_3.10.102.v20160118-1700.jar:lib/org.eclipse.text-3.5.101.jar" \
    -d bin @/tmp/src_files.txt
```

### Step 4: Checkout a buggy project and run SimFix

```bash
mkdir -p /tmp/chart
defects4j checkout -p Chart -v 1b -w /tmp/chart/chart_1_buggy

java -cp "bin:lib/*" cofix.main.Main \
    --proj_home=/tmp \
    --proj_name=chart \
    --bug_id=1
```

## Test Steps

```bash
java -cp "bin:lib/*" org.junit.runner.JUnitCore \
    cofix.core.parser.search.SimpleFilterTest \
    cofix.core.parser.node.CodeBlockTest \
    cofix.core.match.CodeBlockMatcherTest
```

## Unexpected Issues

- **Defects4J repo download URL is dead:** `defects4j-repos.zip` returns 404. Workaround: use a newer Defects4J version from `main` branch which has updated download logic.
- Requires **JDK 7 specifically** — JDK 8+ may cause issues with Eclipse JDT core 3.11.2 and GZoltar 0.1.1.
- SimFix has no traditional build system (no pom.xml, build.gradle, or build.xml) — must compile with `javac`.
- `init.sh` downloads Major 1.3.1, EvoSuite 0.2.0, and Randoop 3.1.0 — these URLs may also become unavailable.
- The `sbfl/data.zip` must be unzipped before running SimFix.
