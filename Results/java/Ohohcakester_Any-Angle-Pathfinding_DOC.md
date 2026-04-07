# Any-Angle-Pathfinding Deployment Document

## Platform

- **Base Image:** `eclipse-temurin:8u422-b05-jdk-focal`

## Prerequisites

```bash
apt-get update && apt-get install -y ant=1.10.12-1
```

## Build Steps

Create `src/main/CLIRunner.java` for headless execution (the default main class opens a Swing GUI):

```java
package main;
public class CLIRunner {
    public static void main(String[] args) {
        AlgoTest.runWithArgs(args);
    }
}
```

### Step 1: Build

```bash
cd /app/project
ant clean dist
```

## Test Steps



```bash
cd /app/project
java -Xmx512m -cp dist/AAP.jar main.CLIRunner dummy BasicThetaStar mazemaps runningTimeOnly fast_test
```

## Unexpected Issues

- **Large mazes timeout:** The `mazemaps` set includes 2000x2000+ grids that take >10 minutes per test. Use `runningTimeOnly` test type.
- **No JUnit:** This project uses a custom benchmark harness. "Tests" are algorithm benchmarks producing CSV output files in `testResults_<postfix>/`.
- **GUI dependency:** Default `main.AnyAnglePathfinding` opens a Swing GUI — must use custom `CLIRunner` for headless Docker.
- **Argument indexing quirk:** `AlgoTest.runWithArgs()` reads algorithm from `args[1]` (not `args[0]`), so a dummy first argument is required.
- Large grid tests need `-Xmx1024m` or more.
