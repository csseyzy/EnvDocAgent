# scipio-erp Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.18+8-1~24.04)
- **JAVA_HOME:** `/usr/lib/jvm/java-17-openjdk-amd64`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-17-jdk=17.0.18+8-1~24.04 \
    ant=1.10.14-1 \
    wget=1.21.4-1ubuntu4 \
    unzip=6.0-28ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

### : Build and load demo data

```bash
cd /app/project
./ant load-demo
```




## Test Steps

### Step 1: Run tests

```bash
cd /app/project
./ant run-test-suite -Dtest.component=base -Dtest.suiteName=basetests
```


### Step 2: View test results

```bash
cat /app/project/runtime/logs/test-results/TESTS-TestSuites.xml
```

### Alternative: Run full test suite

```bash
./ant run-tests
```

## Unexpected Issues

- `install.sh` is interactive — use `./ant load-demo` directly for automation.
- The `./ant` wrapper in project root is NOT system ant. It locates the bundled `ant-launcher.jar` under `framework/base/lib/ant/` and auto-downloads Nashorn JS engine for JDK 15+.
- Use `-Dtest.suiteName` (NOT `-Dtest.suite`) for the `run-test-suite` target.
- 2 known test errors in `UtilPropertiesTests` (NullPointerException in XML property parsing) — pre-existing upstream issue.
- Ant reports `BUILD FAILED` with `Java Result: 99` when any test errors occur, even though 107/109 tests pass. This is expected behavior.
- Tomcat connectors configured on ports 8010 (AJP), 8080 (HTTP), 8443 (HTTPS) during test execution.
