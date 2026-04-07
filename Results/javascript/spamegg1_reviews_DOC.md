# reviews Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- JDK: OpenJDK 17
- Build tool: SBT (Scala Build Tool)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 wget=1.21.4-1ubuntu4 gnupg=2.4.4-2ubuntu17 apt-transport-https
apt-get update && apt-get install -y --no-install-recommends openjdk-17-jdk=17.0.18+8-1~24.04.1
```

## Build Steps

```bash
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | tee /etc/apt/sources.list.d/sbt.list
echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | tee /etc/apt/sources.list.d/sbt_old.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | apt-key add
apt-get update && apt-get install -y sbt
```

## Test Steps

Run `sbt test` independently in each assignment subdirectory:

```bash
cd /app/project/courses/progfun1/w1/example && sbt test
cd /app/project/courses/progfun1/w1/recfun && sbt test
cd /app/project/courses/progfun1/w2/funsets && sbt test
cd /app/project/courses/progfun1/w3/objsets && sbt test
cd /app/project/courses/progfun1/w4/patmat && sbt test
cd /app/project/courses/progfun1/w6/forcomp && sbt test
cd /app/project/courses/progfun2/w1/quickCheck && sbt test
cd /app/project/courses/progfun2/w2/streams && sbt test
```

## Unexpected Issues

- This is a Scala project, not a JavaScript project — uses SBT + Scala 3.4.2 + Java 17
- The first `sbt test` run downloads a large number of dependencies and takes significant time
- `apt-key add` is deprecated on newer Ubuntu versions; warnings may appear but do not affect functionality
- The repository has a multi-course structure with an independent `build.sbt` in each assignment subdirectory
