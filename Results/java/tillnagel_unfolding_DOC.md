# unfolding Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.18+8-1~24.04.1)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1 \
    ant=1.10.14-1 \
    fontconfig=2.15.0-1.1ubuntu2 \
    fonts-dejavu-core=2.37-8 \
    ca-certificates=20240203
```

## Build Steps

### Narrow the batchtest pattern in build.xml


Replace the batchtest fileset in the `junit` target:
```xml
<batchtest todir="${test.report.dir}">
    <fileset dir="${build.dir}">
        <include name="**/JunitDemoTest.class" />
        <include name="**/AbstractShapeMarkerLocationTest.class" />
    </fileset>
</batchtest>
```

## Test Steps

```bash
cd /app/project
export JAVA_TOOL_OPTIONS='-Djava.awt.headless=true -Dfile.encoding=UTF-8'
ant clean compile-test junit
```

## Unexpected Issues

- Only 2 of 33 `*Test*` files are actual JUnit tests; the rest are interactive Processing/PApplet applications.
- The `build.xml` author annotated the junit target with `<!-- NOTE: This is not working yet -->`.
- `haltonfailure="yes"` causes the entire test run to abort on the first PApplet class failure.
- `fork="false"` means all tests run in the Ant JVM, so a headless crash kills everything.
- PApplet-based classes require OpenGL/display context even with `java.awt.headless=true`.
