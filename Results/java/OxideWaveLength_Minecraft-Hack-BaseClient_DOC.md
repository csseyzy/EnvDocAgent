# Minecraft-Hack-BaseClient Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Java: OpenJDK 17 (`openjdk-17-jdk`). README says Java 8 but the compilable subset works on Java 17.
- This is a raw MCP (Minecraft Coders Pack) source tree. Only a small subset (Slick XML utilities) can be compiled standalone in a headless container. The full project depends on LWJGL, Minecraft client libraries, and native/graphics dependencies.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1
```


## Build Steps


Test data files are not included in the repository but are required at runtime. Must create:

```bash
mkdir -p /app/project/testdata
```

Create `testdata/test.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testRoot>
  <simple>Hello world</simple>
  <parent>
    <child>
      <grand name="bob" age="1" />
      <another />
    </child>
    <child />
  </parent>
  <other x="5.3" y="5.4" />
</testRoot>
```

Create `testdata/objxmltest.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<GameData>
  <Entity x="10" y="20">
    <Inventory>
      <Item name="Sword" condition="80" />
      <Bag name="Pouch" condition="100">
        <Item name="Potion" condition="100" />
      </Bag>
    </Inventory>
    <Stats hp="100" mp="50" age="25.5" exp="2000" />
  </Entity>
</GameData>
```


```bash
cd /app/project
mkdir -p out

javac -encoding UTF-8 -d out \
  minecraft/org/newdawn/slick/SlickException.java \
  minecraft/org/newdawn/slick/util/LogSystem.java \
  minecraft/org/newdawn/slick/util/DefaultLogSystem.java \
  minecraft/org/newdawn/slick/util/Log.java \
  minecraft/org/newdawn/slick/util/ResourceLocation.java \
  minecraft/org/newdawn/slick/util/FileSystemLocation.java \
  minecraft/org/newdawn/slick/util/ClasspathLocation.java \
  minecraft/org/newdawn/slick/util/ResourceLoader.java \
  minecraft/org/newdawn/slick/util/xml/SlickXMLException.java \
  minecraft/org/newdawn/slick/util/xml/XMLElementList.java \
  minecraft/org/newdawn/slick/util/xml/XMLElement.java \
  minecraft/org/newdawn/slick/util/xml/XMLParser.java \
  minecraft/org/newdawn/slick/util/xml/ObjectTreeParser.java \
  minecraft/org/newdawn/slick/tests/xml/XMLTest.java

javac -encoding UTF-8 -cp out -d out \
  minecraft/org/newdawn/slick/tests/xml/*.java
```


## Test Steps

Working directory must be `/app/project` for resource loading:

```bash
cd /app/project
java -cp out org.newdawn.slick.tests.xml.XMLTest
java -cp out org.newdawn.slick.tests.xml.ObjectParserTest
```



## Unexpected Issues

- **No build system.** This is a raw MCP source tree. No `pom.xml`, `build.gradle`, or `Makefile` exists.
- **Only a small subset compiles headlessly.** The full project depends on LWJGL, Minecraft client libraries, and native/graphics dependencies not available in a headless container.
- **No formal test framework.** Tests are `main()`-based programs, not JUnit/TestNG.
- **Test data files not in repo.** `testdata/test.xml` and `testdata/objxmltest.xml` must be created manually (reverse-engineered from test source code).
- **Most of the codebase is not testable headlessly.** The majority (Minecraft client, GUI, rendering) requires a graphical environment.
